"""
网文编辑Agent服务
提供对单章内容的轻量编辑审核（节奏、爽点、信息量、重复度等），不做违规/敏感内容审核。
"""
from datetime import datetime
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from loguru import logger

from app.core.config import settings
from app.models.schemas import EditorReview
from app.models.novel import Novel, Chapter


class EditorService:
    """网文编辑Agent服务类"""

    def __init__(self) -> None:
        # 复用相对便宜的简单模型，用于轻量点评
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_SIMPLE,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            temperature=0.5,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是一名资深中文网文编辑，只做内容质量与节奏方面的轻量点评，不做任何法律或敏感内容审核。

请根据作者当前这一章的内容，从以下维度给出简明、可执行的建议：
- 节奏：是否拖沓、推进是否够快；
- 爽点/冲突：是否有足够的矛盾和爽点；
- 信息量：是否堆设定/解释过多；
- 重复度：是否有明显的内容/表达重复；
- 人物表现：主角和关键角色是否有鲜明表现。

输出时请严格使用 JSON 格式，结构如下（示例，仅说明字段，不是内容）：
{{
  "score": 85,
  "summary": "整体节奏较为流畅，但开头略慢，可适当前置冲突。",
  "issues": [
    {{
      "type": "节奏",
      "level": "warn",
      "message": "开场连续三段内心独白，缺少外部动作描写。",
      "suggestion": "可以删减部分心理描写，在前两页内安排一个小冲突或事件。"
    }}
  ],
  "suggested_tags": ["爽文", "学院流" ]
}}

不要输出任何解释文字或前后缀，只输出 JSON。""",
                ),
                (
                    "user",
                    """小说标题：{title}
小说类型：{genre}
世界观节选：{worldview}

当前章节：第 {chapter_number} 章《{chapter_title}》
章节内容：
{chapter_content}
""",
                ),
            ]
        )

    async def review_chapter(self, *, novel: Novel, chapter: Chapter) -> Optional[EditorReview]:
        """对单章内容进行轻量审核，返回编辑点评结果。

        若模型返回格式异常或调用失败，返回 None，不影响业务流程。
        """
        # 章节内容过长时做截断，防止提示过大
        content = chapter.content or ""
        if len(content) > 6000:
            content = content[-6000:]

        worldview = novel.worldview or ""
        if len(worldview) > 800:
            worldview = worldview[:800] + "..."

        chain = self.prompt | self.llm

        try:
            result = await chain.ainvoke(
                {
                    "title": novel.title,
                    "genre": novel.genre or "未指定",
                    "worldview": worldview or "未设定",
                    "chapter_number": chapter.chapter_number,
                    "chapter_title": chapter.title,
                    "chapter_content": content or "(本章暂无内容)",
                }
            )

            raw = (result.content or "").strip()
            if not raw:
                return None

            # 允许模型在外层多输出一些内容，尽量提取最外层 JSON
            import json

            try:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                json_str = raw[start:end] if start != -1 and end != 0 else raw
                data = json.loads(json_str)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"解析编辑Agent JSON失败: {e}")
                return None

            score = int(data.get("score") or 0)
            summary = str(data.get("summary") or "").strip()
            issues_data = data.get("issues") or []
            suggested_tags = data.get("suggested_tags") or []

            # 规范化 issues
            issues = []
            for item in issues_data:
                try:
                    issues.append(
                        {
                            "type": str(item.get("type") or "其它"),
                            "level": str(item.get("level") or "info"),
                            "message": str(item.get("message") or "").strip(),
                            "suggestion": (str(item.get("suggestion")) or "").strip() or None,
                        }
                    )
                except Exception:
                    continue

            review = EditorReview(
                score=score,
                summary=summary or "本章整体可读性良好，建议根据编辑意见做轻量调整。",
                issues=issues,
                suggested_tags=[str(t) for t in suggested_tags if str(t).strip()],
                created_at=datetime.utcnow(),
            )
            return review

        except Exception as e:  # noqa: BLE001
            logger.warning(f"编辑Agent调用失败（novel_id={novel.id}, chapter_id={chapter.id}）: {e}")
            return None


# 单例实例，供路由直接使用
editor_service = EditorService()
