# 团队协作指南

AI小说创作系统的团队开发规范、工作流程和最佳实践。

## 👥 团队结构

### 核心团队（7人）

| 角色 | 人数 | 主要职责 | 代号 |
|-----|-----|---------|-----|
| **项目经理/产品经理** | 1人 | 需求管理、进度协调 | PM |
| **后端开发A** | 1人 | 核心架构（Agent、RAG、一致性）| BE-A |
| **后端开发C** | 1人 | 用户系统、章节管理 | BE-C |
| **后端开发D** | 1人 | 导出功能、性能优化 | BE-D |
| **前端开发A** | 1人 | 核心页面、内容生成 | FE-A |
| **前端开发B** | 1人 | 角色、世界观、大纲管理 | FE-B |
| **UI/UX设计师** | 1人 | 设计系统、用户体验 | UI |
| **全栈开发E（可选）** | 1人 | 实时协作、前后端联调 | FS-E |

### 技能矩阵

| 成员 | Python | TypeScript | AI/LLM | UI设计 | DevOps |
|-----|--------|-----------|--------|--------|--------|
| BE-A | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | - | ⭐⭐ |
| BE-C | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | - | ⭐⭐⭐ |
| BE-D | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | - | ⭐⭐⭐⭐ |
| FE-A | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| FE-B | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| UI | - | ⭐⭐ | - | ⭐⭐⭐⭐⭐ | - |

---

## 📅 工作流程

### Sprint计划（2周一个迭代）

```
Sprint 1 (Week 1-2): Alpha版本核心功能
  - 后端：Agent服务、RAG检索、一致性检查
  - 前端：项目初始化、基础框架
  - 交付：可运行的后端API + 前端脚手架

Sprint 2 (Week 3-4): Beta版本 - 小说和内容生成
  - 后端：优化Agent工作流、添加缓存
  - 前端：小说管理、内容生成界面
  - 交付：完整的生成流程

Sprint 3 (Week 5-6): 角色和世界观管理
  - 后端：用户认证、章节管理
  - 前端：角色、世界观、大纲管理
  - 交付：管理功能完整

Sprint 4 (Week 7-8): 功能增强和优化
  - 后端：导出功能、缓存优化
  - 前端：UI优化、性能调优
  - 交付：可上线的Production版本
```

### 每日站会（Daily Standup）

**时间**：每天上午10:00，15分钟

**三个问题**：
1. 昨天完成了什么？
2. 今天计划做什么？
3. 遇到了什么阻碍？

**形式**：
- 现场会议或视频会议
- 简洁明了，不展开讨论
- 复杂问题会后单独讨论

### 每周回顾（Weekly Retrospective）

**时间**：每周五下午4:00，1小时

**内容**：
1. **成果展示**：Demo本周完成的功能
2. **进度回顾**：对比计划和实际进度
3. **问题讨论**：技术难点、协作问题
4. **下周计划**：明确下周目标和任务

---

## 🔀 Git工作流

### 分支策略（Git Flow）

```
main (生产环境)
  ↑
develop (开发环境)
  ↑
feature/xxx (功能分支)
  ↑
本地开发
```

### 分支命名规范

| 分支类型 | 命名格式 | 示例 | 说明 |
|---------|---------|------|------|
| 功能开发 | `feature/功能名` | `feature/user-auth` | 新功能开发 |
| Bug修复 | `fix/问题描述` | `fix/api-timeout` | 修复Bug |
| 性能优化 | `perf/优化内容` | `perf/cache-llm` | 性能改进 |
| 文档更新 | `docs/文档名` | `docs/api-reference` | 文档修改 |
| 重构 | `refactor/模块名` | `refactor/agent-service` | 代码重构 |

### 提交信息规范（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）**：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 添加测试
- `chore`: 构建/工具配置

**示例**：
```bash
feat(agent): 实现三Agent协作工作流

- 添加Agent A（世界观描写）
- 添加Agent B（角色对话）
- 添加Agent C（剧情控制）
- 实现LangGraph状态图

Closes #123
```

### 代码审查（Code Review）

**原则**：
- 所有代码必须经过审查才能合并到`develop`
- 至少1人approve
- 通过所有CI测试

**审查清单**：
- [ ] 代码符合项目规范
- [ ] 功能实现正确
- [ ] 有足够的测试覆盖
- [ ] 无明显性能问题
- [ ] 无安全漏洞
- [ ] 文档已更新

**审查流程**：
1. 开发者创建Pull Request
2. 自动运行CI测试
3. 指定审查人员（Reviewer）
4. 审查人员提出意见或approve
5. 开发者修改
6. 合并到develop分支

---

## 📝 需求管理

### 需求文档模板

```markdown
# 需求标题

## 背景和目标
为什么需要这个功能？解决什么问题？

## 用户故事
作为[角色]，我想要[功能]，以便[价值]。

## 功能需求
1. 功能点1
2. 功能点2
3. 功能点3

## 非功能需求
- 性能：响应时间<500ms
- 安全：数据加密传输
- 可用性：99.9%正常运行时间

## 验收标准
- [ ] 标准1
- [ ] 标准2
- [ ] 标准3

## 原型/设计
[附上UI设计稿或原型链接]

## 技术实现建议
[可选，技术方案建议]

## 优先级
P0（必须有）| P1（应该有）| P2（可以有）| P3（不急）

## 预计工期
X人天

## 依赖
依赖其他需求或资源
```

### 任务跟踪（Jira/GitHub Issues）

**任务状态流转**：
```
待办 (Backlog)
  ↓
进行中 (In Progress)
  ↓
代码审查 (In Review)
  ↓
测试中 (In Testing)
  ↓
已完成 (Done)
```

**任务优先级**：
- 🔴 **P0（Critical）**：阻塞性Bug，必须立即修复
- 🟠 **P1（High）**：核心功能，本Sprint必须完成
- 🟡 **P2（Medium）**：重要功能，下个Sprint完成
- 🟢 **P3（Low）**：优化改进，有时间就做

---

## 🔧 开发环境

### 统一开发环境

**后端**：
- Python 3.10+
- Poetry或virtualenv管理依赖
- VS Code + Python插件

**前端**：
- Node.js 18+
- npm或pnpm管理依赖
- VS Code + ESLint + Prettier

**数据库**：
- Docker Compose统一管理
- 本地开发用Docker，避免环境差异

### VS Code推荐插件

**后端开发**：
- Python (Microsoft)
- Pylance
- Python Docstring Generator
- GitLens

**前端开发**：
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Auto Import

### 环境变量管理

**原则**：
- 敏感信息（API密钥）不提交到Git
- 使用`.env.example`作为模板
- 每个开发者维护自己的`.env`文件

**示例**：
```bash
# 复制模板
cp .env.example .env

# 编辑自己的配置
# .env
OPENAI_API_KEY=sk-your-key-here
```

---

## 🧪 测试策略

### 测试金字塔

```
        E2E测试（10%）
           ↑
      集成测试（30%）
           ↑
     单元测试（60%）
```

### 测试分工

| 测试类型 | 负责人 | 工具 |
|---------|--------|------|
| 单元测试 | 功能开发者本人 | pytest, Jest |
| 集成测试 | 功能开发者本人 | pytest, Supertest |
| E2E测试 | QA或前端开发 | Playwright, Cypress |

### 测试覆盖率要求

- **核心服务**：≥90%（agent_service, rag_service）
- **API路由**：≥80%
- **工具函数**：≥80%
- **整体项目**：≥70%

### 测试规范

**命名规范**：
```python
# 后端测试
def test_agent_service_generate_content_success():
    """测试Agent服务生成内容 - 成功场景"""
    pass

def test_agent_service_generate_content_with_invalid_input():
    """测试Agent服务生成内容 - 无效输入"""
    pass
```

**测试结构（AAA模式）**：
```python
def test_example():
    # Arrange（准备）
    service = MyService()
    input_data = {"key": "value"}

    # Act（执行）
    result = service.do_something(input_data)

    # Assert（断言）
    assert result["status"] == "success"
```

---

## 📚 文档规范

### API文档

**使用OpenAPI（Swagger）**：
- FastAPI自动生成文档：`http://localhost:8000/docs`
- 所有接口必须有详细描述
- 参数和返回值必须有类型注解

**示例**：
```python
@router.post(
    "/novels",
    response_model=NovelResponse,
    summary="创建小说",
    description="创建一个新的小说项目，需要提供标题、类型和简介"
)
async def create_novel(
    novel: NovelCreate,
    user: User = Depends(get_current_user)
):
    """
    创建小说接口

    Args:
        novel: 小说创建数据
        user: 当前登录用户

    Returns:
        NovelResponse: 创建的小说信息

    Raises:
        HTTPException: 创建失败时抛出
    """
    pass
```

### 代码注释

**Python（使用Google风格）**：
```python
def generate_content(prompt: str, novel_id: int) -> GenerationResponse:
    """
    生成小说内容

    使用三Agent协作工作流生成高质量小说段落。

    Args:
        prompt: 剧情提示词
        novel_id: 小说ID

    Returns:
        GenerationResponse: 生成结果，包含最终内容和各Agent输出

    Raises:
        ValueError: 如果prompt为空
        APIError: 如果LLM API调用失败

    Examples:
        >>> response = generate_content("主角遇到敌人", 1)
        >>> print(response.final_content)
    """
    pass
```

**TypeScript（使用JSDoc）**：
```typescript
/**
 * 生成小说内容
 *
 * @param prompt - 剧情提示词
 * @param novelId - 小说ID
 * @returns 生成结果
 * @throws {Error} 如果API调用失败
 *
 * @example
 * ```ts
 * const result = await generateContent("主角遇到敌人", 1);
 * console.log(result.finalContent);
 * ```
 */
async function generateContent(
  prompt: string,
  novelId: number
): Promise<GenerationResponse> {
  // ...
}
```

### README文档

每个主要模块应该有README：
- `backend/README.md` - 后端架构、运行方式
- `frontend/README.md` - 前端架构、组件说明
- `docs/API.md` - API接口文档
- `docs/ARCHITECTURE.md` - 系统架构文档

---

## 💬 沟通协作

### 沟通渠道

| 场景 | 渠道 | 响应时间 |
|-----|------|---------|
| 紧急问题（阻塞开发） | 电话/即时通讯 | 立即 |
| 日常问题 | Slack/钉钉 | 1小时内 |
| 需求讨论 | 会议/文档 | 1天内 |
| Bug报告 | GitHub Issues | 1天内 |
| 技术方案讨论 | 文档+会议 | 2天内 |

### Slack/钉钉频道

- `#general` - 全体公告
- `#backend` - 后端技术讨论
- `#frontend` - 前端技术讨论
- `#design` - UI/UX设计讨论
- `#random` - 闲聊（团建、段子）
- `#cicd` - CI/CD通知（自动消息）

### 会议规范

**高效会议原则**：
- 提前发送会议议程
- 准时开始，准时结束
- 指定记录人，会后发送纪要
- 明确行动项（Action Items）和负责人

**会议类型**：
- **每日站会**：15分钟，同步进度
- **技术评审会**：1小时，评审技术方案
- **需求评审会**：1-2小时，确认需求细节
- **Sprint回顾会**：1小时，总结和改进

---

## 🚀 持续集成/持续部署（CI/CD）

### GitHub Actions工作流

**后端CI**（`.github/workflows/backend-ci.yml`）：
```yaml
name: Backend CI

on:
  push:
    branches: [develop, main]
    paths:
      - 'backend/**'
  pull_request:
    branches: [develop]

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

      - name: Run linting
        run: |
          cd backend
          pylint app/

      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**前端CI**（`.github/workflows/frontend-ci.yml`）：
```yaml
name: Frontend CI

on:
  push:
    branches: [develop, main]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm install

      - name: Run linting
        run: |
          cd frontend
          npm run lint

      - name: Run tests
        run: |
          cd frontend
          npm run test

      - name: Build
        run: |
          cd frontend
          npm run build
```

### 部署流程

```
开发完成
  ↓
提交PR并通过CI
  ↓
代码审查并合并到develop
  ↓
部署到测试环境（Staging）
  ↓
QA测试
  ↓
合并到main分支
  ↓
部署到生产环境（Production）
```

---

## 🎯 最佳实践

### 代码质量

1. **DRY原则**：不要重复自己（Don't Repeat Yourself）
   - 提取公共逻辑为函数/组件
   - 使用配置文件管理常量

2. **单一职责**：每个函数/类只做一件事
   - 函数长度<50行
   - 类的方法数<10个

3. **命名规范**：清晰表意
   - 函数：动词+名词（`getUserById`）
   - 变量：名词（`userName`, `novelList`）
   - 常量：大写下划线（`MAX_RETRY_COUNT`）

### 性能优化

1. **后端**：
   - 使用数据库索引
   - 实现LLM响应缓存
   - 异步处理耗时任务（Celery）

2. **前端**：
   - 使用SWR缓存API响应
   - 实现虚拟滚动（长列表）
   - 懒加载图片和组件

### 安全实践

1. **输入验证**：所有用户输入必须验证
2. **SQL注入防护**：使用ORM，避免拼接SQL
3. **XSS防护**：前端对输出进行转义
4. **CSRF防护**：使用CSRF Token
5. **密码加密**：使用bcrypt，不存储明文

---

## 📊 项目指标

### 开发指标

| 指标 | 目标 | 当前值 | 趋势 |
|-----|------|--------|------|
| 代码覆盖率 | ≥80% | - | - |
| Bug数量 | <10个/周 | - | - |
| PR平均审查时间 | <24小时 | - | - |
| CI构建时间 | <5分钟 | - | - |

### 质量指标

| 指标 | 目标 |
|-----|------|
| API响应时间（P95） | <500ms |
| 前端首屏加载时间 | <3s |
| Lighthouse性能分数 | >90 |
| 用户满意度 | >4.5/5 |

---

## 🆘 问题升级机制

### 问题级别

| 级别 | 定义 | 响应时间 | 处理方式 |
|-----|------|---------|---------|
| P0 | 系统崩溃、数据丢失 | 立即 | 全员参与 |
| P1 | 核心功能不可用 | 2小时内 | 相关开发者处理 |
| P2 | 次要功能故障 | 1天内 | 排期修复 |
| P3 | 体验问题、优化建议 | 1周内 | 规划到Sprint |

### 升级流程

```
发现问题
  ↓
自行尝试解决（30分钟）
  ↓ 失败
向团队成员求助（Slack）
  ↓ 1小时后仍未解决
升级到技术负责人
  ↓ 2小时后仍未解决
升级到项目经理
```

---

## 🎉 团队建设

### 代码分享会（每两周一次）

- 分享有趣的技术发现
- 讨论遇到的技术难题和解决方案
- Demo创新功能

### 技术学习

- 每人每月1天学习时间
- 报销技术书籍费用
- 鼓励参加技术会议

### 团队活动

- 每月一次团建活动
- 项目里程碑庆祝

---

**良好的协作是成功的基石！** 🤝
