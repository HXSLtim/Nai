'use client';

import { Fragment, Suspense, useEffect, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Divider,
  CircularProgress,
  Chip,
  Alert,
  IconButton,
  Card,
  CardContent,
  LinearProgress,
  Slider,
  Select,
  MenuItem,
  Menu,
  FormControl,
  InputLabel,
  FormControlLabel,
  Switch,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Collapse,
  InputAdornment,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SaveIcon from '@mui/icons-material/Save';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import UndoIcon from '@mui/icons-material/Undo';
import RedoIcon from '@mui/icons-material/Redo';
import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import WarningIcon from '@mui/icons-material/Warning';
import { api } from '@/lib/api';
import type { Novel, Chapter, StyleSample, AgentWorkflowTrace } from '@/types';
import type { SSEEvent } from '@/lib/sse';

// 工作台组件
import AiWritingAssistant from '@/components/workspace/AiWritingAssistant';
import WorkflowPanel from '@/components/workspace/WorkflowPanel';
import TextRewriter from '@/components/workspace/TextRewriter';
import ConsistencyChecker from '@/components/workspace/ConsistencyChecker';
import PlotOptionsGenerator from '@/components/workspace/PlotOptionsGenerator';
import AutoSaver from '@/components/workspace/AutoSaver';
import StyleManager from '@/components/workspace/StyleManager';
import ResearchAssistant from '@/components/workspace/ResearchAssistant';
import CharacterStats from '@/components/workspace/CharacterStats';
// import ChapterManager from '@/components/workspace/ChapterManager';

const DRAWER_WIDTH = 280;
const AI_PANEL_WIDTH = 400;
const AUTO_SAVE_DELAY = 5000;

/**
 * 写作工作台 - 专业的AI辅助写作环境
 */
function WorkspacePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const novelId = Number(searchParams.get('novel'));
  const chapterId = Number(searchParams.get('chapter'));

  // 数据状态
  const [novel, setNovel] = useState<Novel | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null);
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [autoSaving, setAutoSaving] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [lastSavedTitle, setLastSavedTitle] = useState('');
  const [lastSavedContent, setLastSavedContent] = useState('');

  // UI状态
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);

  // 章节管理状态
  const [createChapterDialogOpen, setCreateChapterDialogOpen] = useState(false);
  const [newChapterTitle, setNewChapterTitle] = useState('');
  const [newChapterNumber, setNewChapterNumber] = useState(1);
  const [creatingChapter, setCreatingChapter] = useState(false);

  // 章节菜单状态
  const [chapterMenuAnchor, setChapterMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedChapterForMenu, setSelectedChapterForMenu] = useState<Chapter | null>(null);
  const [deleteChapterDialogOpen, setDeleteChapterDialogOpen] = useState(false);
  const [editChapterDialogOpen, setEditChapterDialogOpen] = useState(false);
  const [editChapterTitle, setEditChapterTitle] = useState('');
  const [editChapterNumber, setEditChapterNumber] = useState(1);
  const [deletingChapter, setDeletingChapter] = useState(false);
  const [updatingChapter, setUpdatingChapter] = useState(false);

  // 局部改写状态
  const [selectionStart, setSelectionStart] = useState<number | null>(null);
  const [selectionEnd, setSelectionEnd] = useState<number | null>(null);
  const [selectedText, setSelectedText] = useState('');
  const contentInputRef = useRef<HTMLTextAreaElement | null>(null);

  // 文风样本状态
  const [selectedStyleSampleId, setSelectedStyleSampleId] = useState<number | null>(null);

  // 剧情走向提示（由PlotOptionsGenerator提供，供AI续写时参考）
  const [plotDirectionHint, setPlotDirectionHint] = useState<string | null>(null);

  // 撤销/重做状态
  const [contentHistory, setContentHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const isApplyingHistoryRef = useRef(false);
  const streamingTimerRef = useRef<number | null>(null);
  const sseEventIdRef = useRef(0);

  // 多Agent工作流追踪（用于右侧工作流可视化侧栏）
  const [workflowTrace, setWorkflowTrace] = useState<AgentWorkflowTrace | null>(null);

  // AI续写助手的 ref，用于外部触发续写
  const aiWritingAssistantRef = useRef<{ triggerContinue: () => void } | null>(null);

  const hasUnsavedChanges = title !== lastSavedTitle || content !== lastSavedContent;

  const formatTime = (date: Date) => {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  // 加载工作台数据
  const loadWorkspace = async () => {
    try {
      const [novelData, chaptersData] = await Promise.all([
        api.getNovel(novelId),
        api.getChapters(novelId),
      ]);

      setNovel(novelData);
      setChapters(chaptersData.sort((a, b) => a.chapter_number - b.chapter_number));

      // 加载当前章节
      if (chapterId) {
        const chapter = chaptersData.find(c => c.id === chapterId);
        if (chapter) {
          setCurrentChapter(chapter);
          setContent(chapter.content);
          setTitle(chapter.title);
          setLastSavedTitle(chapter.title);
          setLastSavedContent(chapter.content);
          setLastSavedAt(null);
          // 初始化撤销/重做历史
          setContentHistory([chapter.content]);
          setHistoryIndex(0);
        }
      }
    } catch (err) {
      setError('加载失败，请返回重试');
    } finally {
      setLoading(false);
    }
  };

  // 保存章节
  const handleSave = async () => {
    if (!currentChapter) return;

    if (!title || !content) {
      setError('标题和内容不能为空');
      return;
    }

    setSaving(true);
    try {
      await api.updateChapter(novelId, currentChapter.id, {
        title,
        content,
      });
      setLastSavedAt(new Date());
      setLastSavedTitle(title);
      setLastSavedContent(content);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  // 处理AI生成的内容
  const handleContentGenerated = (newContent: string) => {
    console.log('[DEBUG] handleContentGenerated 被调用');
    console.log('[DEBUG] 新内容长度:', newContent.length);
    console.log('[DEBUG] 新内容前100字:', newContent.substring(0, 100));
    setContent(newContent);
    // 添加到历史记录
    if (!isApplyingHistoryRef.current) {
      const newHistory = contentHistory.slice(0, historyIndex + 1);
      newHistory.push(newContent);
      setContentHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
    }
  };

  // 将AI生成的内容应用到下一章节（自动创建）
  const handleApplyGeneratedToNextChapter = async (generatedText: string) => {
    if (!novelId) {
      setError('未找到当前小说');
      return;
    }

    try {
      // 计算下一章节号：在现有章节号中取最大值再加1
      const nextNumber = Math.max(...chapters.map(c => c.chapter_number), 0) + 1;
      const nextTitle = `第${nextNumber}章`;

      const newChapter = await api.createChapter(novelId, {
        chapter_number: nextNumber,
        title: nextTitle,
        content: generatedText,
      });

      // 跳转到新创建的章节，loadWorkspace 会在 chapterId 变化后自动加载
      router.push(`/workspace?novel=${novelId}&chapter=${newChapter.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建下一章节失败');
    }
  };

  // 处理文本改写
  const handleTextRewritten = (newText: string, start: number, end: number) => {
    const beforeText = content.slice(0, start);
    const afterText = content.slice(end);
    const newContent = beforeText + newText + afterText;
    
    setContent(newContent);
    setSelectedText('');
    setSelectionStart(null);
    setSelectionEnd(null);
    
    // 添加到历史记录
    if (!isApplyingHistoryRef.current) {
      const newHistory = contentHistory.slice(0, historyIndex + 1);
      newHistory.push(newContent);
      setContentHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
    }
  };

  // 处理剧情选项选择
  const handlePlotSelected = (option: { id: number; title: string; summary: string; impact?: string | null; risk?: string | null }) => {
    const parts: string[] = [];
    parts.push(`${option.title}`);
    parts.push(option.summary);
    if (option.impact) {
      parts.push(`影响：${option.impact}`);
    }
    if (option.risk) {
      parts.push(`风险：${option.risk}`);
    }
    setPlotDirectionHint(parts.join('；'));
  };

  // 处理剧情选项选择并立即续写
  const handlePlotSelectedAndContinue = (option: { id: number; title: string; summary: string; impact?: string | null; risk?: string | null }) => {
    // 先设置剧情走向
    handlePlotSelected(option);
    // 稍微延迟以确保状态更新，然后触发 AI 续写
    setTimeout(() => {
      if (aiWritingAssistantRef.current) {
        aiWritingAssistantRef.current.triggerContinue();
      }
    }, 100);
  };

  // 打开新建章节对话框
  const handleCreateChapterOpen = () => {
    const nextNumber = Math.max(...chapters.map(c => c.chapter_number), 0) + 1;
    setNewChapterNumber(nextNumber);
    setNewChapterTitle(`第${nextNumber}章`);
    setCreateChapterDialogOpen(true);
  };

  // 创建新章节
  const handleCreateChapter = async () => {
    if (!newChapterTitle.trim()) {
      setError('章节标题不能为空');
      return;
    }

    setCreatingChapter(true);
    try {
      const newChapter = await api.createChapter(novelId, {
        chapter_number: newChapterNumber,
        title: newChapterTitle.trim(),
        content: '',
      });
      
      setCreateChapterDialogOpen(false);
      setNewChapterTitle('');
      await loadWorkspace(); // 重新加载章节列表
      
      // 自动跳转到新创建的章节
      router.push(`/workspace?novel=${novelId}&chapter=${newChapter.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建章节失败');
    } finally {
      setCreatingChapter(false);
    }
  };

  // 打开章节菜单
  const handleChapterMenuOpen = (event: React.MouseEvent<HTMLElement>, chapter: Chapter) => {
    event.stopPropagation();
    setChapterMenuAnchor(event.currentTarget);
    setSelectedChapterForMenu(chapter);
  };

  // 关闭章节菜单
  const handleChapterMenuClose = () => {
    setChapterMenuAnchor(null);
    setSelectedChapterForMenu(null);
  };

  // 打开编辑章节对话框
  const handleEditChapterOpen = () => {
    if (selectedChapterForMenu) {
      setEditChapterTitle(selectedChapterForMenu.title);
      setEditChapterNumber(selectedChapterForMenu.chapter_number);
      setEditChapterDialogOpen(true);
    }
    handleChapterMenuClose();
  };

  // 打开删除章节对话框
  const handleDeleteChapterOpen = () => {
    // 仅关闭菜单，不要清空selectedChapterForMenu，
    // 后续删除对话框需要依赖该状态来确定要删除的章节
    setDeleteChapterDialogOpen(true);
    setChapterMenuAnchor(null);
  };

  // 更新章节
  const handleUpdateChapter = async () => {
    if (!selectedChapterForMenu || !editChapterTitle.trim()) {
      setError('章节标题不能为空');
      return;
    }

    setUpdatingChapter(true);
    try {
      await api.updateChapter(novelId, selectedChapterForMenu.id, {
        title: editChapterTitle.trim(),
        chapter_number: editChapterNumber,
      });
      
      setEditChapterDialogOpen(false);
      setEditChapterTitle('');
      setSelectedChapterForMenu(null);
      await loadWorkspace();
    } catch (err) {
      setError(err instanceof Error ? err.message : '更新章节失败');
    } finally {
      setUpdatingChapter(false);
    }
  };

  // 删除章节
  const handleDeleteChapter = async () => {
    if (!selectedChapterForMenu) return;

    setDeletingChapter(true);
    try {
      await api.deleteChapter(novelId, selectedChapterForMenu.id);
      
      setDeleteChapterDialogOpen(false);
      setSelectedChapterForMenu(null);
      await loadWorkspace();
      
      // 如果删除的是当前章节，跳转到第一个章节
      if (currentChapter?.id === selectedChapterForMenu.id) {
        const remainingChapters = chapters.filter(c => c.id !== selectedChapterForMenu.id);
        if (remainingChapters.length > 0) {
          router.push(`/workspace?novel=${novelId}&chapter=${remainingChapters[0].id}`);
        } else {
          router.push(`/workspace?novel=${novelId}`);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除章节失败');
    } finally {
      setDeletingChapter(false);
    }
  };

  // 加载数据
  useEffect(() => {
    if (novelId) {
      loadWorkspace();
    }
  }, [novelId, chapterId]);

  return (
    <Fragment>
      {/* 移动端章节列表抽屉 */}
      <Drawer
        variant="temporary"
        anchor="left"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
          },
        }}
      >
        <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
          <Typography variant="h6" gutterBottom fontWeight="600">
            章节管理
          </Typography>
          
          {/* 新建章节按钮 */}
          <Button
            fullWidth
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateChapterOpen}
            sx={{ mb: 2 }}
          >
            新建章节
          </Button>
          
          <Divider sx={{ mb: 2 }} />
          
          <List dense>
            {chapters.map((chapter) => (
              <ListItem
                key={chapter.id}
                sx={{
                  border: '1px solid',
                  borderColor: currentChapter?.id === chapter.id ? 'primary.main' : 'divider',
                  borderRadius: 1,
                  mb: 1,
                  cursor: 'pointer',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover',
                  },
                }}
                onClick={() => {
                  router.push(`/workspace?novel=${novelId}&chapter=${chapter.id}`);
                  setMobileOpen(false);
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" fontWeight="medium">
                        第{chapter.chapter_number}章
                      </Typography>
                      {currentChapter?.id === chapter.id && (
                        <Chip label="当前" size="small" color="primary" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {chapter.title}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={`${chapter.word_count || 0} 字`}
                          size="small"
                          variant="outlined"
                        />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(chapter.updated_at || chapter.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton 
                    size="small"
                    onClick={(e) => handleChapterMenuOpen(e, chapter)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>


      <Box sx={{ display: 'flex', height: '100vh', width: '100%' }}>
        {/* 左侧章节列表（桌面版） */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            width: DRAWER_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              position: 'relative',
            },
          }}
        >
          <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom fontWeight="600">
              章节管理
            </Typography>
            
            {/* 新建章节按钮 */}
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateChapterOpen}
              sx={{ mb: 2 }}
            >
              新建章节
            </Button>
            
            <Divider sx={{ mb: 2 }} />
            
            <List dense>
              {chapters.map((chapter) => (
                <ListItem
                  key={chapter.id}
                  sx={{
                    border: '1px solid',
                    borderColor: currentChapter?.id === chapter.id ? 'primary.main' : 'divider',
                    borderRadius: 1,
                    mb: 1,
                    cursor: 'pointer',
                    '&:hover': {
                      borderColor: 'primary.main',
                      bgcolor: 'action.hover',
                    },
                  }}
                  onClick={() => {
                    router.push(`/workspace?novel=${novelId}&chapter=${chapter.id}`);
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" fontWeight="medium">
                          第{chapter.chapter_number}章
                        </Typography>
                        {currentChapter?.id === chapter.id && (
                          <Chip label="当前" size="small" color="primary" />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 0.5 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {chapter.title}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Chip
                            label={`${chapter.word_count || 0} 字`}
                            size="small"
                            variant="outlined"
                          />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(chapter.updated_at || chapter.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton 
                      size="small"
                      onClick={(e) => handleChapterMenuOpen(e, chapter)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* 主内容区域 */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* 顶部工具栏 */}
          <AppBar
            position="static"
            sx={{
              bgcolor: 'primary.main',
              boxShadow: 1,
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                edge="start"
                onClick={() => setMobileOpen(!mobileOpen)}
                sx={{ mr: 2, display: { sm: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              
              <IconButton
                color="inherit"
                onClick={() => router.back()}
                sx={{ mr: 2 }}
              >
                <ArrowBackIcon />
              </IconButton>

              <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
                {novel && (
                  <Typography
                    variant="h6"
                    sx={{
                      color: 'white',
                      fontWeight: 600,
                      fontSize: '1.1rem',
                    }}
                  >
                    {novel.title}
                  </Typography>
                )}
                
                {currentChapter && (
                  <Chip
                    label={`第${currentChapter.chapter_number}章`}
                    size="small"
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      color: 'white',
                      fontWeight: 500,
                    }}
                  />
                )}
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {/* 自动保存组件 */}
                <AutoSaver
                  novelId={novelId}
                  chapterId={chapterId}
                  title={title}
                  content={content}
                  lastSavedTitle={lastSavedTitle}
                  lastSavedContent={lastSavedContent}
                  onSaved={setLastSavedAt}
                  onError={setError}
                />
                
                {hasUnsavedChanges && (
                  <Chip
                    label="未保存"
                    size="small"
                    color="warning"
                    sx={{ color: 'white' }}
                  />
                )}
                
                {lastSavedAt && (
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    {formatTime(lastSavedAt)} 已保存
                  </Typography>
                )}

                <Button
                  color="inherit"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  disabled={saving || !hasUnsavedChanges}
                  sx={{ ml: 1 }}
                >
                  {saving ? '保存中...' : '保存'}
                </Button>
              </Box>
            </Toolbar>
          </AppBar>

          {/* 主编辑区域 */}
          <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
            {/* 章节内容编辑区 */}
            <Box
              sx={{
                flexGrow: 1,
                display: 'flex',
                flexDirection: 'column',
                p: { xs: 2, sm: 4, md: 5 },
                overflow: 'auto',
                maxWidth: 900,
                mx: 'auto',
                width: '100%',
              }}
            >
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <CircularProgress />
                </Box>
              ) : error ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              ) : currentChapter ? (
                <>
                  {/* 章节标题 */}
                  <TextField
                    fullWidth
                    label="章节标题"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    sx={{
                      mb: 4,
                      '& .MuiInputBase-root': {
                        fontSize: '1.5rem',
                        fontWeight: 500,
                      },
                    }}
                    variant="outlined"
                  />

                  {/* 章节内容 */}
                  <TextField
                    fullWidth
                    multiline
                    label="章节内容"
                    value={content}
                    onChange={(e) => {
                      setContent(e.target.value);
                      if (!isApplyingHistoryRef.current) {
                        const newHistory = contentHistory.slice(0, historyIndex + 1);
                        newHistory.push(e.target.value);
                        setContentHistory(newHistory);
                        setHistoryIndex(newHistory.length - 1);
                      }
                    }}
                    onSelect={(e) => {
                      const target = e.target as HTMLTextAreaElement;
                      const start = target.selectionStart;
                      const end = target.selectionEnd;

                      if (start !== end) {
                        setSelectionStart(start);
                        setSelectionEnd(end);
                        setSelectedText(content.slice(start, end));
                      } else {
                        setSelectionStart(null);
                        setSelectionEnd(null);
                        setSelectedText('');
                      }
                    }}
                    inputRef={contentInputRef}
                    sx={{
                      flexGrow: 1,
                      '& .MuiInputBase-root': {
                        height: '100%',
                        alignItems: 'flex-start',
                        borderColor: 'divider',
                      },
                      '& .MuiInputBase-input': {
                        height: '100% !important',
                        overflow: 'auto !important',
                        fontSize: '1rem',
                        lineHeight: 1.75,
                        letterSpacing: '0.02em',
                      },
                    }}
                    variant="outlined"
                    placeholder="开始写作..."
                  />

                  {/* 底部工具栏 */}
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      mt: 3,
                      p: 2.5,
                      bgcolor: 'background.subtle',
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'border.light',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <IconButton
                        size="small"
                        disabled={historyIndex <= 0}
                        onClick={() => {
                          if (historyIndex > 0) {
                            isApplyingHistoryRef.current = true;
                            setHistoryIndex(historyIndex - 1);
                            setContent(contentHistory[historyIndex - 1]);
                            setTimeout(() => {
                              isApplyingHistoryRef.current = false;
                            }, 100);
                          }
                        }}
                        sx={{
                          transition: 'all 0.2s ease',
                          '&:not(:disabled):hover': {
                            bgcolor: 'primary.container',
                            color: 'primary.dark',
                          },
                        }}
                      >
                        <UndoIcon fontSize="small" />
                      </IconButton>

                      <IconButton
                        size="small"
                        disabled={historyIndex >= contentHistory.length - 1}
                        onClick={() => {
                          if (historyIndex < contentHistory.length - 1) {
                            isApplyingHistoryRef.current = true;
                            setHistoryIndex(historyIndex + 1);
                            setContent(contentHistory[historyIndex + 1]);
                            setTimeout(() => {
                              isApplyingHistoryRef.current = false;
                            }, 100);
                          }
                        }}
                        sx={{
                          transition: 'all 0.2s ease',
                          '&:not(:disabled):hover': {
                            bgcolor: 'primary.container',
                            color: 'primary.dark',
                          },
                        }}
                      >
                        <RedoIcon fontSize="small" />
                      </IconButton>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Chip
                        label={`${content.length.toLocaleString()} 字`}
                        size="small"
                        variant="outlined"
                        sx={{ fontWeight: 500 }}
                      />
                    </Box>
                  </Box>
                </>
              ) : (
                <Box sx={{ textAlign: 'center', mt: 8 }}>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
                    请从左侧选择一个章节开始编辑
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    或者创建一个新章节
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        </Box>

        {/* 右侧AI助手面板 */}
        <Drawer
          variant="permanent"
          anchor="right"
          sx={{
            width: AI_PANEL_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: AI_PANEL_WIDTH,
              boxSizing: 'border-box',
              position: 'relative',
              height: '100%',
            },
          }}
        >
          <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
            {/* 多Agent工作流可视化 */}
            <WorkflowPanel workflowTrace={workflowTrace} />

            {/* AI续写助手 */}
            <AiWritingAssistant
              ref={aiWritingAssistantRef}
              novelId={novelId}
              chapterId={chapterId}
              currentContent={content}
              onContentGenerated={handleContentGenerated}
              onError={setError}
              onWorkflowTraceChange={setWorkflowTrace}
              plotDirectionHint={plotDirectionHint}
              onApplyToNextChapter={handleApplyGeneratedToNextChapter}
            />

            {/* 局部改写 */}
            <TextRewriter
              novelId={novelId}
              chapterId={chapterId}
              selectedText={selectedText}
              selectionStart={selectionStart}
              selectionEnd={selectionEnd}
              onTextRewritten={handleTextRewritten}
              onError={setError}
            />

            {/* 剧情走向选项 */}
            <PlotOptionsGenerator
              novelId={novelId}
              chapterId={chapterId}
              currentContent={content}
              onPlotSelected={handlePlotSelected}
              onPlotSelectedAndContinue={handlePlotSelectedAndContinue}
              onError={setError}
            />

            {/* 文风样本管理 */}
            <StyleManager
              novelId={novelId}
              selectedStyleSampleId={selectedStyleSampleId}
              onStyleSampleSelected={setSelectedStyleSampleId}
              onError={setError}
            />

            {/* 资料检索 */}
            <ResearchAssistant
              novelId={novelId}
              onError={setError}
            />

            {/* 角色统计 */}
            <CharacterStats
              novel={novel}
              currentContent={content}
            />

            {/* 一致性检查 */}
            <ConsistencyChecker
              novel={novel}
              currentChapter={currentChapter}
              content={content}
              onError={setError}
            />

            {/* 小说信息 */}
            {novel && (
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    小说信息
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    类型: {novel.genre || '未设置'}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1, fontSize: '0.85rem' }}>
                    简介: {novel.description || '暂无'}
                  </Typography>
                  {novel.worldview && (
                    <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                      世界观: {novel.worldview.slice(0, 100)}...
                    </Typography>
                  )}
                </CardContent>
              </Card>
            )}
          </Box>
        </Drawer>
      </Box>

      {/* 新建章节对话框 */}
      <Dialog 
        open={createChapterDialogOpen} 
        onClose={() => setCreateChapterDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>新建章节</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="章节序号"
            type="number"
            value={newChapterNumber}
            onChange={(e) => setNewChapterNumber(Number(e.target.value))}
            margin="normal"
            inputProps={{ min: 1 }}
          />
          <TextField
            fullWidth
            label="章节标题"
            value={newChapterTitle}
            onChange={(e) => setNewChapterTitle(e.target.value)}
            margin="normal"
            placeholder="例如：初入江湖"
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateChapterDialogOpen(false)}>
            取消
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateChapter}
            disabled={creatingChapter || !newChapterTitle.trim()}
          >
            {creatingChapter ? '创建中...' : '创建章节'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 章节操作菜单 */}
      <Menu
        anchorEl={chapterMenuAnchor}
        open={Boolean(chapterMenuAnchor)}
        onClose={handleChapterMenuClose}
      >
        <MenuItem onClick={handleEditChapterOpen}>
          <EditIcon sx={{ mr: 1 }} fontSize="small" />
          编辑章节
        </MenuItem>
        <MenuItem onClick={handleDeleteChapterOpen} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} fontSize="small" />
          删除章节
        </MenuItem>
      </Menu>

      {/* 编辑章节对话框 */}
      <Dialog 
        open={editChapterDialogOpen} 
        onClose={() => setEditChapterDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>编辑章节</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="章节序号"
            type="number"
            value={editChapterNumber}
            onChange={(e) => setEditChapterNumber(Number(e.target.value))}
            margin="normal"
            inputProps={{ min: 1 }}
          />
          <TextField
            fullWidth
            label="章节标题"
            value={editChapterTitle}
            onChange={(e) => setEditChapterTitle(e.target.value)}
            margin="normal"
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditChapterDialogOpen(false)}>
            取消
          </Button>
          <Button
            variant="contained"
            onClick={handleUpdateChapter}
            disabled={updatingChapter || !editChapterTitle.trim()}
          >
            {updatingChapter ? '更新中...' : '更新章节'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 删除章节对话框 */}
      <Dialog 
        open={deleteChapterDialogOpen} 
        onClose={() => setDeleteChapterDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="error" />
          确认删除章节
        </DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>警告：此操作不可撤销！</strong>
            </Typography>
          </Alert>
          <Typography variant="body1" gutterBottom>
            您确定要删除以下章节吗？
          </Typography>
          {selectedChapterForMenu && (
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1, mt: 2 }}>
              <Typography variant="body2" fontWeight="medium">
                第{selectedChapterForMenu.chapter_number}章 - {selectedChapterForMenu.title}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                字数: {selectedChapterForMenu.word_count || 0} 字
              </Typography>
            </Box>
          )}
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            删除章节将同时清理相关的RAG向量数据和缓存。
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteChapterDialogOpen(false)}>
            取消
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteChapter}
            disabled={deletingChapter}
          >
            {deletingChapter ? '删除中...' : '确认删除'}
          </Button>
        </DialogActions>
      </Dialog>
    </Fragment>
  );
}

export default function WorkspacePage() {
  return (
    <Suspense
      fallback={
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
          }}
        >
          <CircularProgress />
        </Box>
      }
    >
      <WorkspacePageContent />
    </Suspense>
  );
}
