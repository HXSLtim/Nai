## 项目上下文摘要（MCP功能完善）
生成时间：2025-11-15 05:02:00

### 1. 相似实现分析
- **实现1**: backend/app/services/character_mcp_service.py:1-659
  - 模式：服务层模式，单一职责原则
  - 可复用：MCPCharacterAction, MCPCharacterResponse schema模式
  - 需注意：异步操作处理，错误日志记录，权限验证

- **实现2**: backend/app/api/routes/characters.py:1-500
  - 模式：RESTful API路由模式，依赖注入
  - 可复用：权限验证装饰器，错误处理模式
  - 需注意：HTTP状态码规范，响应格式统一

- **实现3**: backend/app/services/agent_service.py:355-1038
  - 模式：Agent服务模式，LangChain集成
  - 可复用：LLM调用封装，JSON解析处理
  - 需注意：Token管理，温度参数调优，错误重试

### 2. 项目约定
- **命名约定**: 
  - 类名：PascalCase (UnifiedMCPService)
  - 函数名：snake_case (execute_unified_action)
  - 文件名：snake_case (unified_mcp_service.py)
  - 常量：UPPER_SNAKE_CASE
- **文件组织**: 
  - services/ 目录存放业务逻辑服务
  - api/routes/ 目录存放API路由
  - models/ 目录存放数据模型和Schema
- **导入顺序**: 
  1. 标准库导入
  2. 第三方库导入  
  3. 本地应用导入
- **代码风格**: 
  - 4空格缩进
  - 行长度限制120字符
  - 类型注解必须
  - 文档字符串使用简体中文

### 3. 可复用组件清单
- `app.crud.novel.get_novel_by_id`: 小说权限验证
- `app.api.dependencies.get_current_user`: 用户认证
- `app.services.agent_service.agent_service`: AI Agent调用
- `app.models.schemas`: 通用Schema模式
- `loguru.logger`: 统一日志记录

### 4. 测试策略
- **测试框架**: pytest (推断自项目结构)
- **测试模式**: 单元测试 + 集成测试
- **参考文件**: 需要创建测试文件
- **覆盖要求**: 正常流程 + 边界条件 + 错误处理 + 权限验证

### 5. 依赖和集成点
- **外部依赖**: FastAPI, SQLAlchemy, Pydantic, LangChain, OpenAI
- **内部依赖**: 
  - character_mcp_service (角色MCP服务)
  - agent_service (AI Agent服务)
  - novel CRUD操作
- **集成方式**: 依赖注入，服务层调用
- **配置来源**: app.core.config.settings

### 6. 技术选型理由
- **为什么用MCP**: 实现AI对小说元素的完全掌控，统一操作接口
- **优势**: 
  - 统一的操作模式
  - 可扩展的目标类型
  - AI自主决策能力
- **劣势和风险**: 
  - 复杂度较高
  - 需要完善的错误处理
  - AI决策的可控性

### 7. 关键风险点
- **并发问题**: 多个MCP操作同时执行可能冲突
- **边界条件**: 
  - 无效的目标类型或操作类型
  - 权限验证失败
  - AI服务不可用
- **性能瓶颈**: 
  - 大量AI调用的延迟
  - 数据库查询优化
- **安全考虑**: 
  - 用户数据隔离
  - AI操作的审计日志
