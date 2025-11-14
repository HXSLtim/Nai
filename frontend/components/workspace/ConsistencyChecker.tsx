'use client';

import { useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { api } from '@/lib/api';
import type { SSEEvent } from '@/lib/sse';
import type { Novel, Chapter } from '@/types';

interface ConsistencyCheckerProps {
  novel: Novel | null;
  currentChapter: Chapter | null;
  content: string;
  onError: (error: string) => void;
}

interface ConsistencySummary {
  hasConflict: boolean;
  violations: string[];
  checksPerformed: string[];
  score?: number;
  details?: {
    character_consistency?: number;
    timeline_consistency?: number;
    worldview_consistency?: number;
  };
}

export default function ConsistencyChecker({
  novel,
  currentChapter,
  content,
  onError,
}: ConsistencyCheckerProps) {
  const [consistencyChecking, setConsistencyChecking] = useState(false);
  const [consistencySummary, setConsistencySummary] = useState<ConsistencySummary | null>(null);
  const [checkingStep, setCheckingStep] = useState('');
  
  // SSE事件日志
  const [sseEvents, setSseEvents] = useState<{ id: number; type: string; label: string }[]>([]);
  const sseEventIdRef = useState(0);

  const handleConsistencyCheck = useCallback(async () => {
    if (!novel || !currentChapter) {
      onError('未找到当前章节');
      return;
    }

    const text = content || currentChapter.content || '';
    if (!text) {
      onError('当前章节内容为空，无法进行一致性检查');
      return;
    }

    setConsistencyChecking(true);
    setConsistencySummary(null);
    setSseEvents([]);
    setCheckingStep('正在初始化检查...');

    try {
      await api.checkConsistencyStream(
        {
          novel_id: novel.id,
          chapter: currentChapter.chapter_number,
          content: text,
          current_day: 1,
        },
        {
          onEvent: (event: SSEEvent) => {
            setSseEvents((prev) => {
              const id = sseEventIdRef[0]++;
              let label = '';
              if (event.type === 'layer') {
                const layer = (event as any).layer ?? '';
                const status = (event as any).status ?? '';
                label = `${layer}:${status}`;
                setCheckingStep(`检查${layer}...`);
              } else if (event.type === 'summary') {
                label = 'summary';
                setCheckingStep('生成检查报告...');
              } else {
                label = event.type || 'unknown';
              }

              const next = [{ id, type: event.type ?? 'unknown', label }, ...prev];
              return next.slice(0, 30);
            });
          },
          onSummary: (summary: any) => {
            setConsistencySummary({
              hasConflict: !!summary.has_conflict,
              violations: summary.violations || [],
              checksPerformed: summary.checks_performed || [],
              score: summary.consistency_score,
              details: summary.details,
            });
            setCheckingStep('检查完成');
          },
          onError: (error: Error) => {
            onError(error.message);
            setCheckingStep('检查失败');
          },
        },
      );
    } catch (err) {
      onError(err instanceof Error ? err.message : '一致性检查失败');
      setCheckingStep('检查失败');
    } finally {
      setConsistencyChecking(false);
    }
  }, [novel, currentChapter, content, onError]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 80) return <CheckCircleIcon color="success" />;
    if (score >= 60) return <WarningIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 1,
          }}
        >
          <Typography variant="subtitle2">一致性检查</Typography>
          <Button
            size="small"
            variant="outlined"
            startIcon={<PlayArrowIcon />}
            onClick={handleConsistencyCheck}
            disabled={consistencyChecking || !novel || !currentChapter}
          >
            {consistencyChecking ? '检查中...' : '开始检查'}
          </Button>
        </Box>
        <Divider sx={{ my: 1 }} />

        {/* 检查进度 */}
        {consistencyChecking && (
          <Box sx={{ mb: 2 }}>
            <LinearProgress sx={{ mb: 1 }} />
            <Typography variant="caption" color="text.secondary">
              {checkingStep}
            </Typography>
          </Box>
        )}

        {/* 检查结果 */}
        {consistencySummary ? (
          <Box>
            {/* 总体评分 */}
            {consistencySummary.score !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {getScoreIcon(consistencySummary.score)}
                <Box sx={{ ml: 1 }}>
                  <Typography variant="body2" fontWeight="medium">
                    一致性评分: {consistencySummary.score}/100
                  </Typography>
                  <Chip
                    label={
                      consistencySummary.score >= 80
                        ? '优秀'
                        : consistencySummary.score >= 60
                        ? '良好'
                        : '需要改进'
                    }
                    size="small"
                    color={getScoreColor(consistencySummary.score) as any}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              </Box>
            )}

            {/* 详细评分 */}
            {consistencySummary.details && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  详细评分:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {consistencySummary.details.character_consistency !== undefined && (
                    <Chip
                      label={`角色: ${consistencySummary.details.character_consistency}/100`}
                      size="small"
                      variant="outlined"
                    />
                  )}
                  {consistencySummary.details.timeline_consistency !== undefined && (
                    <Chip
                      label={`时间线: ${consistencySummary.details.timeline_consistency}/100`}
                      size="small"
                      variant="outlined"
                    />
                  )}
                  {consistencySummary.details.worldview_consistency !== undefined && (
                    <Chip
                      label={`世界观: ${consistencySummary.details.worldview_consistency}/100`}
                      size="small"
                      variant="outlined"
                    />
                  )}
                </Box>
              </Box>
            )}

            {/* 冲突提示 */}
            <Alert
              severity={consistencySummary.hasConflict ? 'warning' : 'success'}
              sx={{ mb: 2 }}
            >
              {consistencySummary.hasConflict ? '发现潜在冲突' : '未发现明显冲突'}
            </Alert>

            {/* 违规项目列表 */}
            {consistencySummary.violations.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  发现的问题:
                </Typography>
                <List dense>
                  {consistencySummary.violations.slice(0, 5).map((violation, idx) => (
                    <ListItem key={idx} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <WarningIcon color="warning" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={violation}
                        primaryTypographyProps={{
                          variant: 'body2',
                          color: 'text.secondary',
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
                {consistencySummary.violations.length > 5 && (
                  <Typography variant="caption" color="text.secondary">
                    还有 {consistencySummary.violations.length - 5} 个问题...
                  </Typography>
                )}
              </Box>
            )}

            {/* 检查项目 */}
            <Box>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                已完成的检查:
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {consistencySummary.checksPerformed.map((check, idx) => (
                  <Chip
                    key={idx}
                    label={check}
                    size="small"
                    color="success"
                    variant="outlined"
                    icon={<CheckCircleIcon />}
                  />
                ))}
              </Box>
            </Box>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            基于知识图谱对章节内容进行深度一致性分析，检查角色关系、时间线和世界观的逻辑一致性。
          </Typography>
        )}

        {/* 检查流程显示 */}
        {(consistencyChecking || sseEvents.length > 0) && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              🔍 一致性检查流程
              {consistencyChecking && (
                <Chip 
                  label="检查中" 
                  size="small" 
                  color="info" 
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
                maxHeight: 150, 
                overflow: 'auto',
                bgcolor: 'info.50',
                borderRadius: 1,
                p: 1.5,
                border: '1px solid',
                borderColor: 'info.200'
              }}
            >
              {sseEvents.length === 0 && consistencyChecking && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <LinearProgress sx={{ flexGrow: 1, height: 4 }} />
                  <Typography variant="body2" color="text.secondary">
                    初始化检查引擎...
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
                    opacity: consistencyChecking && index === 0 ? 1 : 0.8,
                    transition: 'opacity 0.3s ease'
                  }}
                >
                  {consistencyChecking && index === 0 ? (
                    <Box sx={{ width: 12, height: 12, position: 'relative' }}>
                      <LinearProgress 
                        sx={{ 
                          width: 12, 
                          height: 12, 
                          borderRadius: '50%',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: '50%'
                          }
                        }} 
                      />
                    </Box>
                  ) : (
                    <CheckCircleIcon 
                      sx={{ 
                        width: 12, 
                        height: 12, 
                        color: 'success.main',
                        flexShrink: 0
                      }} 
                    />
                  )}
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontSize: '0.8rem',
                      fontFamily: 'monospace',
                      color: consistencyChecking && index === 0 ? 'info.main' : 'text.secondary'
                    }}
                  >
                    [{new Date().toLocaleTimeString()}] {event.label}
                  </Typography>
                </Box>
              ))}
              
              {consistencyChecking && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1, pt: 1, borderTop: '1px dashed', borderColor: 'info.300' }}>
                  <LinearProgress sx={{ flexGrow: 1, height: 4 }} />
                  <Typography variant="body2" color="info.main" sx={{ fontWeight: 500 }}>
                    {checkingStep || '正在分析...'}
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
