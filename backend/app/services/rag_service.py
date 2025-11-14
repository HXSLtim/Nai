"""
RAG检索服务
使用Chroma向量数据库 + Ollama本地Embedding
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.embeddings import BaseEmbedding
from app.core.config import settings
from app.models.schemas import RAGQuery, RAGResult, RAGResponse
from loguru import logger
import os


class RAGService:
    """RAG检索服务类（使用Chroma + Ollama）"""

    def __init__(self):
        """初始化RAG服务"""
        self.available = False
        self.vector_store = None
        self.embed_model: Optional[BaseEmbedding] = None
        self.index = None
        # 当前Embedding向量维度，用于区分不同维度的Chroma集合
        self.embed_dim: Optional[int] = None

        try:
            # 初始化Embedding模型（Ollama本地）
            self._init_embedding()

            # 初始化Chroma向量数据库
            self._init_vector_store()

            self.available = True
            logger.info("✅ RAG服务初始化成功（Chroma + Ollama）")

        except Exception as e:
            logger.warning(f"⚠️ RAG服务初始化失败: {e}")
            logger.warning("RAG功能将不可用，但不影响其他功能")
            self.available = False

    def _init_embedding(self):
        """初始化Embedding模型"""
        try:
            # 尝试使用Ollama本地Embedding
            logger.info("尝试连接Ollama Embedding服务...")
            self.embed_model = OllamaEmbedding(
                model_name=settings.OLLAMA_EMBED_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                request_timeout=30.0,
            )

            # 测试连接并记录向量维度
            test_embedding = self.embed_model.get_text_embedding("测试")
            self.embed_dim = len(test_embedding)
            logger.info(f"✅ Ollama Embedding已连接，向量维度: {self.embed_dim}")

        except Exception as e:
            logger.warning(f"Ollama连接失败: {e}")
            logger.info("回退到简单Embedding模型...")

            # 回退方案：使用HuggingFace本地模型（如果Ollama不可用）
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding

            self.embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )

            # 同样记录维度，保持后续向量库配置一致
            test_embedding = self.embed_model.get_text_embedding("测试")
            self.embed_dim = len(test_embedding)
            logger.info("✅ 使用HuggingFace本地Embedding")
            logger.info(f"✅ Embedding向量维度: {self.embed_dim}")

    def _init_vector_store(self):
        """初始化Chroma向量数据库"""
        # 确保数据目录存在
        chroma_path = settings.CHROMA_DB_PATH
        os.makedirs(chroma_path, exist_ok=True)

        # 创建Chroma客户端（持久化存储）
        chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )

        # 根据Embedding维度区分集合名称，避免维度不匹配
        base_collection_name = settings.CHROMA_COLLECTION_NAME
        if self.embed_dim:
            collection_name = f"{base_collection_name}_{self.embed_dim}"
        else:
            collection_name = base_collection_name

        chroma_collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": (
                    f"小说内容向量存储（维度={self.embed_dim}）" if self.embed_dim else "小说内容向量存储"
                )
            },
        )

        # 创建向量存储
        self.vector_store = ChromaVectorStore(
            chroma_collection=chroma_collection
        )

        logger.info(f"✅ Chroma向量数据库已初始化：{chroma_path}")
        logger.info(f"✅ 集合名称：{collection_name}")

    async def index_content(
        self,
        novel_id: int,
        chapter: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        索引小说内容到向量数据库

        Args:
            novel_id: 小说ID
            chapter: 章节号
            content: 内容文本
            metadata: 额外元数据

        Returns:
            是否成功
        """
        if not self.available:
            logger.warning("RAG服务不可用，跳过索引")
            return False

        try:
            # 分块处理长文本（每500字一块）
            chunks = self._split_text(content, chunk_size=500)

            # 创建文档列表
            documents = []
            for idx, chunk in enumerate(chunks):
                doc_metadata = {
                    "novel_id": novel_id,
                    "chapter": chapter,
                    "chunk_index": idx,
                    **(metadata or {})
                }

                documents.append(
                    Document(
                        text=chunk,
                        metadata=doc_metadata,
                        id_=f"{novel_id}_{chapter}_{idx}"
                    )
                )

            # 创建存储上下文
            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )

            # 创建或更新索引
            if self.index is None:
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    storage_context=storage_context,
                    embed_model=self.embed_model,
                    show_progress=True
                )
            else:
                # 添加文档到现有索引
                for doc in documents:
                    self.index.insert(doc)

            logger.info(f"✅ 成功索引小说{novel_id}章节{chapter}，共{len(chunks)}个分块")
            return True

        except Exception as e:
            logger.error(f"索引内容失败: {e}")
            return False

    async def hybrid_search(self, query: RAGQuery) -> RAGResponse:
        """
        混合检索（向量检索 + 元数据过滤）

        Args:
            query: 检索请求

        Returns:
            检索响应
        """
        if not self.available or self.index is None:
            logger.warning("RAG服务不可用，返回空结果")
            return RAGResponse(
                query=query.query,
                results=[],
                retrieval_method="hybrid"
            )

        try:
            # 创建检索器
            retriever = self.index.as_retriever(
                similarity_top_k=query.top_k
            )

            # 执行检索
            nodes = retriever.retrieve(query.query)

            # 过滤结果（根据novel_id和max_chapter）
            filtered_nodes = []
            for node in nodes:
                metadata = node.metadata

                # 检查novel_id
                if metadata.get("novel_id") != query.novel_id:
                    continue

                # 检查max_chapter
                if query.max_chapter is not None:
                    if metadata.get("chapter", 0) > query.max_chapter:
                        continue

                filtered_nodes.append(node)

            # 转换为RAGResult
            results = [
                RAGResult(
                    content=node.get_content(),
                    metadata={
                        "chapter": node.metadata.get("chapter"),
                        "chunk_index": node.metadata.get("chunk_index"),
                        **{k: v for k, v in node.metadata.items()
                           if k not in ["chapter", "chunk_index", "novel_id"]}
                    },
                    score=node.score if hasattr(node, 'score') else 0.0
                )
                for node in filtered_nodes[:query.top_k]
            ]

            logger.info(f"✅ 混合检索完成，查询:'{query.query}'，返回{len(results)}条结果")

            return RAGResponse(
                query=query.query,
                results=results,
                retrieval_method="hybrid"
            )

        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            return RAGResponse(
                query=query.query,
                results=[],
                retrieval_method="hybrid"
            )

    async def retrieve_worldview(
        self,
        novel_id: int,
        query: str,
        max_chapter: Optional[int] = None,
    ) -> List[str]:
        """
        检索世界观相关内容

        Args:
            novel_id: 小说ID
            query: 查询内容

        Returns:
            相关内容列表
        """
        rag_query = RAGQuery(
            novel_id=novel_id,
            query=query,
            top_k=3,
            max_chapter=max_chapter,
        )
        response = await self.hybrid_search(rag_query)
        return [result.content for result in response.results]

    async def retrieve_character_info(
        self,
        novel_id: int,
        character_name: str,
        max_chapter: Optional[int] = None,
    ) -> List[str]:
        """
        检索角色相关信息

        Args:
            novel_id: 小说ID
            character_name: 角色名称

        Returns:
            角色相关内容列表
        """
        query = f"{character_name}的性格、外貌、背景"
        rag_query = RAGQuery(
            novel_id=novel_id,
            query=query,
            top_k=3,
            max_chapter=max_chapter,
        )
        response = await self.hybrid_search(rag_query)
        return [result.content for result in response.results]

    def _split_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        分割文本为固定大小的块

        Args:
            text: 原始文本
            chunk_size: 块大小（字符数）

        Returns:
            文本块列表
        """
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    async def delete_novel_index(self, novel_id: int) -> bool:
        """
        删除小说的所有索引

        Args:
            novel_id: 小说ID

        Returns:
            是否成功
        """
        if not self.available:
            logger.warning("RAG服务不可用，跳过删除")
            return False

        try:
            # Chroma删除需要通过collection的delete方法
            # 注意：这里需要根据metadata过滤删除
            # 由于LlamaIndex的抽象层限制，我们直接操作collection
            if self.vector_store and hasattr(self.vector_store, '_collection'):
                collection = self.vector_store._collection
                # 获取所有该小说的ID
                results = collection.get(
                    where={"novel_id": novel_id}
                )
                if results and results.get('ids'):
                    collection.delete(ids=results['ids'])
                    logger.info(f"✅ 删除小说{novel_id}的所有索引")
                    return True

            logger.warning(f"未找到小说{novel_id}的索引")
            return False

        except Exception as e:
            logger.error(f"删除索引失败: {e}")
            return False

    async def cleanup_novel_vectors(self, novel_id: int) -> int:
        """
        清理小说的向量数据
        
        Args:
            novel_id: 小说ID
            
        Returns:
            清理的向量数量
        """
        if not self.available:
            logger.warning("RAG服务不可用，跳过清理向量")
            return 0

        try:
            if self.vector_store and hasattr(self.vector_store, '_collection'):
                collection = self.vector_store._collection
                # 获取所有该小说的向量
                results = collection.get(
                    where={"novel_id": novel_id}
                )
                
                count = 0
                if results and results.get('ids'):
                    count = len(results['ids'])
                    collection.delete(ids=results['ids'])
                    logger.info(f"✅ 清理小说{novel_id}的{count}个向量")
                
                return count
            
            return 0
            
        except Exception as e:
            logger.error(f"清理向量数据失败: {e}")
            return 0

    async def cleanup_novel_graph(self, novel_id: int) -> int:
        """
        清理小说的知识图谱数据
        
        Args:
            novel_id: 小说ID
            
        Returns:
            清理的图谱节点数量
        """
        # 这里可以添加Neo4j或其他图数据库的清理逻辑
        # 目前返回0，表示没有图谱数据需要清理
        try:
            # TODO: 实现知识图谱清理
            # 例如：删除Neo4j中相关的节点和关系
            logger.info(f"知识图谱清理功能待实现，小说ID: {novel_id}")
            return 0
        except Exception as e:
            logger.error(f"清理知识图谱失败: {e}")
            return 0

    async def cleanup_novel_cache(self, novel_id: int) -> int:
        """
        清理小说的缓存数据
        
        Args:
            novel_id: 小说ID
            
        Returns:
            清理的缓存条目数量
        """
        try:
            # 这里可以清理Redis缓存或其他缓存系统
            # 目前只是模拟清理
            cache_keys = [
                f"novel:{novel_id}:worldview",
                f"novel:{novel_id}:characters",
                f"novel:{novel_id}:plot",
                f"novel:{novel_id}:style",
            ]
            
            # TODO: 实现实际的缓存清理
            # 例如：redis_client.delete(*cache_keys)
            logger.info(f"缓存清理功能待实现，小说ID: {novel_id}")
            return len(cache_keys)
            
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return 0

    async def cleanup_chapter_data(self, novel_id: int, chapter_id: int) -> bool:
        """
        清理特定章节的数据
        
        Args:
            novel_id: 小说ID
            chapter_id: 章节ID
            
        Returns:
            是否成功
        """
        if not self.available:
            logger.warning("RAG服务不可用，跳过清理章节数据")
            return False

        try:
            if self.vector_store and hasattr(self.vector_store, '_collection'):
                collection = self.vector_store._collection
                # 删除特定章节的向量数据
                results = collection.get(
                    where={
                        "novel_id": novel_id,
                        "chapter": chapter_id
                    }
                )
                
                if results and results.get('ids'):
                    collection.delete(ids=results['ids'])
                    logger.info(f"✅ 清理小说{novel_id}章节{chapter_id}的向量数据")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"清理章节数据失败: {e}")
            return False


# 创建全局实例
rag_service = RAGService()
