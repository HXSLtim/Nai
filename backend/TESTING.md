# 测试文档

完整的测试套件说明，包括单元测试、集成测试和端到端测试。

## 📋 测试覆盖范围

### 1. 单元测试（Unit Tests）

**test_rag_service.py** - RAG检索服务测试
- ✅ 内容索引功能
- ✅ 混合检索功能
- ✅ 元数据过滤
- ✅ 世界观检索
- ✅ 文本分割
- ✅ 索引删除

**test_consistency_service.py** - 一致性检查服务测试
- ✅ 规则引擎（魔法等级、飞行速度验证）
- ✅ 时间线管理（时间倒退检测、地理移动合理性）
- ✅ 情绪状态机（情绪转换合理性）
- ✅ 完整一致性检查流程

### 2. 集成测试（Integration Tests）

需要外部服务（Qdrant、OpenAI API）：
- ✅ RAG服务与Qdrant集成
- ✅ Agent服务与OpenAI API集成
- ✅ 完整的生成工作流

### 3. 端到端测试（E2E Tests）

**test_api.py** - API端点测试
- ✅ 健康检查接口
- ✅ 内容生成接口
- ✅ 请求验证
- ✅ 错误处理

## 🚀 运行测试

### 方式1：使用pytest直接运行

```bash
# 进入backend目录
cd backend

# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_rag_service.py

# 运行特定测试类
pytest tests/test_consistency_service.py::TestRuleEngine

# 运行特定测试函数
pytest tests/test_consistency_service.py::TestRuleEngine::test_validate_magic_level_pass

# 显示详细输出
pytest tests/ -v

# 显示print输出
pytest tests/ -s

# 运行并生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### 方式2：使用测试脚本

```bash
# 运行所有测试
python run_tests.py --mode all

# 只运行单元测试
python run_tests.py --mode unit

# 运行集成测试（需要OpenAI API）
python run_tests.py --mode integration

# 生成覆盖率报告
python run_tests.py --mode coverage

# 运行特定文件
python run_tests.py --file test_rag_service.py
```

### 方式3：使用Make命令（如果配置了Makefile）

```bash
make test          # 运行所有测试
make test-unit     # 单元测试
make test-cov      # 覆盖率测试
```

## 📊 测试覆盖率

### 查看覆盖率报告

```bash
# 生成HTML报告
pytest tests/ --cov=app --cov-report=html

# 在浏览器中打开
# Windows: start htmlcov\index.html
# Linux: xdg-open htmlcov/index.html
# Mac: open htmlcov/index.html
```

### 目标覆盖率

- **整体代码覆盖率**: ≥ 80%
- **核心服务**: ≥ 90%
  - agent_service.py
  - rag_service.py
  - consistency_service.py

## 🔧 测试配置

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --tb=short
    --cov=app
    --cov-report=html

markers =
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试
```

### conftest.py

提供了测试夹具（fixtures）：
- `client`: FastAPI测试客户端
- `test_novel_id`: 测试用小说ID
- `test_prompt`: 测试用剧情提示词
- `test_worldview_rules`: 测试用世界观规则

## 🐛 调试测试

### 使用pytest调试

```bash
# 进入Python调试器（失败时）
pytest tests/ --pdb

# 在第一个测试处进入调试器
pytest tests/ --trace

# 显示所有print输出
pytest tests/ -s

# 显示局部变量
pytest tests/ -l
```

### 使用VSCode调试

在 `.vscode/launch.json` 中添加：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "tests/",
                "-v"
            ],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

## ⚠️ 注意事项

### 1. 集成测试需要外部服务

运行集成测试前，确保以下服务正在运行：

```bash
# 启动Docker服务
docker-compose up -d

# 检查服务状态
docker ps
```

### 2. OpenAI API密钥

集成测试需要真实的OpenAI API密钥：

```bash
# 设置环境变量
export OPENAI_API_KEY=your_key_here  # Linux/Mac
set OPENAI_API_KEY=your_key_here     # Windows

# 或者在.env文件中配置
OPENAI_API_KEY=your_key_here
```

### 3. 跳过集成测试

默认情况下，需要外部API的测试会被跳过。要运行这些测试：

```bash
pytest tests/ --run-integration
```

### 4. 测试隔离

- 每个测试应该是独立的，不依赖其他测试
- 使用fixtures创建测试数据
- 测试后清理资源（索引、数据库记录）

## 📝 编写新测试

### 基本结构

```python
import pytest
from app.services.your_service import YourService


class TestYourService:
    """你的服务测试类"""

    @pytest.fixture
    def your_service(self):
        """创建服务实例"""
        return YourService()

    def test_basic_function(self, your_service):
        """测试基本功能"""
        result = your_service.basic_function()
        assert result is not None

    @pytest.mark.asyncio
    async def test_async_function(self, your_service):
        """测试异步功能"""
        result = await your_service.async_function()
        assert result["status"] == "success"
```

### 命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`
- 测试应该清楚描述被测试的功能

### 断言规范

```python
# 使用清晰的断言消息
assert result is True, "结果应该为True"

# 使用具体的断言
assert len(items) == 3  # 而不是 assert items

# 测试异常
with pytest.raises(ValueError):
    service.invalid_operation()
```

## 📈 持续集成（CI）

### GitHub Actions配置示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## 🎯 测试最佳实践

1. **测试应该快速**：单元测试应在几秒内完成
2. **测试应该独立**：不依赖执行顺序
3. **测试应该可重复**：每次运行结果一致
4. **测试应该清晰**：命名和结构一目了然
5. **测试应该全面**：覆盖正常流程、边界条件、异常情况

## 🔍 常见问题

### Q1: 测试失败："Qdrant connection refused"

**解决方案**：
```bash
# 确保Qdrant正在运行
docker-compose up -d qdrant

# 检查端口
netstat -an | findstr 6333  # Windows
netstat -an | grep 6333     # Linux/Mac
```

### Q2: 测试失败："OpenAI API key not found"

**解决方案**：
```bash
# 在.env文件中设置
OPENAI_API_KEY=sk-your-key

# 或者跳过集成测试
pytest tests/ -m "not integration"
```

### Q3: 测试覆盖率太低

**解决方案**：
```bash
# 查看未覆盖的行
pytest tests/ --cov=app --cov-report=term-missing

# 针对性编写测试覆盖这些行
```

---

**测试是代码质量的保障！** ✅
