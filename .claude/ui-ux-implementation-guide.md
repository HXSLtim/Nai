## UI/UX流程改进 - 实施指南

**制定日期**：2025-11-14
**适用范围**：前端代码改动
**预计工期**：2-3周
**技术栈**：Next.js + TypeScript + Material-UI v5

---

## 🎯 总体目标

1. **移除冗余按钮** - 统一UI元素，减少用户混淆
2. **补充缺失功能** - 完善用户工作流
3. **优化布局和流程** - 降低用户操作成本
4. **提升可用性** - 使关键功能易于发现

---

## 📋 任务清单

### 阶段1：删除冗余按钮（2-3天）

#### Task 1.1：移除dashboard对话框中的"AI续写"

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\dashboard\page.tsx`

**当前代码**（第500-530行）：
```typescript
<DialogActions sx={{ justifyContent: 'space-between' }}>
  <Box>
    <Button
      startIcon={<AutoFixHighIcon />}
      onClick={async () => {
        // AI续写逻辑...
      }}
      disabled={aiGenerating || !chapterForm.content}
    >
      {aiGenerating ? 'AI创作中...' : 'AI续写'}
    </Button>
  </Box>
  <Box>
    <Button onClick={() => setOpenDialog(false)}>取消</Button>
    <Button
      onClick={handleSaveChapter}
      variant="contained"
      disabled={!chapterForm.title || !chapterForm.content}
    >
      创建
    </Button>
  </Box>
</DialogActions>
```

**改为**：
```typescript
<DialogActions>
  <Button onClick={() => setOpenDialog(false)}>取消</Button>
  <Button
    onClick={handleSaveNovel}
    variant="contained"
    disabled={!novelForm.title}
  >
    {editingNovel ? '保存' : '创建'}
  </Button>
</DialogActions>
```

**需删除的状态**：
- `aiGenerating` 状态（与此对话框无关）
- `handleAiContinue` 函数调用

**验证方式**：
```typescript
// 对话框打开时应该只有"取消"和"创建/保存"两个按钮
const dialogActionButtons = document.querySelectorAll('[role="dialog"] button');
console.assert(dialogActionButtons.length === 2, '应该只有2个按钮');
```

---

#### Task 1.2：移除novels/[id]对话框中的"AI续写"

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\novels\[id]\page.tsx`

**当前代码**（第501-542行）：
```typescript
<DialogActions sx={{ justifyContent: 'space-between' }}>
  <Box>
    <Button
      startIcon={<AutoFixHighIcon />}
      onClick={async () => {
        // AI续写逻辑...
      }}
      disabled={aiGenerating || !chapterForm.content}
    >
      {aiGenerating ? 'AI创作中...' : 'AI续写'}
    </Button>
  </Box>
  <Box>
    <Button onClick={() => setOpenDialog(false)}>取消</Button>
    <Button
      onClick={handleSaveChapter}
      variant="contained"
      disabled={!chapterForm.title || !chapterForm.content}
    >
      {editingChapter ? '保存' : '创建'}
    </Button>
  </Box>
</DialogActions>
```

**改为**：
```typescript
<DialogActions>
  <Button onClick={() => setOpenDialog(false)}>取消</Button>
  <Button
    onClick={handleSaveChapter}
    variant="contained"
    disabled={!chapterForm.title || !chapterForm.content}
  >
    {editingChapter ? '保存' : '创建'}
  </Button>
</DialogActions>
```

**需清理的代码**：
- 移除AI续写逻辑块（第504-530行）
- 移除`aiGenerating`和`setAiGenerating`（对此页面无用）

---

#### Task 1.3：改进Dashboard中"继续上次写作"的显示

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\dashboard\page.tsx`

**当前代码**（第257-266行）：
```typescript
<Button
  variant="outlined"
  disabled={!lastWorkspace}
  onClick={() => {
    if (!lastWorkspace) return;
    router.push(`/workspace?novel=${lastWorkspace.novelId}&chapter=${lastWorkspace.chapterId}`);
  }}
>
  继续上次写作
</Button>
```

**改为**（带有提示）：
```typescript
<Button
  variant="outlined"
  disabled={!lastWorkspace}
  onClick={() => {
    if (!lastWorkspace) return;
    router.push(`/workspace?novel=${lastWorkspace.novelId}&chapter=${lastWorkspace.chapterId}`);
  }}
  title={!lastWorkspace ? '暂无最近编辑的小说' : ''}
>
  继续上次写作
</Button>
```

**或改为**（更友好的提示）：
```typescript
{lastWorkspace ? (
  <Button
    variant="outlined"
    onClick={() => {
      router.push(`/workspace?novel=${lastWorkspace.novelId}&chapter=${lastWorkspace.chapterId}`);
    }}
  >
    继续上次写作
  </Button>
) : (
  <Typography variant="body2" color="text.secondary">
    暂无最近编辑的小说
  </Typography>
)}
```

---

### 阶段2：补充关键功能按钮（5-7天）

#### Task 2.1：工作台补充"撤销"按钮

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\workspace\page.tsx`

**步骤1**：导入图标
```typescript
import UndoIcon from '@mui/icons-material/Undo';
import { useRef } from 'react';
```

**步骤2**：补充历史栈状态
```typescript
// 添加到状态声明部分（第65-145行之间）
const [contentHistory, setContentHistory] = useState<string[]>([]);
const [historyIndex, setHistoryIndex] = useState(-1);
const contentInputRef = useRef<HTMLTextAreaElement | null>(null);
```

**步骤3**：实现撤销逻辑
```typescript
/**
 * 当内容变化时保存到历史栈
 */
useEffect(() => {
  if (!content) return;

  // 只在用户主动修改时记录（不记录AI生成）
  if (historyIndex >= 0 && contentHistory[historyIndex] === content) {
    return;
  }

  // 清除撤销点之后的历史
  const newHistory = contentHistory.slice(0, historyIndex + 1);
  newHistory.push(content);

  setContentHistory(newHistory);
  setHistoryIndex(newHistory.length - 1);
}, [content]);

/**
 * 撤销操作
 */
const handleUndo = () => {
  if (historyIndex <= 0) {
    setError('已经是最早版本');
    return;
  }

  const newIndex = historyIndex - 1;
  setHistoryIndex(newIndex);
  setContent(contentHistory[newIndex]);
};

/**
 * 重做操作（可选）
 */
const handleRedo = () => {
  if (historyIndex >= contentHistory.length - 1) {
    setError('已经是最新版本');
    return;
  }

  const newIndex = historyIndex + 1;
  setHistoryIndex(newIndex);
  setContent(contentHistory[newIndex]);
};
```

**步骤4**：在UI中添加撤销按钮

位置：工作台顶部工具栏，紧跟"返回"按钮后

```typescript
// 在AppBar的Toolbar中（第771-816行）
<IconButton
  color="inherit"
  onClick={() => router.push(`/novels/${novelId}`)}
>
  <ArrowBackIcon />
</IconButton>

{/* 新增撤销/重做按钮 */}
<IconButton
  color="inherit"
  onClick={handleUndo}
  disabled={historyIndex <= 0}
  title="撤销（Ctrl+Z）"
>
  <UndoIcon />
</IconButton>
<IconButton
  color="inherit"
  onClick={handleRedo}
  disabled={historyIndex >= contentHistory.length - 1}
  title="重做（Ctrl+Shift+Z）"
>
  <RedoIcon />
</IconButton>
```

**步骤5**：补充键盘快捷键

```typescript
// 在useEffect中添加键盘监听（第695-700行之后）
useEffect(() => {
  const handleKeyDown = (event: KeyboardEvent) => {
    // 保存快捷键
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault();
      if (!saving) handleSave();
    }

    // 撤销快捷键
    if ((event.ctrlKey || event.metaKey) && event.key === 'z') {
      event.preventDefault();
      if (historyIndex > 0) handleUndo();
    }

    // 重做快捷键
    if ((event.ctrlKey || event.metaKey) && (event.shiftKey || event.key === 'y')) {
      event.preventDefault();
      if (historyIndex < contentHistory.length - 1) handleRedo();
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [historyIndex, contentHistory, saving]);
```

**验证方式**：
```typescript
// 测试撤销功能
1. 在工作台输入文本
2. 点击撤销按钮，内容应回到上一步
3. 尝试Ctrl+Z快捷键
4. 当历史为空时，撤销按钮应禁用
```

---

#### Task 2.2：工作台补充"人物出场追踪"

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\workspace\page.tsx`

**步骤1**：补充状态
```typescript
// 在状态声明部分添加
const [charactersAppearance, setCharactersAppearance] = useState<
  {
    name: string;
    count: number;
    lines: number[];
  }[]
>([]);
```

**步骤2**：提取人物名单

首先需要从小说设定中提取已有的人物列表。根据代码，人物信息存储在`novel.worldview`中，需要解析格式：

```typescript
/**
 * 从世界观设定中提取人物列表
 */
const extractCharactersFromWorldview = (worldview: string): string[] => {
  // 寻找【主要角色】部分
  const match = worldview.match(/【主要角色】\n([\s\S]*?)(?=\n【|$)/);
  if (!match) return [];

  const lines = match[1].split('\n');
  return lines
    .map(line => {
      // 提取人物名（假设格式为"姓名：描述"）
      const nameMatch = line.match(/^([^：:]+)/);
      return nameMatch ? nameMatch[1].trim() : '';
    })
    .filter(name => name && name.length > 0);
};
```

**步骤3**：分析人物出场

```typescript
/**
 * 分析当前章节中的人物出场
 */
const analyzeCharacterAppearance = (
  chapterContent: string,
  characters: string[]
) => {
  const appearance: {
    name: string;
    count: number;
    lines: number[];
  }[] = [];

  const lines = chapterContent.split('\n');

  characters.forEach(character => {
    const count = chapterContent.split(character).length - 1;
    const appearanceLines: number[] = [];

    if (count > 0) {
      lines.forEach((line, idx) => {
        if (line.includes(character)) {
          appearanceLines.push(idx + 1);
        }
      });
    }

    if (count > 0) {
      appearance.push({
        name: character,
        count,
        lines: appearanceLines,
      });
    }
  });

  return appearance.sort((a, b) => b.count - a.count);
};
```

**步骤4**：在content变化时更新

```typescript
/**
 * 监听内容变化，更新人物出场信息
 */
useEffect(() => {
  if (!novel?.worldview || !content) {
    setCharactersAppearance([]);
    return;
  }

  const characters = extractCharactersFromWorldview(novel.worldview);
  if (characters.length === 0) {
    setCharactersAppearance([]);
    return;
  }

  const appearance = analyzeCharacterAppearance(content, characters);
  setCharactersAppearance(appearance);
}, [content, novel?.worldview]);
```

**步骤5**：在右侧面板显示

```typescript
// 在右侧面板中添加（在"AI续写"按钮下方）
{charactersAppearance.length > 0 && (
  <Card sx={{ mb: 2 }}>
    <CardContent>
      <Typography variant="subtitle2" gutterBottom>
        👥 人物出场追踪
      </Typography>
      <Divider sx={{ my: 1 }} />
      {charactersAppearance.map((char) => (
        <Box key={char.name} sx={{ mb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2">{char.name}</Typography>
            <Chip
              label={`${char.count}次`}
              size="small"
              variant="outlined"
              color={char.count > 5 ? 'primary' : 'default'}
            />
          </Box>
          <Typography variant="caption" color="text.secondary">
            第 {char.lines.join(', ')} 行
          </Typography>
        </Box>
      ))}
    </CardContent>
  </Card>
)}
```

**验证方式**：
```typescript
// 测试人物追踪
1. 在小说详情中设定人物（如"张三、李四、王五"）
2. 在工作台中输入含有这些人物名字的文本
3. 右侧面板应自动显示人物出场次数和所在行号
4. 出场最多的人物应排在最前
```

---

#### Task 2.3：补充段落格式化工具

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\workspace\page.tsx`

**步骤1**：导入图标
```typescript
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import SpaceBarIcon from '@mui/icons-material/SpaceBar';
```

**步骤2**：补充格式化函数

```typescript
/**
 * 格式化文本：统一段落间距、删除多余空行
 */
const formatParagraphs = (text: string): string => {
  // 1. 删除多余空行（超过2个连续空行改为2个）
  let formatted = text.replace(/\n\n\n+/g, '\n\n');

  // 2. 删除行尾多余空格
  formatted = formatted
    .split('\n')
    .map(line => line.trimEnd())
    .join('\n');

  // 3. 确保段落前后空行
  formatted = formatted
    .split(/\n\n+/)
    .map(para => para.trim())
    .filter(para => para.length > 0)
    .join('\n\n');

  return formatted;
};

/**
 * 删除不可见字符（零宽空格等）
 */
const cleanInvisibleChars = (text: string): string => {
  return text
    .replace(/\u200B/g, '') // 零宽空格
    .replace(/\u200C/g, '') // 零宽非连接符
    .replace(/\u200D/g, '') // 零宽连接符
    .replace(/\uFEFF/g, ''); // BOM
};

/**
 * 统一标点符号（可选，需谨慎）
 */
const normalizePunctuation = (text: string): string => {
  return text
    .replace(/，/g, '，') // 确保中文逗号
    .replace(/。/g, '。') // 确保中文句号
    .replace(/！/g, '！') // 确保中文感叹号
    .replace(/？/g, '？'); // 确保中文问号
};
```

**步骤3**：补充格式化按钮

```typescript
// 在章节内容标题旁添加（第950-980行之间）
<Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
  <Button
    size="small"
    variant="text"
    startIcon={<FormatListBulletedIcon />}
    onClick={() => {
      const formatted = formatParagraphs(content);
      setContent(formatted);
      setError('已清理段落格式');
    }}
    title="清理段落、删除多余空行"
  >
    清理格式
  </Button>

  <Button
    size="small"
    variant="text"
    startIcon={<SpaceBarIcon />}
    onClick={() => {
      const cleaned = cleanInvisibleChars(content);
      setContent(cleaned);
      setError('已删除不可见字符');
    }}
    title="删除零宽空格等不可见字符"
  >
    清理特殊符
  </Button>

  {/* 原有的改写方式选择保留 */}
  <FormControl size="small" sx={{ minWidth: 120 }}>
    <InputLabel>改写方式</InputLabel>
    <Select
      label="改写方式"
      value={rewriteType}
      onChange={(e) =>
        setRewriteType(e.target.value as 'polish' | 'rewrite' | 'shorten' | 'extend')
      }
    >
      <MenuItem value="polish">润色</MenuItem>
      <MenuItem value="rewrite">重写</MenuItem>
      <MenuItem value="shorten">压缩</MenuItem>
      <MenuItem value="extend">扩写</MenuItem>
    </Select>
  </FormControl>

  <Button
    size="small"
    variant="outlined"
    onClick={handleRewriteSelection}
    disabled={rewriteLoading || !selectedText}
  >
    {rewriteLoading ? 'AI改写中...' : 'AI改写选中'}
  </Button>
</Box>
```

**验证方式**：
```typescript
// 测试格式化
1. 粘贴含有多个空行的文本
2. 点击"清理格式"
3. 内容应该段落间距统一（最多2个空行）
4. 行尾应无多余空格
```

---

#### Task 2.4：Dashboard补充搜索框

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\dashboard\page.tsx`

**步骤1**：补充状态
```typescript
// 在状态声明部分添加
const [searchQuery, setSearchQuery] = useState('');
```

**步骤2**：实现搜索逻辑

```typescript
/**
 * 根据搜索词过滤小说
 */
const filteredNovels = novels.filter((novel) => {
  const query = searchQuery.toLowerCase();
  return (
    novel.title.toLowerCase().includes(query) ||
    novel.genre?.toLowerCase().includes(query) ||
    novel.description?.toLowerCase().includes(query)
  );
});
```

**步骤3**：在UI中添加搜索框

```typescript
// 在"我的小说"标题行之前添加（第272行之前）
<Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
  <TextField
    fullWidth
    placeholder="搜索小说... (标题、类型、简介)"
    value={searchQuery}
    onChange={(e) => setSearchQuery(e.target.value)}
    size="small"
    variant="outlined"
    InputProps={{
      startAdornment: (
        <InputAdornment position="start">
          <SearchIcon />
        </InputAdornment>
      ),
    }}
  />
</Box>

{/* 改为使用filteredNovels替代novels */}
{filteredNovels.length === 0 ? (
  <Box sx={{ textAlign: 'center', mt: 8 }}>
    <Typography variant="h6" color="text.secondary">
      {searchQuery ? '没有找到匹配的小说' : '还没有创建任何小说'}
    </Typography>
    {searchQuery && (
      <Button
        variant="text"
        onClick={() => setSearchQuery('')}
        sx={{ mt: 2 }}
      >
        清除搜索
      </Button>
    )}
  </Box>
) : (
  <Grid container spacing={3}>
    {filteredNovels.map((novel) => (
      // 现有的小说卡片代码
    ))}
  </Grid>
)}
```

**步骤4**：导入所需图标
```typescript
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
```

**验证方式**：
```typescript
// 测试搜索
1. 创建多部小说，标题/类型/简介各不相同
2. 在搜索框输入关键词
3. 列表应实时过滤
4. 清空搜索框应恢复全部显示
```

---

### 阶段3：优化布局（3-4天）

#### Task 3.1：小说详情补充进度条和统计

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\novels\[id]\page.tsx`

**步骤1**：在小说卡片补充统计信息

```typescript
// 在小说信息卡片中补充（第294-371行）

// 导入必要组件
import { LinearProgress, Grid, Box } from '@mui/material';

// 在CardContent中添加

<Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
  <Box>
    <Typography variant="h4" gutterBottom>
      {novel.title}
    </Typography>
    {novel.genre && (
      <Chip label={novel.genre} size="small" sx={{ mr: 1 }} />
    )}
    <Chip
      label={`${chapters.length} 章节`}
      size="small"
      color="primary"
      variant="outlined"
    />
  </Box>
  <Box>
    <Button
      variant="outlined"
      size="small"
      startIcon={<PsychologyIcon />}
      onClick={() => setInitDialogOpen(true)}
      sx={{ mr: 1 }}
    >
      AI初始化设定
    </Button>
    {/* 新增导出按钮 */}
    <Button
      variant="outlined"
      size="small"
      startIcon={<DownloadIcon />}
    >
      导出
    </Button>
  </Box>
</Box>

{/* 新增进度条和统计 */}
<Divider sx={{ my: 2 }} />
<Grid container spacing={2} sx={{ mt: 0 }}>
  <Grid item xs={12}>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
      <Typography variant="subtitle2">进度</Typography>
      <Typography variant="body2">
        {chapters.length}/10 章
      </Typography>
    </Box>
    <LinearProgress
      variant="determinate"
      value={(chapters.length / 10) * 100}
      sx={{ height: 8, borderRadius: 1 }}
    />
  </Grid>

  <Grid item xs={6} sm={3}>
    <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
      <Typography variant="body2" color="text.secondary">
        总字数
      </Typography>
      <Typography variant="h6">
        {chapters.reduce((sum, c) => sum + (c.word_count || 0), 0)}
      </Typography>
    </Paper>
  </Grid>

  <Grid item xs={6} sm={3}>
    <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
      <Typography variant="body2" color="text.secondary">
        平均章节
      </Typography>
      <Typography variant="h6">
        {chapters.length > 0
          ? Math.round(chapters.reduce((sum, c) => sum + (c.word_count || 0), 0) / chapters.length)
          : 0}
      </Typography>
    </Paper>
  </Grid>

  <Grid item xs={6} sm={3}>
    <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
      <Typography variant="body2" color="text.secondary">
        完成度
      </Typography>
      <Typography variant="h6">
        {((chapters.length / 10) * 100).toFixed(0)}%
      </Typography>
    </Paper>
  </Grid>

  <Grid item xs={6} sm={3}>
    <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
      <Typography variant="body2" color="text.secondary">
        已用时
      </Typography>
      <Typography variant="h6">
        {/* 根据创建时间计算 */}
        N天
      </Typography>
    </Paper>
  </Grid>
</Grid>
```

**步骤2**：导入必要图标
```typescript
import DownloadIcon from '@mui/icons-material/Download';
import { Paper, Grid } from '@mui/material';
```

**验证方式**：
```typescript
// 测试统计显示
1. 创建包含多个章节的小说
2. 应该显示进度条、总字数、平均章节、完成度
3. 添加新章节后，统计应自动更新
```

---

#### Task 3.2：优化右侧面板布局

**文件**：`C:\Users\a2778\Desktop\code\Nai\frontend\app\workspace\page.tsx`

当前右侧面板的顺序（第1017-1456行）需要重新排列，优先级调整为：

1. 快速指令（Chip组合）- **最高**
2. 生成设置（目标字数、高级选项）
3. 剧情走向选择
4. 资料检索
5. 文风管理
6. **AI续写按钮**（分离出来）
7. 生成进度（条件）
8. 提取的文风特征（条件）
9. RAG上下文（条件）
10. 多Agent协作（条件）
11. 小说信息

**实施方式**：

只需将右侧Drawer中的Box内容重新排序即可：

```typescript
// 在右侧Drawer的Box中
<Box sx={{ p: 2, overflow: 'auto' }}>
  <Typography variant="h6" gutterBottom>
    📝 AI写作助手
  </Typography>

  {/* 1. 快速指令 - 优先显示 */}
  <Box sx={{ mb: 2 }}>
    <Typography variant="body2" gutterBottom sx={{ fontWeight: 500 }}>
      💡 快速指令
    </Typography>
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
      {['展开这一段', '增加对话和冲突', '加强紧张感', '补充环境描写'].map((text) => (
        <Chip
          key={text}
          label={text}
          size="small"
          onClick={() => setAiInstruction(text)}
          sx={{ cursor: 'pointer' }}
        />
      ))}
    </Box>
  </Box>

  {/* 2. 生成设置 */}
  <Card sx={{ mb: 2 }}>
    {/* 现有的生成设置代码保留 */}
  </Card>

  {/* 3. 剧情走向选择 */}
  <Card sx={{ mb: 2 }}>
    {/* 现有代码保留 */}
  </Card>

  {/* 4. 资料检索 */}
  <Card sx={{ mb: 2 }}>
    {/* 现有代码保留 */}
  </Card>

  {/* 5. 文风管理 */}
  {/* (文风样本选择和新建) */}

  {/* 6. 突出的AI续写按钮 */}
  <Button
    fullWidth
    variant="contained"
    size="large"
    startIcon={<AutoFixHighIcon />}
    onClick={handleAiContinue}
    disabled={aiGenerating || (!content && !hasPrevContent)}
    sx={{
      mb: 1,
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontSize: '1.1rem',
      padding: '12px 24px',
    }}
  >
    {aiGenerating ? 'AI创作中...' : 'AI 续写'}
  </Button>

  {/* 撤销/重做快捷 */}
  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
    <Button
      fullWidth
      size="small"
      variant="outlined"
      onClick={handleUndo}
      disabled={historyIndex <= 0}
    >
      ↶ 撤销
    </Button>
    <Button
      fullWidth
      size="small"
      variant="outlined"
      onClick={handleRedo}
      disabled={historyIndex >= contentHistory.length - 1}
    >
      ↷ 重做
    </Button>
  </Box>

  {/* 7. 条件显示的反馈信息 */}
  {aiGenerating && (
    <Box sx={{ mb: 2 }}>
      <LinearProgress />
      <Typography variant="caption" sx={{ mt: 1 }}>
        {generationStep}
      </Typography>
    </Box>
  )}

  {/* 8-11. 其他条件显示的信息保留 */}
</Box>
```

**验证方式**：
```typescript
// 测试布局优化
1. 打开工作台
2. 右侧面板顶部应显示快速指令
3. "AI续写"按钮应该突出显示
4. 页面滚动时高频功能保持可见
```

---

## 📝 代码审查清单

### 删除检查
- [ ] dashboard对话框确实移除了"AI续写"
- [ ] novels/[id]对话框确实移除了"AI续写"
- [ ] 相关的状态变量已清理

### 新增功能检查
- [ ] 撤销/重做功能正常工作
- [ ] 人物出场追踪显示正确
- [ ] 格式化工具清理掉多余空行
- [ ] 搜索框能正确过滤小说
- [ ] 进度条和统计数据显示正确

### 性能检查
- [ ] 页面加载时间<3秒
- [ ] 点击按钮响应<100ms
- [ ] 内存占用无明显增长
- [ ] 历史栈不会无限增长（定期清理旧历史）

### 兼容性检查
- [ ] 移动端显示正常
- [ ] 浏览器兼容性（Chrome、Firefox、Safari）
- [ ] 深色模式正常显示
- [ ] 键盘快捷键有效

---

## 🚀 发布检查清单

### 代码质量
- [ ] 没有Console错误和警告
- [ ] TypeScript类型检查通过
- [ ] ESLint检查通过
- [ ] 代码格式符合Prettier规范

### 功能验证
- [ ] 所有P1任务完成并测试
- [ ] 所有P2任务完成并测试
- [ ] 没有回归Bug
- [ ] 用户路径畅通（少于3次点击完成主要任务）

### 文档更新
- [ ] 更新API文档（如有变化）
- [ ] 更新用户指南
- [ ] 更新开发规范文档

### 交付物
- [ ] 代码push到仓库
- [ ] 建立Pull Request并通过审核
- [ ] 发布到staging环境供测试
- [ ] 发布到production环境

---

## 📊 进度跟踪

### Week 1（5天）
```
Mon-Tue: 完成Task 1.1-1.3（删除冗余按钮）
Wed-Thu: 完成Task 2.1-2.2（撤销和人物追踪）
Fri: 完成Task 2.3-2.4（格式化和搜索）+ 测试
```

### Week 2（5天）
```
Mon-Tue: 完成Task 3.1-3.2（统计和布局优化）
Wed-Thu: 完整测试（功能、性能、兼容性）
Fri: 修复Bug和细节优化
```

### Week 3（可选）
```
补充P2功能：快速指令库、词汇统计等
```

---

## 🔗 参考资源

### Material-UI 官方文档
- Button组件：https://mui.com/api/button/
- Dialog组件：https://mui.com/api/dialog/
- Card组件：https://mui.com/api/card/

### React 官方文档
- useEffect Hook：https://react.dev/reference/react/useEffect
- useState Hook：https://react.dev/reference/react/useState
- useRef Hook：https://react.dev/reference/react/useRef

### TypeScript 类型定义
- 确保所有新增状态都有正确的类型注解
- 使用`Array<T>`而非`T[]`保持一致性

---

**实施指南完成**
**下一步**：按优先级选择任务开始实施
**预期交付时间**：2-3周（全量实施）

