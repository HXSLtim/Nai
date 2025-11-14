"""
API端到端测试
测试FastAPI路由和完整的请求响应流程
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthAPI:
    """健康检查API测试"""

    def test_health_check(self, client: TestClient):
        """测试健康检查接口"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data

    def test_ping(self, client: TestClient):
        """测试ping接口"""
        response = client.get("/api/ping")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "pong"


class TestGenerationAPI:
    """内容生成API测试"""

    def test_generate_content_missing_fields(self, client: TestClient):
        """测试生成接口 - 缺少必填字段"""
        response = client.post(
            "/api/generation/generate",
            json={}
        )

        assert response.status_code == 422  # Validation error

    def test_generate_content_invalid_data(self, client: TestClient):
        """测试生成接口 - 无效数据"""
        response = client.post(
            "/api/generation/generate",
            json={
                "novel_id": "invalid",  # 应该是int
                "prompt": "测试",
                "chapter": 1
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_generate_content_success(self, client: TestClient, request):
        """测试生成接口 - 成功（需要真实API）"""
        try:
            run_integration = request.config.getoption("--run-integration")
        except ValueError:
            run_integration = False

        if not run_integration:
            pytest.skip("需要OpenAI API密钥，使用 --run-integration 运行")
        response = client.post(
            "/api/generation/generate",
            json={
                "novel_id": 1,
                "prompt": "主角在森林中遇到了一只神秘的魔兽",
                "chapter": 1,
                "current_day": 1,
                "target_length": 300
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "final_content" in data
        assert "agent_outputs" in data
        assert len(data["agent_outputs"]) == 3
        assert data["novel_id"] == 1
        assert data["chapter"] == 1

    @pytest.mark.asyncio
    async def test_generation_test_endpoint(self, client: TestClient, request):
        """测试生成测试接口"""
        try:
            run_integration = request.config.getoption("--run-integration")
        except ValueError:
            run_integration = False

        if not run_integration:
            pytest.skip("需要OpenAI API密钥，使用 --run-integration 运行")
        response = client.get("/api/generation/test")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "测试成功"
        assert "final_content" in data
        assert "length" in data
        assert isinstance(data["length"], int)


def pytest_addoption(parser):
    """添加pytest命令行选项"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="运行需要外部API的集成测试"
    )
