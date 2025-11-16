# 快速启动指南

本指南帮助你在5分钟内启动AI小说创作系统。

## 前置条件

- Python 3.10+
- Docker Desktop（用于运行数据库）
- OpenAI API密钥

## 步骤1：启动数据库服务

```bash
# 在项目根目录执行
docker-compose up -d

# 验证服务状态
docker ps

# 应该看到4个容器运行中：
# - novel_postgres (PostgreSQL)
# - novel_qdrant (Qdrant向量数据库)
# - novel_redis (Redis缓存)
# - novel_neo4j (Neo4j知识图谱)
```

## 步骤2：配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑.env文件，填入你的OpenAI API密钥
# OPENAI_API_KEY=sk-your-api-key-here
```

## 步骤3：安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 步骤4：启动后端服务

```bash
# 在backend目录下执行
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者直接运行
python app/main.py
```

启动成功后，访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

## 步骤5：测试生成功能

### 方式1：通过API文档测试

1. 打开 http://localhost:8000/docs
2. 找到 `GET /api/generation/test` 接口
3. 点击 "Try it out"
4. 点击 "Execute"
5. 查看生成的小说段落

### 方式2：使用curl命令测试

```bash
curl http://localhost:8000/api/generation/test
```

### 方式3：使用Python脚本测试

```python
import requests

response = requests.get("http://localhost:8000/api/generation/test")
print(response.json())
```

## 服务管理

### 查看后端日志

```bash
# 后端日志会实时显示在终端
# 可以看到Agent A、B、C的工作流程
```

### 查看数据库

**Qdrant管理界面**
- 访问：http://localhost:6333/dashboard
- 查看向量集合和索引状态

**Neo4j浏览器**
- 访问：http://localhost:7474
- 用户名：neo4j
- 密码：neo4j_password
- 查看角色关系图谱

### 停止服务

```bash
# 停止后端（Ctrl+C）

# 停止数据库
docker-compose down

# 停止并删除数据（谨慎使用）
docker-compose down -v
```

## 常见问题

### 问题1：端口被占用

```bash
# Windows: 查看端口占用
netstat -ano | findstr :8000

# 杀死占用端口的进程
taskkill /PID <进程ID> /F
```

### 问题2：Docker服务启动失败

```bash
# 查看日志
docker-compose logs

# 重启特定服务
docker-compose restart qdrant
```

### 问题3：OpenAI API调用失败

- 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
- 检查网络连接
- 查看后端日志中的错误信息

### 问题4：依赖安装失败

```bash
# 升级pip
python -m pip install --upgrade pip

# 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 下一步

完成快速启动后，你可以：

1. **阅读技术文档**
   - `.claude/executive-summary.md` - 执行摘要
   - `.claude/ai-novel-writing-system-analysis.md` - 完整技术方案

2. **定制世界观规则**
   - 编辑 `backend/app/services/consistency_service.py`
   - 添加自己的魔法体系、物理规则

3. **调整Agent提示词**
   - 编辑 `backend/app/services/agent_service.py`
   - 修改Agent A、B、C的系统提示词

4. **开发前端界面**
   - 查看 `frontend/` 目录
   - 使用Next.js构建可视化管理界面

## 技术支持

如有问题，请：
1. 查看 `README.md` 了解项目概览
2. 查看 `.claude/quick-reference.md` 获取技术参考
3. 提交Issue到GitHub仓库（推荐）
4. 发送邮件至 a2778978136@163.com 获取支持
5. 访问项目主页：https://github.com/HXSLtim/Nai

## 项目信息

- **项目维护者**：hahage
- **邮箱**：a2778978136@163.com
- **GitHub**：https://github.com/HXSLtim
- **版本**：Alpha 0.1.0

---

**祝你使用愉快！** 🎉

如有问题或建议，欢迎联系项目维护者 hahage。
