'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  Container,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Divider,
  LinearProgress,
  Grid,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import PsychologyIcon from '@mui/icons-material/Psychology';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import CreateIcon from '@mui/icons-material/Create';
import { api } from '@/lib/api';
import type { Novel, Chapter, ChapterCreate } from '@/types';

export default function NovelDetailPage() {
  const router = useRouter();
  const params = useParams();
  const novelId = Number(params.id);

  const [novel, setNovel] = useState<Novel | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // 创建/编辑章节对话框
  const [openDialog, setOpenDialog] = useState(false);
  const [editingChapter, setEditingChapter] = useState<Chapter | null>(null);
  const [chapterForm, setChapterForm] = useState<ChapterCreate>({
    chapter_number: 1,
    title: '',
    content: '',
  });

  // AI生成状态
  const [aiGenerating, setAiGenerating] = useState(false);

  // AI初始化设定状态
  const [initDialogOpen, setInitDialogOpen] = useState(false);
  const [initLoading, setInitLoading] = useState(false);
  const [initTheme, setInitTheme] = useState('');
  const [initTargetChapters, setInitTargetChapters] = useState(10);
  const [initWorldview, setInitWorldview] = useState('');
  const [initMainCharacters, setInitMainCharacters] = useState('');
  const [initOutline, setInitOutline] = useState('');
  const [initPlotHooks, setInitPlotHooks] = useState('');

  useEffect(() => {
    if (!openDialog) return;
    if (typeof window === 'undefined') return;

    // 仅对新建章节使用本地草稿，避免与工作台编辑的已保存内容产生冲突
    try {
      if (!editingChapter) {
        const draftKey = `chapter_form_draft_new_${novelId}`;
        const draft = window.localStorage.getItem(draftKey);
        if (draft) {
          const parsed = JSON.parse(draft) as ChapterCreate;
          setChapterForm(parsed);
        }
      }
    } catch {
      // 忽略草稿恢复错误
    }
  }, [openDialog, editingChapter, novelId]);

  useEffect(() => {
    if (!openDialog) return;
    if (typeof window === 'undefined') return;

    // 仅在新建章节时持续写入本地草稿，编辑章节直接使用后端最新内容
    if (editingChapter) return;

    try {
      const draftKey = `chapter_form_draft_new_${novelId}`;
      window.localStorage.setItem(draftKey, JSON.stringify(chapterForm));
    } catch {
      // 忽略草稿写入错误
    }
  }, [openDialog, editingChapter, novelId, chapterForm]);

  useEffect(() => {
    loadNovelAndChapters();
  }, [novelId]);

  const loadNovelAndChapters = async () => {
    try {
      const [novelData, chaptersData] = await Promise.all([
        api.getNovel(novelId),
        api.getChapters(novelId),
      ]);
      setNovel(novelData);
      setChapters(chaptersData.sort((a, b) => a.chapter_number - b.chapter_number));
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
      setTimeout(() => router.push('/dashboard'), 2000);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChapter = () => {
    const nextChapterNumber = chapters.length > 0
      ? Math.max(...chapters.map(c => c.chapter_number)) + 1
      : 1;

    setChapterForm({
      chapter_number: nextChapterNumber,
      title: '',
      content: '',
    });
    setEditingChapter(null);
    setOpenDialog(true);
  };

  const handleAutoCreateChapter = async () => {
    try {
      setAiGenerating(true);

      const lastChapter = chapters.length > 0 ? chapters[chapters.length - 1] : null;
      const newChapter = await api.autoCreateChapter({
        novel_id: novelId,
        base_chapter_id: lastChapter?.id,
        target_length: 500,
      });

      await loadNovelAndChapters();
      router.push(`/workspace?novel=${novelId}&chapter=${newChapter.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'AI自动生成章节失败');
    } finally {
      setAiGenerating(false);
    }
  };

  const handleEditChapter = (chapter: Chapter) => {
    setChapterForm({
      chapter_number: chapter.chapter_number,
      title: chapter.title,
      content: chapter.content,
    });
    setEditingChapter(chapter);
    setOpenDialog(true);
  };

  const handleSaveChapter = async () => {
    try {
      if (editingChapter) {
        // 更新章节
        await api.updateChapter(novelId, editingChapter.id, {
          title: chapterForm.title,
          content: chapterForm.content,
        });

        if (typeof window !== 'undefined') {
          const draftKey = `chapter_form_draft_edit_${novelId}_${editingChapter.id}`;
          window.localStorage.removeItem(draftKey);
        }

        setOpenDialog(false);
        await loadNovelAndChapters();
      } else {
        // 创建新章节
        const newChapter = await api.createChapter(novelId, chapterForm);

        if (typeof window !== 'undefined') {
          const draftKey = `chapter_form_draft_new_${novelId}`;
          window.localStorage.removeItem(draftKey);
        }

        setOpenDialog(false);
        // 可选：刷新列表，确保返回列表时数据是最新的
        await loadNovelAndChapters();

        // 新建章节后直接进入写作工作台
        router.push(`/workspace?novel=${novelId}&chapter=${newChapter.id}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    }
  };

  const handleGenerateInit = async () => {
    try {
      setInitLoading(true);
      const result = await api.initNovel({
        novel_id: novelId,
        target_chapters: initTargetChapters,
        theme: initTheme || undefined,
      });

      setInitWorldview(result.worldview || '');
      setInitMainCharacters(
        result.main_characters && result.main_characters.length > 0
          ? result.main_characters.join('\n')
          : '',
      );
      setInitOutline(result.outline || '');
      setInitPlotHooks(
        result.plot_hooks && result.plot_hooks.length > 0
          ? result.plot_hooks.join('\n')
          : '',
      );
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '初始化设定失败');
    } finally {
      setInitLoading(false);
    }
  };

  const handleApplyInit = async () => {
    if (!novel) return;

    const combinedWorldview = `【世界观】\n${initWorldview}\n\n【主要角色】\n${initMainCharacters}\n\n【章节大纲】\n${initOutline}\n\n【剧情线索】\n${initPlotHooks}`;

    try {
      const updated = await api.updateNovel(novelId, {
        worldview: combinedWorldview,
      });
      setNovel(updated);
      setInitDialogOpen(false);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '应用设定失败');
    }
  };

  const handleDeleteChapter = async (chapterId: number) => {
    if (!confirm('确定要删除这个章节吗？')) return;

    try {
      await api.deleteChapter(novelId, chapterId);
      await loadNovelAndChapters();
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography>加载中...</Typography>
        </Box>
      </Container>
    );
  }

  if (!novel) {
    return null;
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* 头部导航 */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push('/dashboard')}
          >
            返回列表
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* 进度统计卡片 */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  总字数
                </Typography>
                <Typography variant="h4">
                  {chapters.reduce((sum, ch) => sum + (ch.word_count || 0), 0).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  章节数
                </Typography>
                <Typography variant="h4">
                  {chapters.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  平均字数/章
                </Typography>
                <Typography variant="h4">
                  {chapters.length > 0
                    ? Math.round(
                        chapters.reduce((sum, ch) => sum + (ch.word_count || 0), 0) / chapters.length
                      ).toLocaleString()
                    : 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* 小说信息卡片 */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
              <Box>
                <Typography variant="h4" gutterBottom>
                  {novel.title}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {novel.genre && (
                    <Chip label={novel.genre} size="small" color="primary" />
                  )}
                  <Chip
                    label={`${chapters.length} 章节`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Box>
              <Box>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<PsychologyIcon />}
                  onClick={() => setInitDialogOpen(true)}
                >
                  AI初始化设定
                </Button>
              </Box>
            </Box>

            <Box sx={{ mt: 2 }}>
              {chapters.length === 0 ? (
                <Button
                  variant="contained"
                  size="small"
                  onClick={handleCreateChapter}
                >
                  创建第 1 章并开始写作
                </Button>
              ) : (
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => {
                    const last = chapters[chapters.length - 1];
                    router.push(`/workspace?novel=${novelId}&chapter=${last.id}`);
                  }}
                >
                  继续写第 {chapters[chapters.length - 1].chapter_number} 章
                </Button>
              )}
            </Box>

            {novel.description && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  简介
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  {novel.description}
                </Typography>
              </>
            )}

            {novel.worldview && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  世界观设定
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  {novel.worldview}
                </Typography>
              </>
            )}
          </CardContent>
        </Card>

        {/* 章节列表 */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">章节列表</Typography>
              <Box>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<AutoFixHighIcon />}
                  onClick={handleAutoCreateChapter}
                  disabled={aiGenerating}
                  sx={{ mr: 1 }}
                >
                  AI 新章节
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={handleCreateChapter}
                >
                  新建章节
                </Button>
              </Box>
            </Box>

            {chapters.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  还没有创建任何章节
                </Typography>
              </Box>
            ) : (
              <List>
                {chapters.map((chapter, index) => {
                  const maxWords = Math.max(...chapters.map(ch => ch.word_count || 0), 1);
                  const progress = ((chapter.word_count || 0) / maxWords) * 100;
                  return (
                    <ListItem
                      key={chapter.id}
                      divider={index < chapters.length - 1}
                      sx={{
                        flexDirection: 'column',
                        alignItems: 'stretch',
                        py: 2,
                        '&:hover': {
                          bgcolor: 'action.hover',
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', mb: 1 }}>
                        <Box sx={{ flex: 1, minWidth: 0, mr: 2 }}>
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            第 {chapter.chapter_number} 章：{chapter.title}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                            <Chip
                              label={`${chapter.word_count || 0} 字`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            size="small"
                            onClick={() => router.push(`/workspace?novel=${novelId}&chapter=${chapter.id}`)}
                            title="进入写作工作台"
                            color="primary"
                          >
                            <CreateIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteChapter(chapter.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={progress}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: 'action.hover',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: 'primary.main',
                          },
                        }}
                      />
                    </ListItem>
                  );
                })}
              </List>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* 创建/编辑章节对话框 */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingChapter ? '编辑章节' : '新建章节'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="章节号"
            type="number"
            value={chapterForm.chapter_number}
            onChange={(e) =>
              setChapterForm({ ...chapterForm, chapter_number: Number(e.target.value) })
            }
            margin="normal"
            required
            disabled={!!editingChapter}
          />
          <TextField
            fullWidth
            label="章节标题"
            value={chapterForm.title}
            onChange={(e) => setChapterForm({ ...chapterForm, title: e.target.value })}
            margin="normal"
            required
            autoFocus
          />
          <TextField
            fullWidth
            label="章节内容"
            value={chapterForm.content}
            onChange={(e) => setChapterForm({ ...chapterForm, content: e.target.value })}
            margin="normal"
            multiline
            rows={12}
            required
            helperText={`当前字数：${chapterForm.content.length}`}
          />
        </DialogContent>
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
      </Dialog>

      {/* AI初始化小说设定对话框 */}
      <Dialog
        open={initDialogOpen}
        onClose={() => setInitDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>AI初始化小说设定</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="故事主题/补充说明"
            value={initTheme}
            onChange={(e) => setInitTheme(e.target.value)}
            margin="normal"
          />
          <TextField
            fullWidth
            type="number"
            label="目标章节数"
            value={initTargetChapters}
            onChange={(e) => setInitTargetChapters(Number(e.target.value) || 1)}
            margin="normal"
            inputProps={{ min: 1 }}
          />
          <Box sx={{ my: 2 }}>
            <Button
              variant="contained"
              onClick={handleGenerateInit}
              disabled={initLoading}
            >
              {initLoading ? '生成中...' : '生成AI设定'}
            </Button>
          </Box>
          <TextField
            fullWidth
            label="世界观设定"
            value={initWorldview}
            onChange={(e) => setInitWorldview(e.target.value)}
            margin="normal"
            multiline
            rows={4}
          />
          <TextField
            fullWidth
            label="主要角色（每行一个）"
            value={initMainCharacters}
            onChange={(e) => setInitMainCharacters(e.target.value)}
            margin="normal"
            multiline
            rows={4}
          />
          <TextField
            fullWidth
            label="故事大纲"
            value={initOutline}
            onChange={(e) => setInitOutline(e.target.value)}
            margin="normal"
            multiline
            rows={4}
          />
          <TextField
            fullWidth
            label="剧情线索（每行一个）"
            value={initPlotHooks}
            onChange={(e) => setInitPlotHooks(e.target.value)}
            margin="normal"
            multiline
            rows={4}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInitDialogOpen(false)}>取消</Button>
          <Button
            onClick={handleApplyInit}
            variant="contained"
            disabled={
              !initWorldview && !initMainCharacters && !initOutline && !initPlotHooks
            }
          >
            应用到小说
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
