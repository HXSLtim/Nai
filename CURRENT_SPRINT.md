# 当前Sprint执行计划

**Sprint周期**：Week 1-2（2周，10个工作日）
**Sprint目标**：前端基础框架 + 用户认证 + 小说管理
**开始日期**：2025-11-14
**结束日期**：2025-11-28

---

## 📊 团队配置与状态

| 角色 | 代号 | 状态 | 主要职责 | 本Sprint工作量 |
|------|------|------|----------|----------------|
| 后端开发A | **BE-A** | ✅ 已完成 | 核心架构、多Agent系统 | 0天（指导答疑） |
| 前端开发A | **FE-A** | 🔴 急需 | Next.js基础、小说管理页 | 10天（满负荷） |
| 前端开发B | **FE-B** | 🔴 急需 | 角色管理、协助联调 | 10天（满负荷） |
| UI/UX设计师 | **UI** | 🟡 需要 | 设计规范、组件库 | 10天（满负荷） |
| 后端开发C | **BE-C** | 🟡 需要 | 用户认证、章节管理 | 10天（满负荷） |

---

## 🎯 Sprint里程碑

| 里程碑 | 截止日期 | 负责人 | 验收标准 | 状态 |
|--------|----------|--------|----------|------|
| **M1.1: 前端项目初始化** | Day 2 (11-15) | FE-A + UI | Next.js可运行，TailwindCSS配置完成 | 🔴 待开始 |
| **M1.2: 用户认证后端** | Day 5 (11-20) | BE-C | 注册/登录API可用 | 🔴 待开始 |
| **M1.3: 小说管理前端** | Day 7 (11-22) | FE-A | 列表、创建、详情可用 | 🔴 待开始 |
| **M1.4: 角色管理前端** | Day 7 (11-22) | FE-B | 角色列表、创建可用 | 🔴 待开始 |
| **M1.5: 前后端联调** | Day 10 (11-28) | All | 完整流程打通 | 🔴 待开始 |

---

## 📋 详细任务分配

### 👨‍💻 前端开发A（FE-A）- 核心前端开发

**技能要求**：React, Next.js 14+, TypeScript, TailwindCSS

#### Day 1-2：项目初始化（2天）

**任务清单**：
- [ ] 创建Next.js 14项目（App Router）
  ```bash
  npx create-next-app@latest frontend --typescript --tailwind --app
  ```
- [ ] 配置TypeScript严格模式
- [ ] 配置ESLint + Prettier
- [ ] 配置环境变量（`.env.local`）
- [ ] 创建项目基础目录结构：
  ```
  frontend/
  ├── app/
  │   ├── (auth)/          # 认证相关页面
  │   ├── (dashboard)/     # 主应用页面
  │   └── api/             # API路由（如需要）
  ├── components/
  │   ├── ui/              # 基础UI组件
  │   ├── layout/          # 布局组件
  │   └── features/        # 功能组件
  ├── lib/
  │   ├── api.ts           # API封装
  │   ├── auth.ts          # 认证逻辑
  │   └── utils.ts         # 工具函数
  └── types/               # TypeScript类型定义
  ```

**交付物**：
- 可运行的Next.js项目
- 代码规范配置文件
- README.md（本地开发指南）

**检查点**：
- `npm run dev` 可启动项目
- `npm run lint` 无错误
- 与UI设计师确认TailwindCSS配置

---

#### Day 2-3：全局布局和导航（1天）

**任务清单**：
- [ ] 创建全局布局组件 `components/layout/AppLayout.tsx`
  - 顶部导航栏
  - 侧边栏菜单
  - 面包屑导航
- [ ] 创建路由导航配置 `lib/navigation.ts`
- [ ] 集成UI设计师提供的设计规范

**交付物**：
- 响应式布局组件
- 可折叠侧边栏
- 路由高亮显示

**检查点**：
- 移动端/桌面端布局正常
- 与UI设计师确认设计一致性

---

#### Day 3-4：API封装（1天）

**任务清单**：
- [ ] 创建API客户端 `lib/api.ts`
  ```typescript
  // 示例结构
  class APIClient {
    private baseURL: string;
    private token: string | null;

    async get<T>(path: string): Promise<T>
    async post<T>(path: string, data: any): Promise<T>
    // ...
  }
  ```
- [ ] 封装常用API方法
- [ ] 错误处理和重试逻辑
- [ ] TypeScript类型定义 `types/api.ts`

**交付物**：
- 完整的API封装层
- TypeScript类型定义
- API使用文档

**检查点**：
- 可调用后端健康检查接口
- 错误处理符合预期

---

#### Day 4-6：小说列表页（2天）

**任务清单**：
- [ ] 创建小说列表页 `app/(dashboard)/novels/page.tsx`
- [ ] 小说卡片组件 `components/features/NovelCard.tsx`
- [ ] 搜索和过滤功能
- [ ] 分页组件
- [ ] 加载状态和空状态

**交付物**：
- 完整的小说列表页
- 搜索/过滤/分页功能
- 响应式设计

**检查点**：
- 可展示小说列表（先用Mock数据）
- 搜索和过滤交互正常

---

#### Day 6-8：创建小说页（2天）

**任务清单**：
- [ ] 创建小说表单页 `app/(dashboard)/novels/new/page.tsx`
- [ ] 表单验证（使用react-hook-form + zod）
- [ ] 提交逻辑和错误处理
- [ ] 成功后跳转到详情页

**交付物**：
- 完整的创建小说表单
- 表单验证
- 成功/失败提示

**检查点**：
- 表单验证符合预期
- 与UI设计师确认交互流程

---

#### Day 8-9：小说详情页（1天）

**任务清单**：
- [ ] 创建详情页 `app/(dashboard)/novels/[id]/page.tsx`
- [ ] 展示小说基本信息
- [ ] 操作按钮（编辑、删除、生成）
- [ ] Tab切换（章节、角色、世界观）

**交付物**：
- 完整的详情页
- Tab切换功能
- 操作按钮（暂不连接后端）

---

#### Day 9-10：登录/注册页（2天）

**任务清单**：
- [ ] 创建登录页 `app/(auth)/login/page.tsx`
- [ ] 创建注册页 `app/(auth)/register/page.tsx`
- [ ] JWT Token存储逻辑 `lib/auth.ts`
- [ ] Token自动刷新机制
- [ ] 路由守卫（保护私有页面）

**交付物**：
- 登录/注册页面
- JWT管理逻辑
- 路由权限控制

**检查点**：
- 与BE-C联调登录API
- Token刷新机制测试通过

---

### 👨‍💻 前端开发B（FE-B）- 角色管理 + 协助

**技能要求**：React, TypeScript, 可视化库（React Flow基础）

#### Day 1：环境搭建和熟悉（1天）

**任务清单**：
- [ ] 克隆FE-A搭建的前端项目
- [ ] 本地环境验证
- [ ] 熟悉项目结构和代码规范
- [ ] 学习FE-A封装的API层用法

**交付物**：
- 本地开发环境可运行
- 理解项目架构文档

---

#### Day 2-4：角色列表页（2天）

**任务清单**：
- [ ] 创建角色列表页 `app/(dashboard)/characters/page.tsx`
- [ ] 角色卡片组件 `components/features/CharacterCard.tsx`
  - 展示角色头像、名称、性格标签
  - 快速操作按钮
- [ ] 搜索和过滤功能
- [ ] 按小说ID过滤角色

**交付物**：
- 完整的角色列表页
- 角色卡片组件
- 搜索过滤功能

---

#### Day 4-6：角色创建表单（2天）

**任务清单**：
- [ ] 创建角色表单页 `app/(dashboard)/characters/new/page.tsx`
- [ ] 表单字段：
  - 基本信息（名称、性别、年龄）
  - 外貌描写
  - 性格标签
  - 背景故事
- [ ] 表单验证
- [ ] 提交逻辑

**交付物**：
- 完整的角色创建表单
- 表单验证
- 提交成功处理

---

#### Day 6-7：角色详情页（1天）

**任务清单**：
- [ ] 创建详情页 `app/(dashboard)/characters/[id]/page.tsx`
- [ ] 展示完整角色信息
- [ ] 编辑/删除按钮

**交付物**：
- 完整的角色详情页

---

#### Day 8-10：协助FE-A联调（2天）

**任务清单**：
- [ ] 协助FE-A联调登录/注册
- [ ] 统一前端风格和组件复用
- [ ] Bug修复
- [ ] 代码Review

**交付物**：
- 前端统一风格
- Bug清零

---

#### Day 9-10：学习React Flow（2天，可并行）

**任务清单**：
- [ ] 学习React Flow基础用法
- [ ] 创建简单Demo（节点 + 连线）
- [ ] 准备Week 3-4的关系图谱功能

**交付物**：
- React Flow Demo示例
- 学习笔记

---

### 🎨 UI/UX设计师（UI）- 设计规范 + 组件库

**技能要求**：Figma, TailwindCSS, 前端基础

#### Day 1-2：视觉设计规范（2天）

**任务清单**：
- [ ] 定义色彩系统
  - 主色（Primary）
  - 辅助色（Secondary）
  - 成功/警告/错误/信息色
  - 灰度色阶
- [ ] 定义字体系统
  - 标题字体
  - 正文字体
  - 代码字体
  - 字号阶梯
- [ ] 定义间距系统（4px基准）
- [ ] 定义圆角、阴影、边框规范

**交付物**：
- 设计规范文档（Figma或Markdown）
- TailwindCSS配置文件 `tailwind.config.js`

**检查点**：
- 与团队评审设计规范
- FE-A确认配置可用

---

#### Day 2-3：TailwindCSS配置（1天）

**任务清单**：
- [ ] 将设计规范转换为TailwindCSS配置
- [ ] 自定义颜色变量
- [ ] 自定义字体和间距
- [ ] 提供给FE-A集成

**交付物**：
- `tailwind.config.js`
- 设计Token文档

---

#### Day 3-6：基础组件库（3天）

**任务清单**：
- [ ] Button组件（多种变体）
  ```typescript
  <Button variant="primary|secondary|ghost" size="sm|md|lg">
  ```
- [ ] Input组件（文本、密码、搜索）
- [ ] Card组件
- [ ] Modal组件
- [ ] Toast通知组件
- [ ] Loading组件
- [ ] Empty空状态组件
- [ ] Badge徽章组件

**交付物**：
- 完整的基础组件库 `components/ui/`
- 组件使用文档
- Storybook（可选）

**检查点**：
- 组件可复用性高
- 与FE团队确认组件API

---

#### Day 6-8：小说管理页原型（2天）

**任务清单**：
- [ ] 小说列表页设计稿（Figma）
- [ ] 创建小说表单设计稿
- [ ] 小说详情页设计稿
- [ ] 交互流程说明

**交付物**：
- Figma设计稿（可点击原型）
- 交互说明文档

---

#### Day 8-10：内容生成页原型（2天）

**任务清单**：
- [ ] 内容生成配置界面设计
- [ ] 实时生成展示界面设计
- [ ] Agent状态可视化设计
- [ ] 结果展示和保存设计

**交付物**：
- Figma设计稿
- 为Week 3-4做准备

---

### 🔧 后端开发C（BE-C）- 用户认证 + 章节管理

**技能要求**：Python, FastAPI, PostgreSQL/SQLite, JWT

#### Day 1-2：User数据模型（1天）

**任务清单**：
- [ ] 创建User数据模型 `backend/app/models/user.py`
  ```python
  class User(Base):
      id: int
      username: str
      email: str
      hashed_password: str
      created_at: datetime
      is_active: bool
  ```
- [ ] 数据库迁移（如使用Alembic）
- [ ] 或直接用SQLite测试

**交付物**：
- User模型定义
- 数据库迁移脚本

---

#### Day 2-3：JWT认证逻辑（1天）

**任务清单**：
- [ ] 创建JWT工具函数 `backend/app/core/security.py`
  - `create_access_token()`
  - `verify_token()`
  - `hash_password()`
  - `verify_password()`
- [ ] 安装依赖：`python-jose`, `passlib`, `bcrypt`

**交付物**：
- JWT工具函数
- 单元测试

---

#### Day 3-5：注册/登录API（2天）

**任务清单**：
- [ ] 创建认证路由 `backend/app/api/routes/auth.py`
- [ ] `POST /api/auth/register` - 用户注册
- [ ] `POST /api/auth/login` - 用户登录
- [ ] `POST /api/auth/refresh` - Token刷新
- [ ] `GET /api/auth/me` - 获取当前用户信息
- [ ] 添加到主路由

**交付物**：
- 完整的认证API
- API文档（FastAPI自动生成）

**检查点**：
- Postman/curl测试通过
- 返回格式与前端约定一致

---

#### Day 5-6：权限依赖注入（1天）

**任务清单**：
- [ ] 创建依赖注入函数 `backend/app/api/dependencies.py`
  ```python
  async def get_current_user(token: str = Depends(oauth2_scheme)):
      # 验证Token，返回User对象

  async def require_admin(user: User = Depends(get_current_user)):
      # 验证管理员权限
  ```
- [ ] 文档说明如何在路由中使用

**交付物**：
- 权限依赖函数
- 使用示例

---

#### Day 6-8：保护现有API（2天）

**任务清单**：
- [ ] 在现有路由中添加权限保护
  ```python
  @router.post("/generate")
  async def generate_content(
      request: GenerationRequest,
      current_user: User = Depends(get_current_user)
  ):
      # ...
  ```
- [ ] 测试所有API需要认证

**交付物**：
- 所有API需要Token访问
- 测试报告

---

#### Day 8-10：前端集成联调（2天）

**任务清单**：
- [ ] 与FE-A联调登录/注册流程
- [ ] 调试Token刷新机制
- [ ] 解决CORS问题（如有）
- [ ] 错误处理优化

**交付物**：
- 登录流程完全打通
- 前后端联调测试通过

**检查点**：
- 前端可成功注册、登录
- Token刷新自动进行
- 退出登录正常

---

#### Day 7-10：章节管理API（可并行，3天）

**任务清单**：
- [ ] 创建Chapter数据模型 `backend/app/models/chapter.py`
  ```python
  class Chapter(Base):
      id: int
      novel_id: int
      chapter_number: int
      title: str
      content: str
      created_at: datetime
  ```
- [ ] 创建章节路由 `backend/app/api/routes/chapters.py`
- [ ] `GET /api/novels/{novel_id}/chapters` - 获取章节列表
- [ ] `POST /api/novels/{novel_id}/chapters` - 创建章节
- [ ] `GET /api/chapters/{id}` - 获取章节详情
- [ ] `PUT /api/chapters/{id}` - 更新章节
- [ ] `DELETE /api/chapters/{id}` - 删除章节

**交付物**：
- 完整的章节CRUD API
- 权限保护（仅作者可编辑）
- API文档

**检查点**：
- Postman测试通过
- 为Week 3-4前端集成做准备

---

## 🔄 协作流程

### 每日站会（Daily Standup）

**时间**：每天上午10:00
**时长**：15分钟
**参与者**：所有开发人员

**内容**：
1. 昨天完成了什么？
2. 今天计划做什么？
3. 有什么阻塞问题？

---

### 代码审查（Code Review）

**规则**：
- 所有代码必须经过至少1人审查才能合并
- 前端代码：FE-A ↔ FE-B 互相审查
- 后端代码：BE-C → BE-A 审查
- UI组件：UI → FE-A/FE-B 审查

**检查点**：
- 代码符合规范（ESLint/Pylint）
- 有适当注释
- 功能测试通过

---

### Git协作规范

**分支策略**：
```
main（受保护）
  ├── develop（开发分支）
  │   ├── feature/fe-novels-list（FE-A）
  │   ├── feature/fe-characters（FE-B）
  │   ├── feature/be-auth（BE-C）
  │   └── feature/ui-components（UI）
```

**提交规范**：
```
feat: 新功能
fix: 修复Bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/配置
```

**示例**：
```bash
git commit -m "feat(novels): 添加小说列表页"
git commit -m "fix(auth): 修复Token刷新逻辑"
```

---

### API契约（API Contract）

**前后端约定**：
- 所有API遵循RESTful规范
- 响应格式统一：
  ```json
  {
    "data": { ... },
    "message": "成功",
    "code": 200
  }
  ```
- 错误响应格式：
  ```json
  {
    "detail": "错误描述",
    "code": 400
  }
  ```

**文档地址**：
- 后端API文档：http://localhost:8000/docs
- 前端组件文档：（待Storybook部署）

---

## 📞 沟通渠道

### 技术问题升级流程

1. **自行解决**（30分钟内）
2. **Slack/钉钉求助**（1小时内）
3. **升级到技术负责人**（2小时内）
   - 前端问题 → FE-A（如已入职）
   - 后端问题 → BE-A
4. **升级到项目经理**（4小时内）

### 设计评审流程

1. UI设计师完成设计稿 → Slack通知
2. 团队成员48小时内提供反馈
3. 设计师修改 → 最终确认
4. 交付给FE团队实现

---

## ✅ Sprint验收标准

### M1.1: 前端项目初始化（Day 2）

**验收人**：项目经理 + FE-A
**验收标准**：
- [ ] `npm run dev` 可启动项目
- [ ] TailwindCSS配置生效
- [ ] ESLint/Prettier配置正确
- [ ] 基础布局可见

---

### M1.2: 用户认证后端（Day 5）

**验收人**：BE-A + FE-A
**验收标准**：
- [ ] 注册API可用（Postman测试）
- [ ] 登录API返回有效Token
- [ ] Token验证逻辑正确
- [ ] 密码哈希安全

---

### M1.3: 小说管理前端（Day 7）

**验收人**：FE-A + UI
**验收标准**：
- [ ] 小说列表可展示（Mock数据）
- [ ] 创建表单验证正常
- [ ] 详情页可展示
- [ ] 响应式布局正常

---

### M1.4: 角色管理前端（Day 7）

**验收人**：FE-B + UI
**验收标准**：
- [ ] 角色列表可展示
- [ ] 创建表单可用
- [ ] 详情页可展示

---

### M1.5: 前后端联调（Day 10）

**验收人**：全体成员
**验收标准**：
- [ ] 用户可注册、登录
- [ ] 登录后可访问受保护页面
- [ ] Token刷新自动进行
- [ ] 小说CRUD联调通过（如后端完成）
- [ ] 无阻塞性Bug

---

## 🎯 成功指标

**技术指标**：
- 代码覆盖率 ≥ 60%（后端）
- ESLint错误数 = 0
- TypeScript类型错误 = 0
- API响应时间 < 500ms

**交付指标**：
- 所有5个里程碑按时完成
- 严重Bug数 = 0
- 中等Bug数 ≤ 3

**协作指标**：
- 每日站会出席率 ≥ 90%
- 代码审查响应时间 ≤ 4小时
- 任务完成率 ≥ 90%

---

## 📚 开发资源

### 后端资源

- FastAPI文档：https://fastapi.tiangolo.com/
- Pydantic文档：https://docs.pydantic.dev/
- JWT认证指南：https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

### 前端资源

- Next.js 14文档：https://nextjs.org/docs
- TailwindCSS：https://tailwindcss.com/docs
- React Hook Form：https://react-hook-form.com/
- Zod验证：https://zod.dev/

### 设计资源

- TailwindCSS UI库参考：
  - Shadcn UI：https://ui.shadcn.com/
  - Headless UI：https://headlessui.com/
  - DaisyUI：https://daisyui.com/

---

## 🚨 风险管理

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 前端人员未到位 | 高 | 高 | 调整Sprint范围，BE-C可先完成更多后端API |
| 设计稿延期 | 中 | 中 | FE团队先用Shadcn UI库快速开发 |
| 技术难点卡壳 | 中 | 中 | BE-A提供技术指导，必要时调整方案 |
| 联调时间不足 | 中 | 高 | 每天预留1小时联调时间，提前Mock数据 |

---

## 📝 备注

1. **优先级调整**：如前端人员未到位，BE-C可优先完成：
   - 章节管理API
   - 小说CRUD API
   - 角色管理API

2. **设计灵活性**：如UI设计师暂时缺位，FE团队可：
   - 使用Shadcn UI库快速搭建
   - 参考成熟产品（如Notion、语雀）
   - 后续优化设计

3. **测试策略**：
   - 后端：使用pytest编写单元测试
   - 前端：先手动测试，后续引入Jest/Playwright

---

**文档版本**：v1.0
**最后更新**：2025-11-14
**负责人**：BE-A（后端架构师）
**审核人**：项目经理
