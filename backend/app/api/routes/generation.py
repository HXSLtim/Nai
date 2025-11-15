"""
内容生成路由
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.schemas import (
    GenerationRequest,
    GenerationResponse,
    InitNovelRequest,
    InitNovelResponse,
    PlotOptionsRequest,
    PlotOptionsResponse,
    PlotOption,
    AutoChapterRequest,
    ChapterCreate,
    ChapterResponse,
    RewriteRequest,
    RewriteResponse,
)
from app.services.agent_service import agent_service
from app.services.rag_service import rag_service
from app.db.base import get_db
from app.crud import novel as novel_crud
from app.api.routes.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
import json
import asyncio

router = APIRouter()


# 初始化设定使用的LLM
init_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL_COMPLEX,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE,
    temperature=0.8,
)


class ContinueRequest(BaseModel):
    """章节续写请求"""
    novel_id: int
    chapter_id: int
    current_content: str
    target_length: int = 500
    # 用户可控参数
    style_strength: float = 0.7  # 文风强度 (0-1)
    pace: str = "medium"  # 节奏：slow/medium/fast
    tone: str = "neutral"  # 基调：neutral/tense/relaxed/sad/joyful
    use_rag_style: bool = True  # 是否使用RAG学习文风
    style_sample_id: int | None = None  # 文风样本ID（用户上传的参考文风）
    plot_direction_hint: str | None = None  # 选定的剧情走向提示，用于引导续写方向


class OutlineRequest(BaseModel):
    """大纲生成请求"""
    novel_id: int
    theme: str
    target_chapters: int = 10


class CharacterRequest(BaseModel):
    """角色生成请求"""
    novel_id: int
    character_type: str  # 主角/配角/反派
    character_description: str


@router.post("/init", response_model=InitNovelResponse)
async def init_novel(
    request: InitNovelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 初始化小说设定

    根据小说的标题、类型和用户提供的主题，自动生成世界观、主要角色、大纲和剧情线索。
    """
    try:
        logger.info(
            "生成剧情选项请求：novel_id=%s, chapter_id=%s, num_options=%s",
            request.novel_id,
            request.chapter_id,
            request.num_options,
        )
        # 校验小说归属
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")

        # 构造提示词（注意：示例JSON中的花括号需要用双花括号转义，避免被当作模板变量）
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是一名专业的中文网络小说策划编辑，擅长根据简单的想法，生成完整的设定与大纲。

请你根据用户提供的信息，为这部小说生成：
- 世界观设定（worldview）：整体世界结构、力量体系、时代背景等，使用多段文字描述；
- 主要角色列表（main_characters）：3-6个主要角色，每个用一句话概括；
- 故事大纲（outline）：从开篇到结局的主线设计，可以按段落分点描述；
- 剧情线索（plot_hooks）：3-8条可以展开的重要伏笔或矛盾。

输出时请严格使用JSON格式（注意：下面是结构示例，不是内容）：
{{
  "worldview": "...",
  "main_characters": ["角色1：...", "角色2：..."],
  "outline": "...",
  "plot_hooks": ["线索1", "线索2", "线索3"]
}}

不要输出任何解释性文字、注释或前后缀，只输出上述JSON。""",
                ),
                (
                    "user",
                    """小说标题：{title}
小说类型：{genre}
已有简介：{description}
目标章节数：{target_chapters}
故事主题/补充说明：{theme}
""",
                ),
            ]
        )

        chain = prompt | init_llm
        result = await chain.ainvoke(
            {
                "title": novel.title,
                "genre": novel.genre or "未指定",
                "description": novel.description or "暂无简介",
                "target_chapters": request.target_chapters,
                "theme": request.theme or "",
            }
        )

        raw = result.content.strip()

        try:
            # 尝试从返回内容中提取JSON片段
            start = raw.find("{")
            end = raw.rfind("}") + 1
            json_str = raw[start:end] if start != -1 and end != 0 else raw
            data = json.loads(json_str)
        except Exception as e:  # noqa: BLE001
            logger.error(f"解析初始化设定JSON失败: {e}")
            raise HTTPException(status_code=500, detail="AI返回格式异常，初始化设定失败")

        worldview = str(data.get("worldview") or "").strip()
        main_chars_raw = data.get("main_characters") or data.get("characters") or []
        outline = str(data.get("outline") or "").strip()
        plot_hooks_raw = data.get("plot_hooks") or []

        # 规范化 main_characters
        if isinstance(main_chars_raw, str):
            main_characters = [line.strip() for line in main_chars_raw.split("\n") if line.strip()]
        elif isinstance(main_chars_raw, list):
            main_characters = [str(item).strip() for item in main_chars_raw if str(item).strip()]
        else:
            main_characters = []

        # 规范化 plot_hooks
        if isinstance(plot_hooks_raw, str):
            plot_hooks = [line.strip() for line in plot_hooks_raw.split("\n") if line.strip()]
        elif isinstance(plot_hooks_raw, list):
            plot_hooks = [str(item).strip() for item in plot_hooks_raw if str(item).strip()]
        else:
            plot_hooks = []

        return InitNovelResponse(
            novel_id=request.novel_id,
            worldview=worldview,
            main_characters=main_characters,
            outline=outline,
            plot_hooks=plot_hooks,
        )

    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"AI初始化小说设定失败: {e}")
        raise HTTPException(status_code=500, detail=f"初始化设定失败: {str(e)}")


@router.post("/generate", response_model=GenerationResponse)
async def generate_content(request: GenerationRequest):
    """
    生成小说内容

    使用三Agent协作工作流生成高质量小说段落：
    - Agent A：世界观描写
    - Agent B：角色对话
    - Agent C：剧情控制

    Args:
        request: 生成请求

    Returns:
        生成响应（包含最终内容和各Agent输出）

    Raises:
        HTTPException: 生成失败时抛出
    """
    try:
        logger.info(f"收到生成请求：小说{request.novel_id}，提示词:'{request.prompt}'")
        response = await agent_service.generate_content(request)
        return response
    except Exception as e:
        logger.error(f"生成失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"生成失败: {str(e)}"
        )


@router.post("/plot-options", response_model=PlotOptionsResponse)
async def generate_plot_options(
    request: PlotOptionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """生成剧情走向选项

    用于在续写前给用户提供多个可选的剧情发展方向，由AI给出结构化描述。
    """
    try:
        # 验证小说所有权
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")

        # 验证章节归属
        chapter = novel_crud.get_chapter_by_id(db, request.chapter_id)
        if not chapter or chapter.novel_id != request.novel_id:
            raise HTTPException(status_code=404, detail="章节不存在")

        # 构造提示词
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """你是一名专业的小说剧情策划编辑。

你的任务是根据小说的设定、当前章节内容和整体节奏，设计多个合理的下一步剧情走向选项。

要求：
1. 不要直接给出续写正文，只输出剧情走向的结构化描述。
2. 每个选项需要包含：title（简短标题）、summary（具体会发生什么）、impact（对节奏/情绪/伏笔的影响，简要），risk（潜在风险，可选）。
3. 输出必须是JSON格式：{{"options": [{{"title": "...", "summary": "...", "impact": "...", "risk": "..."}}, ...]}}。
4. 不要添加任何额外说明或前后缀，只输出JSON。
""",
            ),
            (
                "user",
                """请基于以下信息给出{num_options}个下一步剧情走向选项：

小说标题：{title}
小说类型：{genre}
世界观（节选）：{worldview}
故事简介：{description}

当前章节标题：{chapter_title}
当前章节内容（节选）：{chapter_excerpt}

当前写作内容（用于判断下一步剧情）：{current_excerpt}
""",
            ),
        ])

        # 构造章节与当前内容节选，避免提示过长
        chapter_excerpt = chapter.content[-500:] if len(chapter.content) > 500 else chapter.content
        current_excerpt = (
            request.current_content[-800:]
            if len(request.current_content) > 800
            else request.current_content
        )
        worldview_excerpt = (
            novel.worldview[:500] + "..." if novel.worldview and len(novel.worldview) > 500 else (novel.worldview or "未设定")
        )

        chain = prompt | init_llm
        response = await chain.ainvoke(
            {
                "num_options": request.num_options,
                "title": novel.title,
                "genre": novel.genre or "未指定",
                "worldview": worldview_excerpt,
                "description": novel.description or "暂无简介",
                "chapter_title": chapter.title,
                "chapter_excerpt": chapter_excerpt or "暂无内容",
                "current_excerpt": current_excerpt or "",
            }
        )

        raw = response.content.strip()

        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            json_str = raw[start:end] if start != -1 and end != 0 else raw
            data = json.loads(json_str)
            options_raw = data.get("options", [])
        except Exception as e:  # noqa: BLE001
            logger.warning(f"解析剧情选项JSON失败，将原始内容作为单个选项返回: {e}")
            options_raw = [
                {
                    "title": "默认剧情走向",
                    "summary": raw,
                    "impact": "",
                    "risk": "",
                }
            ]

        options: list[PlotOption] = []
        for idx, item in enumerate(options_raw[: request.num_options], start=1):
            title = str(item.get("title") or f"剧情选项{idx}")
            summary = str(item.get("summary") or "")
            impact = item.get("impact")
            risk = item.get("risk")

            options.append(
                PlotOption(
                    id=idx,
                    title=title,
                    summary=summary,
                    impact=str(impact) if impact is not None else None,
                    risk=str(risk) if risk is not None else None,
                )
            )

        response = PlotOptionsResponse(
            novel_id=request.novel_id,
            chapter_id=request.chapter_id,
            options=options,
        )
        logger.info(
            "生成剧情选项完成：novel_id=%s, chapter_id=%s, 实际返回选项数=%s",
            response.novel_id,
            response.chapter_id,
            len(response.options),
        )
        return response

    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"生成剧情选项失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成剧情选项失败: {str(e)}")


@router.post("/auto-chapter", response_model=ChapterResponse)
async def auto_create_chapter(
    request: AutoChapterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI自动生成并创建新章节

    根据小说设定和参考章节，自动生成下一章的章节号、标题和正文，并写入数据库。
    """
    try:
        # 验证小说所有权
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")

        # 确定参考章节
        base_chapter = None
        if request.base_chapter_id is not None:
            base_chapter = novel_crud.get_chapter_by_id(db, request.base_chapter_id)
            if not base_chapter or base_chapter.novel_id != request.novel_id:
                raise HTTPException(status_code=404, detail="参考章节不存在")
        else:
            # 使用最后一章作为参考
            chapters = novel_crud.get_chapters_by_novel(db, request.novel_id)
            if chapters:
                base_chapter = chapters[-1]

        # 计算下一章章节号
        if base_chapter:
            next_chapter_number = base_chapter.chapter_number + 1
            base_content = base_chapter.content or ""
        else:
            next_chapter_number = 1
            base_content = ""

        # 构造提示词
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """你是一名专业的长篇小说写作助手，负责为作者自动生成新章节。

你的任务：
1. 根据小说设定和参考内容，设计下一章的章节标题和完整正文初稿。
2. 章节标题要简洁、有记忆点，并且符合该章的核心冲突或事件。
3. 正文需要在指定字数范围内（可略有浮动），保持与前文一致的人设和世界观。
4. 输出必须使用JSON格式：{{"title": "章节标题", "content": "章节正文"}}，不要添加其他内容。
""",
            ),
            (
                "user",
                """小说标题：{title}
小说类型：{genre}
世界观（节选）：{worldview}
故事简介：{description}

参考章节号：{base_chapter_number}
参考章节标题：{base_chapter_title}
参考章节内容（节选）：{base_excerpt}

本章剧情重点：{theme}
目标章节号：{target_chapter_number}
目标字数：约{target_length}字
""",
            ),
        ])

        base_excerpt = base_content[-800:] if len(base_content) > 800 else base_content
        worldview_excerpt = (
            novel.worldview[:500] + "..." if novel.worldview and len(novel.worldview) > 500 else (novel.worldview or "未设定")
        )

        chain = prompt | init_llm
        response = await chain.ainvoke(
            {
                "title": novel.title,
                "genre": novel.genre or "未指定",
                "worldview": worldview_excerpt,
                "description": novel.description or "暂无简介",
                "base_chapter_number": base_chapter.chapter_number if base_chapter else "无",
                "base_chapter_title": base_chapter.title if base_chapter else "无",
                "base_excerpt": base_excerpt or "暂无内容",
                "theme": request.theme or "无特别说明",
                "target_chapter_number": next_chapter_number,
                "target_length": request.target_length,
            }
        )

        raw = response.content.strip()
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            json_str = raw[start:end] if start != -1 and end != 0 else raw
            data = json.loads(json_str)
            title = str(data.get("title") or f"第{next_chapter_number}章")
            content = str(data.get("content") or "")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"解析自动章节JSON失败，将原始内容作为正文返回: {e}")
            title = f"第{next_chapter_number}章"
            content = raw

        chapter_create = ChapterCreate(
            chapter_number=next_chapter_number,
            title=title,
            content=content,
        )

        # 创建章节
        db_chapter = novel_crud.create_chapter(db, request.novel_id, chapter_create)

        # 将章节内容索引到RAG（忽略失败）
        try:
            await rag_service.index_content(
                novel_id=request.novel_id,
                chapter=db_chapter.chapter_number,
                content=db_chapter.content,
                metadata={"source": "chapter", "chapter_id": db_chapter.id},
            )
            logger.info(
                f"AI自动创建章节已索引到RAG：小说{request.novel_id}，章节{db_chapter.chapter_number}"
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"AI自动章节索引到RAG失败（novel_id={request.novel_id}, chapter={db_chapter.chapter_number}）: {e}"
            )

        return ChapterResponse.model_validate(db_chapter)

    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"AI自动生成章节失败: {e}")
        raise HTTPException(status_code=500, detail=f"自动生成章节失败: {str(e)}")


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(
    request: RewriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """局部文本改写

    根据用户选择的改写类型，对一小段文本进行润色/重写/压缩/扩写。
    """
    try:
        # 权限校验：至少校验小说归属
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")

        if not request.original_text.strip():
            raise HTTPException(status_code=400, detail="原文不能为空")

        if request.chapter_id is not None:
            chapter = novel_crud.get_chapter_by_id(db, request.chapter_id)
            if not chapter or chapter.novel_id != request.novel_id:
                raise HTTPException(status_code=404, detail="章节不存在")

        # 改写类型说明
        type_map = {
            "polish": "在保持原始含义和大致长度不变的前提下，对文本进行润色，使其更流畅、生动、自然。",
            "rewrite": "在保持总体情节和信息不变的前提下，重新表述文本，可以调整句式和部分细节。",
            "shorten": "在保持关键信息和情感不变的前提下，将文本压缩得更加简洁短小。",
            "extend": "在保持原意的前提下，对文本进行扩写，补充分镜、环境或心理描写。",
        }
        rewrite_type = request.rewrite_type or "polish"
        type_desc = type_map.get(rewrite_type, type_map["polish"])

        style_hint = (request.style_hint or "").strip()
        style_part = f"\n风格提示：{style_hint}" if style_hint else ""

        length_part = ""
        if request.target_length is not None:
            length_part = f"\n目标字数：约{request.target_length}字（允许少量上下浮动）"

        user_prompt = f"""请根据以下要求改写这段中文文本：

改写类型：{type_desc}{style_part}{length_part}

【原文】
{request.original_text}

【输出要求】
1. 仅输出改写后的文本本身，不要解释原因，也不要添加额外的说明或前后缀。
2. 保持人物称呼、世界观名词等专有名词不变，避免引入与原文设定冲突的新设定。
"""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是一名中文小说写作助手，擅长在保持含义和设定一致的前提下，对局部文本进行高质量改写。请严格按照用户要求进行改写，并且只输出改写后的文本本身。""",
                ),
                ("user", "{user_request}"),
            ]
        )

        chain = prompt | init_llm
        result = await chain.ainvoke({"user_request": user_prompt})
        rewritten = result.content.strip()

        if not rewritten:
            raise HTTPException(status_code=500, detail="改写失败，模型返回为空")

        return RewriteResponse(rewritten_text=rewritten)

    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"局部改写失败: {e}")
        raise HTTPException(status_code=500, detail=f"改写失败: {str(e)}")


@router.post("/continue")
async def continue_chapter(
    request: ContinueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    章节续写：根据已有内容继续创作

    Args:
        request: 续写请求（包含当前内容和目标长度）
        current_user: 当前用户
        db: 数据库会话

    Returns:
        续写的内容
    """
    try:
        logger.info(
            "章节续写请求：novel_id=%s, chapter_id=%s, target_length=%s, pace=%s, tone=%s, plot_direction_hint=%s",
            request.novel_id,
            request.chapter_id,
            request.target_length,
            request.pace,
            request.tone,
            (request.plot_direction_hint or ""),
        )

        # 验证小说所有权
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")

        # 获取当前章节信息，确保章节属于该小说
        chapter = novel_crud.get_chapter_by_id(db, request.chapter_id)
        if not chapter or chapter.novel_id != request.novel_id:
            raise HTTPException(status_code=404, detail="章节不存在或不属于该小说")

        # 文风特征与上下文
        style_features: list[str] = []
        style_guide = ""
        style_sample_id = request.style_sample_id
        rag_style_context: list[str] = []

        # 优先使用用户上传的文风样本
        if style_sample_id is not None:
            sample = novel_crud.get_style_sample_by_id(db, style_sample_id)
            if not sample or sample.novel_id != request.novel_id:
                raise HTTPException(status_code=404, detail="文风样本不存在或不属于该小说")

            try:
                style_features = json.loads(sample.style_features) if sample.style_features else []
            except Exception:
                style_features = []

            # 根据文风强度构造指导
            if request.style_strength > 0:
                if style_features:
                    style_guide = "\n\n【文风指导】请尽量参考以下文风特征进行创作：\n" + "\n".join(
                        f"- {feat}" for feat in style_features
                    )

            # 将样本文本的一部分作为风格上下文
            rag_style_context.append(sample.sample_text[:300])

        # 如果没有文风样本但开启了RAG文风分析，则退回到基于当前内容的启发式分析
        elif request.use_rag_style and request.current_content:
            if len(request.current_content) > 100:
                sample_text = (
                    request.current_content[-500:]
                    if len(request.current_content) > 500
                    else request.current_content
                )

                # 统计句子长度和结构
                sentences = (
                    sample_text.replace('。', '。\n')
                    .replace('！', '！\n')
                    .replace('？', '？\n')
                    .split('\n')
                )
                sentences = [s.strip() for s in sentences if s.strip()]

                if sentences:
                    avg_length = sum(len(s) for s in sentences) / len(sentences)

                    if avg_length < 15:
                        style_features.append("使用简短有力的句式")
                    elif avg_length > 30:
                        style_features.append("使用细腻详尽的长句描写")
                    else:
                        style_features.append("使用长短句结合的叙事方式")

                # 检测描写风格
                if '，' in sample_text and sample_text.count('，') > len(sample_text) / 50:
                    style_features.append("善用逗号进行细节铺陈")

                if any(word in sample_text for word in ['只见', '但见', '忽见', '忽听', '忽闻']):
                    style_features.append("采用古典小说的叙事手法")

                if any(word in sample_text for word in ['心中', '心想', '暗道', '暗想']):
                    style_features.append("注重心理描写")

                if request.style_strength > 0.5 and style_features:
                    style_guide = "\n\n【文风指导】请严格保持以下文风特征：\n" + "\n".join(
                        f"- {feat}" for feat in style_features
                    )

        # 构造节奏指导
        pace_guide = {
            "slow": "采用舒缓的节奏，详细描写场景和心理活动，营造沉浸感。",
            "medium": "保持适中的叙事节奏，情节推进与描写平衡。",
            "fast": "采用快节奏叙事，简洁明快，快速推进情节。"
        }.get(request.pace, "")

        # 构造情感基调指导
        tone_guide = {
            "neutral": "",
            "tense": "营造紧张氛围，增强冲突感和悬念。",
            "relaxed": "保持轻松愉快的氛围，注重趣味性。",
            "sad": "渲染悲伤情绪，注重情感共鸣。",
            "joyful": "营造欢快氛围，传递积极向上的情绪。"
        }.get(request.tone, "")

        # 构造剧情走向提示
        plot_direction_hint = (
            request.plot_direction_hint.strip() if isinstance(request.plot_direction_hint, str) else ""
        )
        plot_hint_part = f"\n- 剧情走向：{plot_direction_hint}" if plot_direction_hint else ""

        # 构造完整的续写提示词
        prompt = f"""请根据以下内容继续创作约{request.target_length}字的小说段落。

【小说信息】
标题：{novel.title}
类型：{novel.genre or '未指定'}
世界观：{novel.worldview or '无'}

【已有内容】
{request.current_content[-1000:] if len(request.current_content) > 1000 else request.current_content}

【创作要求】
- 目标字数：约{request.target_length}字
- 叙事节奏：{pace_guide}
- 情感基调：{tone_guide}
{style_guide}{plot_hint_part}

请自然地续写故事，保持情节连贯性和人物一致性。

续写："""

        # 调用生成服务
        gen_request = GenerationRequest(
            novel_id=request.novel_id,
            prompt=prompt,
            chapter=chapter.chapter_number,
            current_day=1,
            target_length=request.target_length,
        )
        response = await agent_service.generate_content(gen_request)

        # 工作流追踪（用于前端可视化多Agent执行过程）
        workflow_trace = (
            response.workflow_trace.model_dump()
            if getattr(response, "workflow_trace", None) is not None
            else None
        )

        logger.info(
            f"章节续写成功：小说{request.novel_id}，章节{chapter.chapter_number}，生成{len(response.final_content)}字，节奏={request.pace}，基调={request.tone}"
        )

        return {
            "content": response.final_content,
            "length": len(response.final_content),
            "style_features": style_features,
            "style_sample_id": style_sample_id,
            "rag_style_context": rag_style_context,
            "rag_story_context": response.worldview_context + response.character_context,
            "agent_outputs": [output.model_dump() for output in response.agent_outputs],
            "workflow_trace": workflow_trace,
            "settings": {
                "pace": request.pace,
                "tone": request.tone,
                "style_strength": request.style_strength
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"章节续写失败: {e}")
        raise HTTPException(status_code=500, detail=f"续写失败: {str(e)}")


@router.post("/continue-stream")
async def continue_chapter_stream(
    request: ContinueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """章节续写流式接口

    使用与 `/generation/continue` 相同的多Agent工作流，但通过SSE将结果按块推送给前端，
    以便工作台实现真正的流式展示效果。
    """

    try:
        # 复用已有的续写逻辑，确保行为与非流式接口保持一致
        logger.info("开始调用 continue_chapter 获取生成结果")
        base_result = await continue_chapter(request, current_user, db)
        logger.info(f"continue_chapter 返回成功，内容长度：{len(base_result.get('content', ''))}")

        # 提取主要字段
        full_content = str(base_result.get("content") or "")
        style_features = base_result.get("style_features") or []
        rag_style_context = base_result.get("rag_style_context") or []
        rag_story_context = base_result.get("rag_story_context") or []
        agent_outputs = base_result.get("agent_outputs") or []
        workflow_trace = base_result.get("workflow_trace")
        settings = base_result.get("settings") or {}
        length = int(base_result.get("length") or len(full_content))

        async def event_generator():
            """SSE事件生成器，按块输出文本和元数据。"""
            try:
                # 如果没有内容，直接发送完成事件
                if not full_content:
                    logger.warning("生成的内容为空")
                    done_payload = {"type": "done"}
                    yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"
                    return

                # 计算块大小，控制在大约 60 个块以内
                total_len = len(full_content)
                chunk_count = 60
                chunk_size = max(50, total_len // chunk_count) if total_len > 0 else 0
                logger.info(f"开始流式发送内容：总长度={total_len}，块大小={chunk_size}，块数={(total_len + chunk_size - 1) // chunk_size}")

                # 按块发送正文内容
                chunk_sent = 0
                for start in range(0, total_len, chunk_size):
                    end = min(start + chunk_size, total_len)
                    chunk = full_content[start:end]
                    if not chunk:
                        continue

                    data = {"type": "chunk", "content": chunk}
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    chunk_sent += 1

                    # 适当让出事件循环，避免阻塞
                    await asyncio.sleep(0)

                logger.info(f"已发送 {chunk_sent} 个内容块")

                # 发送一次性元数据
                metadata = {
                    "style_features": style_features,
                    "rag_style_context": rag_style_context,
                    "rag_story_context": rag_story_context,
                    "agent_outputs": agent_outputs,
                    "workflow_trace": workflow_trace,
                    "settings": settings,
                    "word_count": length,
                }
                meta_payload = {"type": "metadata", "data": metadata}
                # 使用 default=str 处理 datetime 等不可直接序列化的对象
                yield f"data: {json.dumps(meta_payload, ensure_ascii=False, default=str)}\n\n"
                logger.info("已发送元数据")

                # 发送完成事件
                done_payload = {"type": "done"}
                yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"
                logger.info("已发送完成事件")

            except Exception as e:
                logger.error(f"事件生成器异常: {e}", exc_info=True)
                # 尝试发送错误事件
                try:
                    error_payload = {"type": "error", "message": str(e)}
                    yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                except Exception as send_error:
                    logger.error(f"发送错误事件失败: {send_error}")
                raise

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except HTTPException:
        # 直接透传业务错误，前端会在进入流式处理前通过 res.ok 检查
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"章节续写流式接口失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"续写失败: {str(e)}")


@router.post("/outline")
async def generate_outline(
    request: OutlineRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成小说大纲

    Args:
        request: 大纲生成请求（包含主题和章节数）
        current_user: 当前用户
        db: 数据库会话

    Returns:
        生成的大纲（章节列表）
    """
    try:
        # 验证小说所有权
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")

        # 构造大纲生成提示词
        prompt = f"""请为以下小说生成{request.target_chapters}章的详细大纲：

小说标题：{novel.title}
小说类型：{novel.genre or '未指定'}
故事主题：{request.theme}
世界观：{novel.worldview or '未设定'}

请按照以下格式生成大纲：
第X章 章节标题
- 主要情节点1
- 主要情节点2
- 主要情节点3
"""

        # 调用生成服务
        gen_request = GenerationRequest(
            novel_id=request.novel_id,
            prompt=prompt,
            chapter=1,
            current_day=1,
            target_length=request.target_chapters * 100
        )
        response = await agent_service.generate_content(gen_request)

        logger.info(f"大纲生成成功：小说{request.novel_id}，{request.target_chapters}章")

        return {
            "outline": response.final_content,
            "chapters": request.target_chapters
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"大纲生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/character")
async def generate_character(
    request: CharacterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成角色设定

    Args:
        request: 角色生成请求
        current_user: 当前用户
        db: 数据库会话

    Returns:
        生成的角色设定
    """
    try:
        # 验证小说所有权
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")

        # 构造角色生成提示词
        prompt = f"""请为以下小说生成一个{request.character_type}角色的详细设定：

小说标题：{novel.title}
小说类型：{novel.genre or '未指定'}
世界观：{novel.worldview or '未设定'}

角色类型：{request.character_type}
角色描述：{request.character_description}

请生成以下内容：
1. 姓名
2. 年龄/外貌
3. 性格特点
4. 背景故事
5. 能力/特长
6. 动机/目标
7. 人物关系
"""

        # 调用生成服务
        gen_request = GenerationRequest(
            novel_id=request.novel_id,
            prompt=prompt,
            chapter=1,
            current_day=1,
            target_length=500
        )
        response = await agent_service.generate_content(gen_request)

        logger.info(f"角色生成成功：小说{request.novel_id}，{request.character_type}")

        return {
            "character": response.final_content,
            "type": request.character_type
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"角色生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/test")
async def test_generation():
    """
    测试接口：生成示例内容

    用于快速测试系统是否正常工作
    """
    try:
        request = GenerationRequest(
            novel_id=1,
            prompt="主角在魔法塔顶与导师决裂",
            chapter=1,
            current_day=1,
            target_length=500
        )
        response = await agent_service.generate_content(request)
        return {
            "message": "测试成功",
            "final_content": response.final_content,
            "length": len(response.final_content)
        }
    except Exception as e:
        logger.error(f"测试失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"测试失败: {str(e)}"
        )
