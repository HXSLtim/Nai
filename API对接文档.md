# AI小说创作系统 - 前后端API对接文档

**版本**: v0.1.0
**更新时间**: 2025-11-14
**后端地址**: http://localhost:8000
**API文档**: http://localhost:8000/docs

---

## 目录

1. [认证系统](#认证系统)
2. [小说管理](#小说管理)
3. [章节管理](#章节管理)
4. [通用说明](#通用说明)

---

## 通用说明

### 基础URL

```
http://localhost:8000/api
```

### 认证方式

所有需要认证的接口使用**Bearer Token**方式：

```http
Authorization: Bearer <access_token>
```

### HTTP状态码

- `200` - 成功
- `201` - 创建成功
- `204` - 删除成功（无返回内容）
- `400` - 请求参数错误
- `401` - 未认证或Token无效
- `403` - 无权限访问
- `404` - 资源不存在
- `500` - 服务器错误

### 响应格式

所有API返回JSON格式数据。

---

## 认证系统

### 1. 用户注册

**接口**: `POST /api/auth/register`

**请求头**: 无需认证

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "test123456"
}
```

**字段说明**:
- `username`: 用户名，3-50字符
- `email`: 邮箱地址
- `password`: 密码，6-50字符

**响应** (201):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2025-11-14T12:00:00"
  }
}
```

**前端示例**:
```javascript
const response = await fetch('http://localhost:8000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    email: 'test@example.com',
    password: 'test123456'
  })
});
const data = await response.json();
// 保存 data.access_token 到 localStorage
localStorage.setItem('token', data.access_token);
```

---

### 2. 用户登录

**接口**: `POST /api/auth/login`

**请求头**: 无需认证

**请求体**:
```json
{
  "username": "testuser",
  "password": "test123456"
}
```

**响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2025-11-14T12:00:00"
  }
}
```

**前端示例**:
```javascript
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    password: 'test123456'
  })
});
const data = await response.json();
localStorage.setItem('token', data.access_token);
```

---

### 3. 获取当前用户信息

**接口**: `GET /api/auth/me`

**请求头**: 需要认证

**响应** (200):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2025-11-14T12:00:00"
}
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const user = await response.json();
```

---

## 小说管理

### 1. 创建小说

**接口**: `POST /api/novels/`

**请求头**: 需要认证

**请求体**:
```json
{
  "title": "修仙之路",
  "genre": "玄幻",
  "description": "一个关于少年修仙的故事",
  "worldview": "修仙世界，分为炼气、筑基、金丹、元婴等境界"
}
```

**字段说明**:
- `title`: 小说标题，必填，1-200字符
- `genre`: 小说类型，可选，最多50字符
- `description`: 小说简介，可选
- `worldview`: 世界观设定，可选

**响应** (201):
```json
{
  "id": 1,
  "title": "修仙之路",
  "genre": "玄幻",
  "description": "一个关于少年修仙的故事",
  "worldview": "修仙世界，分为炼气、筑基、金丹、元婴等境界",
  "user_id": 1,
  "created_at": "2025-11-14T12:00:00",
  "updated_at": "2025-11-14T12:00:00"
}
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/api/novels/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: '修仙之路',
    genre: '玄幻',
    description: '一个关于少年修仙的故事',
    worldview: '修仙世界，分为炼气、筑基、金丹、元婴等境界'
  })
});
const novel = await response.json();
```

---

### 2. 获取用户的所有小说

**接口**: `GET /api/novels/`

**请求头**: 需要认证

**查询参数**:
- `skip`: 跳过条数，默认0
- `limit`: 返回条数限制，默认100

**响应** (200):
```json
[
  {
    "id": 1,
    "title": "修仙之路",
    "genre": "玄幻",
    "description": "一个关于少年修仙的故事",
    "worldview": "修仙世界，分为炼气、筑基、金丹、元婴等境界",
    "user_id": 1,
    "created_at": "2025-11-14T12:00:00",
    "updated_at": "2025-11-14T12:00:00"
  }
]
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/api/novels/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const novels = await response.json();
```

---

### 3. 获取单个小说详情

**接口**: `GET /api/novels/{novel_id}`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID

**响应** (200):
```json
{
  "id": 1,
  "title": "修仙之路",
  "genre": "玄幻",
  "description": "一个关于少年修仙的故事",
  "worldview": "修仙世界，分为炼气、筑基、金丹、元婴等境界",
  "user_id": 1,
  "created_at": "2025-11-14T12:00:00",
  "updated_at": "2025-11-14T12:00:00"
}
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
const response = await fetch(`http://localhost:8000/api/novels/${novelId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const novel = await response.json();
```

---

### 4. 更新小说信息

**接口**: `PUT /api/novels/{novel_id}`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID

**请求体** (所有字段可选):
```json
{
  "title": "新标题",
  "genre": "新类型",
  "description": "新简介",
  "worldview": "新世界观"
}
```

**响应** (200):
```json
{
  "id": 1,
  "title": "新标题",
  "genre": "新类型",
  "description": "新简介",
  "worldview": "新世界观",
  "user_id": 1,
  "created_at": "2025-11-14T12:00:00",
  "updated_at": "2025-11-14T12:10:00"
}
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
const response = await fetch(`http://localhost:8000/api/novels/${novelId}`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: '新标题',
    description: '新简介'
  })
});
const updatedNovel = await response.json();
```

---

### 5. 删除小说

**接口**: `DELETE /api/novels/{novel_id}`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID

**注意**: 删除小说会级联删除所有章节

**响应** (204): 无返回内容

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
await fetch(`http://localhost:8000/api/novels/${novelId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
// 删除成功，无返回数据
```

---

## 章节管理

### 1. 创建章节

**接口**: `POST /api/novels/{novel_id}/chapters`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID

**请求体**:
```json
{
  "chapter_number": 1,
  "title": "第一章 初入修仙界",
  "content": "李明是一个十六岁的少年，生活在青云镇。在一次偶然的机会下，他发现了一枚古老的玉佩，从此踏上了修仙之路..."
}
```

**字段说明**:
- `chapter_number`: 章节号，必填，大于0
- `title`: 章节标题，必填，1-200字符
- `content`: 章节内容，必填

**响应** (201):
```json
{
  "id": 1,
  "novel_id": 1,
  "chapter_number": 1,
  "title": "第一章 初入修仙界",
  "content": "李明是一个十六岁的少年，生活在青云镇。在一次偶然的机会下，他发现了一枚古老的玉佩，从此踏上了修仙之路...",
  "word_count": 53,
  "created_at": "2025-11-14T12:00:00",
  "updated_at": "2025-11-14T12:00:00"
}
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
const response = await fetch(`http://localhost:8000/api/novels/${novelId}/chapters`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    chapter_number: 1,
    title: '第一章 初入修仙界',
    content: '李明是一个十六岁的少年...'
  })
});
const chapter = await response.json();
```

---

### 2. 获取小说的所有章节

**接口**: `GET /api/novels/{novel_id}/chapters`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID

**查询参数**:
- `skip`: 跳过条数，默认0
- `limit`: 返回条数限制，默认100

**响应** (200):
```json
[
  {
    "id": 1,
    "novel_id": 1,
    "chapter_number": 1,
    "title": "第一章 初入修仙界",
    "content": "李明是一个十六岁的少年，生活在青云镇。在一次偶然的机会下，他发现了一枚古老的玉佩，从此踏上了修仙之路...",
    "word_count": 53,
    "created_at": "2025-11-14T12:00:00",
    "updated_at": "2025-11-14T12:00:00"
  }
]
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
const response = await fetch(`http://localhost:8000/api/novels/${novelId}/chapters`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const chapters = await response.json();
```

---

### 3. 获取单个章节详情

**接口**: `GET /api/novels/{novel_id}/chapters/{chapter_id}`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID
- `chapter_id`: 章节ID

**响应** (200):
```json
{
  "id": 1,
  "novel_id": 1,
  "chapter_number": 1,
  "title": "第一章 初入修仙界",
  "content": "李明是一个十六岁的少年，生活在青云镇。在一次偶然的机会下，他发现了一枚古老的玉佩，从此踏上了修仙之路...",
  "word_count": 53,
  "created_at": "2025-11-14T12:00:00",
  "updated_at": "2025-11-14T12:00:00"
}
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
const chapterId = 1;
const response = await fetch(`http://localhost:8000/api/novels/${novelId}/chapters/${chapterId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const chapter = await response.json();
```

---

### 4. 更新章节

**接口**: `PUT /api/novels/{novel_id}/chapters/{chapter_id}`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID
- `chapter_id`: 章节ID

**请求体** (所有字段可选):
```json
{
  "title": "新标题",
  "content": "新内容"
}
```

**响应** (200):
```json
{
  "id": 1,
  "novel_id": 1,
  "chapter_number": 1,
  "title": "新标题",
  "content": "新内容",
  "word_count": 78,
  "created_at": "2025-11-14T12:00:00",
  "updated_at": "2025-11-14T12:10:00"
}
```

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
const chapterId = 1;
const response = await fetch(`http://localhost:8000/api/novels/${novelId}/chapters/${chapterId}`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: '更新后的章节内容...'
  })
});
const updatedChapter = await response.json();
```

---

### 5. 删除章节

**接口**: `DELETE /api/novels/{novel_id}/chapters/{chapter_id}`

**请求头**: 需要认证

**路径参数**:
- `novel_id`: 小说ID
- `chapter_id`: 章节ID

**响应** (204): 无返回内容

**前端示例**:
```javascript
const token = localStorage.getItem('token');
const novelId = 1;
const chapterId = 1;
await fetch(`http://localhost:8000/api/novels/${novelId}/chapters/${chapterId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
// 删除成功，无返回数据
```

---

## 完整的前端集成示例

### React + TypeScript示例

```typescript
// types.ts
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface Novel {
  id: number;
  title: string;
  genre?: string;
  description?: string;
  worldview?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface Chapter {
  id: number;
  novel_id: number;
  chapter_number: number;
  title: string;
  content: string;
  word_count: number;
  created_at: string;
  updated_at?: string;
}

// api.ts
const API_BASE = 'http://localhost:8000/api';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

export const api = {
  // 认证
  async register(username: string, email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    return res.json();
  },

  async login(username: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return res.json();
  },

  // 小说
  async getNovels(): Promise<Novel[]> {
    const res = await fetch(`${API_BASE}/novels/`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async createNovel(data: Partial<Novel>): Promise<Novel> {
    const res = await fetch(`${API_BASE}/novels/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  },

  // 章节
  async getChapters(novelId: number): Promise<Chapter[]> {
    const res = await fetch(`${API_BASE}/novels/${novelId}/chapters`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async createChapter(novelId: number, data: Partial<Chapter>): Promise<Chapter> {
    const res = await fetch(`${API_BASE}/novels/${novelId}/chapters`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return res.json();
  }
};
```

---

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误

| 状态码 | 错误信息 | 说明 |
|--------|----------|------|
| 401 | "无效的认证令牌" | Token过期或无效 |
| 403 | "无权访问此小说" | 试图访问其他用户的小说 |
| 404 | "小说不存在" | 小说ID不存在 |
| 400 | "章节 1 已存在" | 章节号重复 |

---

## 测试建议

1. 使用Postman或Insomnia测试API
2. 在浏览器访问 http://localhost:8000/docs 查看交互式API文档
3. 查看 `backend/test_novel_api.py` 获取完整的Python测试示例

---

## 下一步开发建议

### 前端团队：

1. **认证流程**
   - 实现登录/注册页面
   - 实现Token存储和自动刷新
   - 实现路由守卫（未登录重定向）

2. **小说管理页面**
   - 小说列表页（展示所有小说）
   - 小说详情页（查看/编辑小说信息）
   - 创建小说表单

3. **章节管理页面**
   - 章节列表页（展示小说所有章节）
   - 章节编辑器（Markdown或富文本编辑器）
   - 章节预览功能

### 后端团队（已完成）：

- ✅ 用户认证API
- ✅ 小说CRUD API
- ✅ 章节CRUD API
- ✅ RAG检索系统（Chroma + HuggingFace）
- ⏳ 待开发：AI生成API (generation.router)

---

**联系方式**: 如有API问题，请查看 http://localhost:8000/docs 或联系后端开发团队
