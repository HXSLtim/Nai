'use client';

import { useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  LinearProgress,
  Divider,
  FormControlLabel,
  Switch,
  Collapse,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Chip,
  CircularProgress,
  Tooltip,
  IconButton,
  Paper,
  Fade,
} from '@mui/material';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import StopIcon from '@mui/icons-material/Stop';
import SettingsIcon from '@mui/icons-material/Settings';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import TuneIcon from '@mui/icons-material/Tune';
import { api } from '@/lib/api';
import type { SSEEvent } from '@/lib/sse';

interface AiWritingAssistantProps {
  novelId: number;
  chapterId: number | null;
  currentContent: string;
  onContentGenerated: (newContent: string) => void;
  onError: (error: string) => void;
}

export default function AiWritingAssistant({
  novelId,
  chapterId,
  currentContent,
  onContentGenerated,
  onError,
}: AiWritingAssistantProps) {
  // AI生成状态
  const [aiGenerating, setAiGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState('');
  const [generatedText, setGeneratedText] = useState('');
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  // 用户设置
  const [aiInstruction, setAiInstruction] = useState('');
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [targetLength, setTargetLength] = useState(500);
  const [styleStrength, setStyleStrength] = useState(0.7);
  const [pace, setPace] = useState<'slow' | 'medium' | 'fast'>('medium');
  const [tone, setTone] = useState<'neutral' | 'tense' | 'relaxed' | 'sad' | 'joyful'>('neutral');
  const [useRagStyle, setUseRagStyle] = useState(true);

  // SSE事件日志
  const [sseEvents, setSseEvents] = useState<{ id: number; type: string; label: string }[]>([]);
  const sseEventIdRef = useState(0);

  // 获取事件类型对应的颜色
  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'agent':
        return 'primary.main';
      case 'generation':
        return 'success.main';
      case 'worldview':
        return 'info.main';
      case 'character':
        return 'warning.main';
      case 'plot':
        return 'secondary.main';
      case 'style':
        return 'purple';
      default:
        return 'grey.400';
    }
  };

  const handleAiContinue = useCallback(async () => {
    if (!chapterId) {
      onError('未找到当前章节');
      return;
    }

    const controller = new AbortController();
    setAbortController(controller);
    setAiGenerating(true);
    setGenerationStep('正在连接AI...');
    setGeneratedText('');
    setSseEvents([]);

    try {
      await api.continueChapterStream(
        {
          novel_id: novelId,
          chapter_id: chapterId,
          current_content: currentContent,
          target_length: targetLength,
          style_strength: styleStrength,
          pace,
          tone,
          use_rag_style: useRagStyle,
        },
        {
          onChunk: (chunk: string) => {
            setGeneratedText(prev => prev + chunk);
            setGenerationStep('AI正在创作...');
          },
          onEvent: (event: SSEEvent) => {
            setSseEvents(prev => {
              const id = sseEventIdRef[0]++;
              let label = '';
              if (event.type === 'agent') {
                const agent = (event as any).agent ?? '';
                const status = (event as any).status ?? '';
                label = `${agent}:${status}`;
              } else if (event.type === 'generation') {
                label = 'generation';
              } else {
                label = event.type || 'unknown';
              }
              
              const next = [{ id, type: event.type ?? 'unknown', label }, ...prev];
              return next.slice(0, 20);
            });
          },
          onMetadata: (metadata: any) => {
            if (metadata.style_features) {
              setGenerationStep(`应用文风特征: ${metadata.style_features.slice(0, 2).join(', ')}`);
            }
          },
          onDone: () => {
            setGenerationStep('生成完成');
            setAiGenerating(false);
            setAbortController(null);
          },
          onError: (error: Error) => {
            onError(error.message);
            setGenerationStep('生成失败');
            setAiGenerating(false);
            setAbortController(null);
          },
        }
      );
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        onError(err.message);
        setGenerationStep('生成失败');
      }
      setAiGenerating(false);
      setAbortController(null);
    }
  }, [novelId, chapterId, currentContent, targetLength, styleStrength, pace, tone, useRagStyle, onError]);

  const handleStopGeneration = useCallback(() => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setAiGenerating(false);
      setGenerationStep('已停止生成');
    }
  }, [abortController]);

  const handleApplyGenerated = useCallback(() => {
    if (generatedText) {
      onContentGenerated(currentContent + generatedText);
      setGeneratedText('');
      setGenerationStep('');
    }
  }, [generatedText, currentContent, onContentGenerated]);

  const handleDiscardGenerated = useCallback(() => {
    setGeneratedText('');
    setGenerationStep('');
  }, []);

  return (
    <Card sx={{ mb: 2, overflow: 'visible' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SmartToyIcon color="primary" />
            <Typography variant="subtitle2" fontWeight="600">
              AI续写助手
            </Typography>
            {aiGenerating && (
              <Chip 
                label="生成中" 
                size="small" 
                color="primary" 
                sx={{ 
                  animation: 'pulse 1.5s infinite',
                  '@keyframes pulse': {
                    '0%': { opacity: 1 },
                    '50%': { opacity: 0.7 },
                    '100%': { opacity: 1 },
                  }
                }} 
              />
            )}
          </Box>
          <Tooltip title="AI参数设置">
            <IconButton size="small" onClick={() => setShowAdvanced(!showAdvanced)}>
              <TuneIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        {/* AI指令输入 */}
        <TextField
          fullWidth
          multiline
          rows={3}
          label="写作指令（可选）"
          value={aiInstruction}
          onChange={(e) => setAiInstruction(e.target.value)}
          placeholder="例如：增加一个转折情节，让主角遇到意外..."
          sx={{ mb: 2 }}
          disabled={aiGenerating}
        />

        {/* 生成/停止按钮 */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          {!aiGenerating ? (
            <Button
              fullWidth
              variant="contained"
              startIcon={<AutoFixHighIcon />}
              onClick={handleAiContinue}
              disabled={!chapterId}
              sx={{
                background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #1976D2 30%, #1CB5E0 90%)',
                },
              }}
            >
              AI续写
            </Button>
          ) : (
            <Button
              fullWidth
              variant="outlined"
              color="error"
              startIcon={<StopIcon />}
              onClick={handleStopGeneration}
              sx={{
                borderWidth: 2,
                '&:hover': {
                  borderWidth: 2,
                  backgroundColor: 'error.50',
                },
              }}
            >
              停止生成
            </Button>
          )}
        </Box>

        {/* 生成进度 */}
        {aiGenerating && (
          <Fade in={aiGenerating}>
            <Paper 
              elevation={0} 
              sx={{ 
                p: 2, 
                mb: 2, 
                bgcolor: 'primary.50', 
                border: '1px solid', 
                borderColor: 'primary.200',
                borderRadius: 2 
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" fontWeight="500" color="primary.main">
                  AI正在思考中...
                </Typography>
              </Box>
              <LinearProgress 
                sx={{ 
                  mb: 1, 
                  height: 6, 
                  borderRadius: 3,
                  backgroundColor: 'primary.100',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                  }
                }} 
              />
              <Typography variant="caption" color="primary.dark" sx={{ fontWeight: 500 }}>
                {generationStep || '正在分析文本结构...'}
              </Typography>
            </Paper>
          </Fade>
        )}

        {/* 生成的文本预览 */}
        {generatedText && (
          <Fade in={Boolean(generatedText)}>
            <Paper 
              elevation={2} 
              sx={{ 
                mb: 2, 
                overflow: 'hidden',
                border: '1px solid',
                borderColor: 'success.200',
              }}
            >
              <Box sx={{ p: 2, bgcolor: 'success.50', borderBottom: '1px solid', borderColor: 'success.200' }}>
                <Typography variant="subtitle2" fontWeight="600" color="success.dark">
                  ✨ AI生成内容预览
                </Typography>
              </Box>
              <Box
                sx={{
                  p: 2,
                  maxHeight: 200,
                  overflow: 'auto',
                  bgcolor: 'background.paper',
                }}
              >
                <Typography 
                  variant="body2" 
                  sx={{ 
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                    fontFamily: '"Noto Serif SC", serif',
                  }}
                >
                  {generatedText}
                </Typography>
              </Box>
              <Box sx={{ p: 2, bgcolor: 'grey.50', display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleDiscardGenerated}
                  sx={{ minWidth: 80 }}
                >
                  丢弃
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  onClick={handleApplyGenerated}
                  sx={{ 
                    minWidth: 100,
                    background: 'linear-gradient(45deg, #4CAF50 30%, #8BC34A 90%)',
                  }}
                >
                  应用到章节
                </Button>
              </Box>
            </Paper>
          </Fade>
        )}

        {/* 高级设置 */}
        <FormControlLabel
          control={
            <Switch
              checked={advancedOpen}
              onChange={(e) => setAdvancedOpen(e.target.checked)}
            />
          }
          label="高级设置"
          sx={{ mb: 1 }}
        />

        <Collapse in={advancedOpen}>
          <Box sx={{ mt: 2 }}>
            {/* 目标长度 */}
            <Typography variant="caption" gutterBottom>
              目标长度: {targetLength} 字
            </Typography>
            <Slider
              value={targetLength}
              onChange={(_, value) => setTargetLength(value as number)}
              min={100}
              max={2000}
              step={50}
              sx={{ mb: 2 }}
              disabled={aiGenerating}
            />

            {/* 文风强度 */}
            <Typography variant="caption" gutterBottom>
              文风强度: {Math.round(styleStrength * 100)}%
            </Typography>
            <Slider
              value={styleStrength}
              onChange={(_, value) => setStyleStrength(value as number)}
              min={0}
              max={1}
              step={0.1}
              sx={{ mb: 2 }}
              disabled={aiGenerating}
            />

            {/* 节奏控制 */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>节奏</InputLabel>
              <Select
                value={pace}
                onChange={(e) => setPace(e.target.value as typeof pace)}
                disabled={aiGenerating}
              >
                <MenuItem value="slow">缓慢</MenuItem>
                <MenuItem value="medium">适中</MenuItem>
                <MenuItem value="fast">快速</MenuItem>
              </Select>
            </FormControl>

            {/* 情感基调 */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>情感基调</InputLabel>
              <Select
                value={tone}
                onChange={(e) => setTone(e.target.value as typeof tone)}
                disabled={aiGenerating}
              >
                <MenuItem value="neutral">中性</MenuItem>
                <MenuItem value="tense">紧张</MenuItem>
                <MenuItem value="relaxed">轻松</MenuItem>
                <MenuItem value="sad">悲伤</MenuItem>
                <MenuItem value="joyful">欢快</MenuItem>
              </Select>
            </FormControl>

            {/* RAG文风开关 */}
            <FormControlLabel
              control={
                <Switch
                  checked={useRagStyle}
                  onChange={(e) => setUseRagStyle(e.target.checked)}
                  disabled={aiGenerating}
                />
              }
              label="使用RAG文风分析"
            />
          </Box>
        </Collapse>

        {/* Agent流程显示 */}
        {(aiGenerating || sseEvents.length > 0) && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              🤖 Agent处理流程
              {aiGenerating && (
                <Chip 
                  label="进行中" 
                  size="small" 
                  color="primary" 
                  sx={{ 
                    animation: 'pulse 1.5s infinite',
                    '@keyframes pulse': {
                      '0%': { opacity: 1 },
                      '50%': { opacity: 0.7 },
                      '100%': { opacity: 1 },
                    }
                  }} 
                />
              )}
            </Typography>
            <Divider sx={{ mb: 1 }} />
            
            <Box 
              sx={{ 
                maxHeight: 200, 
                overflow: 'auto',
                bgcolor: 'grey.50',
                borderRadius: 1,
                p: 1.5,
                border: '1px solid',
                borderColor: 'grey.200'
              }}
            >
              {sseEvents.length === 0 && aiGenerating && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CircularProgress size={12} />
                  <Typography variant="body2" color="text.secondary">
                    正在初始化Agent...
                  </Typography>
                </Box>
              )}
              
              {sseEvents.map((event, index) => (
                <Box 
                  key={event.id}
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1, 
                    mb: 0.5,
                    opacity: aiGenerating && index === 0 ? 1 : 0.8,
                    transition: 'opacity 0.3s ease'
                  }}
                >
                  {aiGenerating && index === 0 ? (
                    <CircularProgress size={12} color="primary" />
                  ) : (
                    <Box 
                      sx={{ 
                        width: 12, 
                        height: 12, 
                        borderRadius: '50%', 
                        bgcolor: getEventColor(event.type),
                        flexShrink: 0
                      }} 
                    />
                  )}
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontSize: '0.8rem',
                      fontFamily: 'monospace',
                      color: aiGenerating && index === 0 ? 'primary.main' : 'text.secondary'
                    }}
                  >
                    [{new Date().toLocaleTimeString()}] {event.label}
                  </Typography>
                </Box>
              ))}
              
              {aiGenerating && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1, pt: 1, borderTop: '1px dashed', borderColor: 'grey.300' }}>
                  <CircularProgress size={12} />
                  <Typography variant="body2" color="primary.main" sx={{ fontWeight: 500 }}>
                    {generationStep || 'Agent正在处理...'}
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
