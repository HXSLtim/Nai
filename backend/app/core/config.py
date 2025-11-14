"""
应用配置模块
使用Pydantic Settings管理环境变量
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = "AI小说创作系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change_this_in_production"

    # OpenAI配置
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str = "https://api.openai.com/v1"  # API地址（兼容DeepSeek等）
    OPENAI_MODEL_COMPLEX: str = "gpt-4o"  # 复杂任务使用
    OPENAI_MODEL_SIMPLE: str = "gpt-4o-mini"  # 简单任务使用

    # PostgreSQL配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "novel_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_password"

    # Chroma向量数据库配置（本地文件存储）
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "novel_embeddings"

    # Ollama Embedding配置（本地）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_EMBED_MODEL: str = "mofanke/m3e-base"  # 或 "bge-small-zh-v1.5"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # Neo4j配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"

    # CORS配置
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://192.168.31.101:3000,http://192.168.31.101:8080,*"

    # 日志配置
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        """生成PostgreSQL数据库URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def allowed_origins_list(self) -> List[str]:
        """解析CORS允许的源"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def redis_url(self) -> str:
        """生成Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        """Pydantic配置"""
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
