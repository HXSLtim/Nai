'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Collapse,
  IconButton,
  Fade,
  Paper,
  Divider,
  useTheme,
  Avatar,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  AccessTime as AccessTimeIcon,
  AutoStories as AutoStoriesIcon,
  Person as PersonIcon,
  Create as CreateIcon,
  RateReview as RateReviewIcon,
  Public as PublicIcon,
  Psychology as PsychologyIcon,
  Architecture as ArchitectureIcon,
  DataObject as DataObjectIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import type { AgentWorkflowTrace } from '@/types';

interface AgentWorkflowVisualizationProps {
  workflowTrace: AgentWorkflowTrace | null;
  isGenerating?: boolean;
}

// 获取 Agent 类型对应的配置 (与 MultiAiStreamDisplay 保持一致)
const getAgentConfig = (agentName: string) => {
  const lowerName = agentName.toLowerCase();
  if (lowerName.includes('architect') || lowerName.includes('plot')) {
    return { icon: <ArchitectureIcon fontSize="small" />, color: '#9c27b0', label: '剧情架构师' };
  }
  if (lowerName.includes('character')) {
    return { icon: <PersonIcon fontSize="small" />, color: '#ff9800', label: '角色设计师' };
  }
  if (lowerName.includes('world') || lowerName.includes('setting')) {
    return { icon: <PublicIcon fontSize="small" />, color: '#009688', label: '世界观构建师' };
  }
  if (lowerName.includes('writer') || lowerName.includes('author')) {
    return { icon: <CreateIcon fontSize="small" />, color: '#2196f3', label: '核心作家' };
  }
  if (lowerName.includes('review') || lowerName.includes('critic')) {
    return { icon: <RateReviewIcon fontSize="small" />, color: '#4caf50', label: '内容审核员' };
  }
  return { icon: <PsychologyIcon fontSize="small" />, color: '#607d8b', label: 'AI 助手' };
};

// 格式化时长
const formatDuration = (ms: number | null | undefined): string => {
  if (!ms) return '';
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
};

// JSON 数据展示组件
const JsonViewer = ({ data, title, color }: { data: any; title: string; color: string }) => {
  if (!data || Object.keys(data).length === 0) return null;

  return (
    <Box sx={{ mt: 1, mb: 2 }}>
      <Typography variant="caption" fontWeight="bold" sx={{ color, display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <DataObjectIcon fontSize="inherit" /> {title}
      </Typography>
      <Paper
        variant="outlined"
        sx={{
          mt: 0.5,
          p: 1.5,
          bgcolor: 'grey.50',
          borderColor: 'divider',
          borderRadius: 2,
          fontSize: '0.75rem',
          fontFamily: 'Consolas, Monaco, monospace',
          overflow: 'auto',
          maxHeight: 200,
          '&::-webkit-scrollbar': {
            width: '6px',
            height: '6px',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'rgba(0,0,0,0.1)',
            borderRadius: '3px',
          },
        }}
      >
        <pre style={{ margin: 0 }}>{JSON.stringify(data, null, 2)}</pre>
      </Paper>
    </Box>
  );
};

const AgentWorkflowVisualization: React.FC<AgentWorkflowVisualizationProps> = ({
  workflowTrace,
  isGenerating = false,
}) => {
  const theme = useTheme();
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [showAll, setShowAll] = useState(true);

  // 自动展开最新的步骤
  useEffect(() => {
    if (workflowTrace?.steps && workflowTrace.steps.length > 0) {
      const lastStep = workflowTrace.steps[workflowTrace.steps.length - 1];
      setExpandedSteps(prev => {
        const newSet = new Set(prev);
        newSet.add(lastStep.id);
        return newSet;
      });
    }
  }, [workflowTrace?.steps?.length]);

  if (!workflowTrace) return null;

  const steps = workflowTrace.steps || [];
  const totalDuration = steps.reduce((sum, step) => sum + (step.duration_ms || 0), 0);

  const toggleStepExpanded = (stepId: string) => {
    setExpandedSteps(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stepId)) {
        newSet.delete(stepId);
      } else {
        newSet.add(stepId);
      }
      return newSet;
    });
  };

  return (
    <Card
      elevation={0}
      sx={{
        mb: 3,
        border: '1px solid',
        borderColor: 'divider',
        bgcolor: 'transparent'
      }}
    >
      <CardContent sx={{ p: 0 }}>
        {/* 标题栏 */}
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            bgcolor: 'grey.50',
            borderBottom: '1px solid',
            borderColor: 'divider'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              <ArchitectureIcon fontSize="small" />
            </Avatar>
            <Box>
              <Typography variant="subtitle2" fontWeight="bold">
                工作流执行追踪
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {steps.length} 个步骤 · 总耗时 {formatDuration(totalDuration)}
              </Typography>
            </Box>
          </Box>
          <IconButton size="small" onClick={() => setShowAll(!showAll)}>
            {showAll ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>

        <Collapse in={showAll}>
          <Box sx={{ p: 3 }}>
            {/* 工作流摘要 */}
            {workflowTrace.summary && (
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  mb: 3,
                  bgcolor: 'primary.50',
                  border: '1px dashed',
                  borderColor: 'primary.200',
                  borderRadius: 2
                }}
              >
                <Typography variant="body2" color="primary.dark" fontWeight="medium">
                  🎯 {workflowTrace.summary}
                </Typography>
              </Paper>
            )}

            {/* 步骤时间线 */}
            <Box sx={{ position: 'relative', ml: 1 }}>
              {/* 连接线 */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 20,
                  bottom: 20,
                  left: 19,
                  width: 2,
                  bgcolor: 'grey.200',
                  zIndex: 0
                }}
              />

              {steps.map((step, index) => {
                const agentConfig = getAgentConfig(step.agent_name || 'Unknown Agent');
                const isExpanded = expandedSteps.has(step.id);
                const isRunning = step.status === 'running';
                const isFailed = step.status === 'failed';
                const isCompleted = step.status === 'completed';

                return (
                  <Fade key={step.id} in={true} timeout={500}>
                    <Box sx={{ mb: 3, position: 'relative', zIndex: 1 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          gap: 2,
                          opacity: isRunning ? 1 : 0.9
                        }}
                      >
                        {/* 左侧图标 */}
                        <Box sx={{ pt: 0.5 }}>
                          <Avatar
                            sx={{
                              width: 40,
                              height: 40,
                              bgcolor: isFailed ? 'error.main' : (isRunning ? 'primary.main' : 'white'),
                              border: '2px solid',
                              borderColor: isFailed ? 'error.main' : (isRunning ? 'primary.main' : agentConfig.color),
                              color: isFailed || isRunning ? 'white' : agentConfig.color,
                              boxShadow: isRunning ? `0 0 10px ${theme.palette.primary.main}` : 'none',
                              transition: 'all 0.3s ease'
                            }}
                          >
                            {isFailed ? <ErrorIcon /> : (isRunning ? <PlayArrowIcon /> : agentConfig.icon)}
                          </Avatar>
                        </Box>

                        {/* 右侧内容卡片 */}
                        <Paper
                          elevation={isExpanded ? 2 : 0}
                          variant={isExpanded ? 'elevation' : 'outlined'}
                          sx={{
                            flex: 1,
                            overflow: 'hidden',
                            border: isExpanded ? 'none' : '1px solid',
                            borderColor: 'grey.200',
                            borderRadius: 2,
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              borderColor: agentConfig.color,
                              bgcolor: 'background.paper'
                            }
                          }}
                        >
                          {/* 步骤头部 */}
                          <Box
                            onClick={() => toggleStepExpanded(step.id)}
                            sx={{
                              p: 2,
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              bgcolor: isRunning ? 'primary.50' : 'transparent'
                            }}
                          >
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                <Typography variant="subtitle2" fontWeight="bold">
                                  {step.title}
                                </Typography>
                                {isRunning && (
                                  <Chip
                                    label="执行中"
                                    size="small"
                                    color="primary"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                )}
                                {isFailed && (
                                  <Chip
                                    label="失败"
                                    size="small"
                                    color="error"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                )}
                              </Box>
                              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
                                {step.description}
                              </Typography>
                            </Box>

                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Box sx={{ textAlign: 'right' }}>
                                <Typography variant="caption" display="block" color="text.secondary">
                                  {agentConfig.label}
                                </Typography>
                                {step.duration_ms && (
                                  <Typography variant="caption" display="block" fontWeight="medium" color="text.primary">
                                    <AccessTimeIcon sx={{ fontSize: 12, verticalAlign: 'text-top', mr: 0.5 }} />
                                    {formatDuration(step.duration_ms)}
                                  </Typography>
                                )}
                              </Box>
                              <IconButton size="small" sx={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}>
                                <ExpandMoreIcon fontSize="small" />
                              </IconButton>
                            </Box>
                          </Box>

                          {/* 步骤详情 */}
                          <Collapse in={isExpanded}>
                            <Divider />
                            <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
                              <JsonViewer
                                data={step.input}
                                title="输入参数"
                                color={theme.palette.primary.main}
                              />

                              {/* 箭头指示 */}
                              {(step.input && step.output) && (
                                <Box sx={{ display: 'flex', justifyContent: 'center', my: 1, opacity: 0.3 }}>
                                  <ArrowForwardIcon sx={{ transform: 'rotate(90deg)' }} />
                                </Box>
                              )}

                              <JsonViewer
                                data={step.output}
                                title="输出结果"
                                color={theme.palette.success.main}
                              />

                              {step.data_sources && Object.keys(step.data_sources).length > 0 && (
                                <JsonViewer
                                  data={step.data_sources}
                                  title="参考数据源"
                                  color={theme.palette.info.main}
                                />
                              )}

                              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                  {step.started_at && `开始: ${new Date(step.started_at).toLocaleTimeString()}`}
                                  {step.finished_at && ` · 结束: ${new Date(step.finished_at).toLocaleTimeString()}`}
                                </Typography>
                              </Box>
                            </Box>
                          </Collapse>
                        </Paper>
                      </Box>
                    </Box>
                  </Fade>
                );
              })}
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default AgentWorkflowVisualization;
