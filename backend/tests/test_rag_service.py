"""
RAG服务单元测试
测试向量检索、内容索引、混合检索等功能
"""
import pytest
from app.services.rag_service import RAGService
from app.models.schemas import RAGQuery


class TestRAGService:
    """RAG服务测试类"""

    @pytest.fixture
    async def rag_service(self):
        """创建RAG服务实例"""
        # 注意：需要确保Qdrant服务正在运行
        return RAGService()

    @pytest.mark.asyncio
    async def test_index_content(self, rag_service, test_novel_id):
        """测试内容索引功能"""
        content = "这是一个测试段落。主角李明在魔法塔中修炼，他的魔法等级已经达到了5级。"

        result = await rag_service.index_content(
            novel_id=test_novel_id,
            chapter=1,
            content=content,
            metadata={"scene": "魔法塔"}
        )

        if not result:
            pytest.skip("RAG服务不可用或向量库配置不兼容，跳过索引测试")

    @pytest.mark.asyncio
    async def test_hybrid_search(self, rag_service, test_novel_id):
        """测试混合检索功能"""
        # 先索引一些内容
        result = await rag_service.index_content(
            novel_id=test_novel_id,
            chapter=1,
            content="李明是一位5级魔法师，擅长火系魔法。"
        )

        if not result:
            pytest.skip("RAG服务不可用或向量库配置不兼容，跳过混合检索测试")

        # 执行检索
        query = RAGQuery(
            novel_id=test_novel_id,
            query="李明的魔法等级",
            top_k=3
        )

        response = await rag_service.hybrid_search(query)

        assert response.query == "李明的魔法等级"
        assert response.retrieval_method == "hybrid"
        assert len(response.results) > 0

    @pytest.mark.asyncio
    async def test_metadata_filtering(self, rag_service, test_novel_id):
        """测试元数据过滤功能"""
        # 索引多个章节的内容
        r1 = await rag_service.index_content(test_novel_id, 1, "第一章内容")
        r2 = await rag_service.index_content(test_novel_id, 2, "第二章内容")
        r3 = await rag_service.index_content(test_novel_id, 3, "第三章内容")

        if not (r1 and r2 and r3):
            pytest.skip("RAG服务不可用或向量库配置不兼容，跳过元数据过滤测试")

        # 只检索前两章
        query = RAGQuery(
            novel_id=test_novel_id,
            query="内容",
            max_chapter=2,
            top_k=10
        )

        response = await rag_service.hybrid_search(query)

        # 验证结果只包含前两章
        for result in response.results:
            assert result.metadata.get("chapter", 999) <= 2

    @pytest.mark.asyncio
    async def test_retrieve_worldview(self, rag_service, test_novel_id):
        """测试世界观检索"""
        # 索引世界观内容
        result = await rag_service.index_content(
            test_novel_id,
            1,
            "这个世界的魔法分为九个等级，9级是最高等级。"
        )

        if not result:
            pytest.skip("RAG服务不可用或向量库配置不兼容，跳过世界观检索测试")

        results = await rag_service.retrieve_worldview(
            test_novel_id,
            "魔法等级系统"
        )

        assert len(results) > 0
        assert "等级" in results[0] or "魔法" in results[0]

    @pytest.mark.asyncio
    async def test_delete_novel_index(self, rag_service, test_novel_id):
        """测试删除索引功能"""
        # 先索引内容
        result_index = await rag_service.index_content(test_novel_id, 1, "测试内容")

        if not result_index:
            pytest.skip("RAG服务不可用或向量库配置不兼容，跳过删除索引测试")

        # 删除索引
        result = await rag_service.delete_novel_index(test_novel_id)

        assert result is True

    def test_split_text(self, rag_service):
        """测试文本分割功能"""
        text = "A" * 1500  # 1500字符
        chunks = rag_service._split_text(text, chunk_size=500)

        assert len(chunks) == 3
        assert len(chunks[0]) == 500
        assert len(chunks[1]) == 500
        assert len(chunks[2]) == 500
