"""
Pytest配置文件
定义测试夹具（fixtures）
"""
import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_novel_id():
    """测试用的小说ID"""
    return 1


@pytest.fixture
def test_prompt():
    """测试用的剧情提示词"""
    return "主角在魔法塔顶与导师决裂，雷电在天空中闪烁"


@pytest.fixture
def test_worldview_rules():
    """测试用的世界观规则"""
    return {
        "魔法等级上限": 9,
        "飞行速度上限": 100,
    }


@pytest.fixture
async def mock_openai_response():
    """模拟OpenAI API响应"""
    return {
        "worldview": "魔法塔顶，雷电交加，魔法能量在空气中涌动。",
        "character": "李明咬紧牙关，眼中闪过决绝的光芒。'导师，我不能再跟随你了！'他的声音在雷声中回荡。",
        "plot": "在魔法塔的最高层，李明终于对导师说出了藏在心底已久的话。雷电在天空中撕裂，映照出两人决裂的瞬间。"
    }
