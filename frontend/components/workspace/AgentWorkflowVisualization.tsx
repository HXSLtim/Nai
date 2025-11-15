'use client';

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  HourglassEmpty as HourglassEmptyIcon,
  PlayArrow as PlayArrowIcon,
  Memory as MemoryIcon,
  Psychology as PsychologyIcon,
  AutoStories as AutoStoriesIcon,
  VerifiedUser as VerifiedUserIcon,
  Storage as StorageIcon,
  AccountTree as AccountTreeIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material';
import type { AgentWorkflowTrace, AgentWorkflowStep } from '@/types';

interface AgentWorkflowVisualizationProps {
  workflowTrace: AgentWorkflowTrace | null;
  isGenerating?: boolean;
}

// 获取 Agent 类型对应的图标
const getAgentIcon = (type: string) => {
  switch (type) {
    case 'rag':
      return <StorageIcon />;
    case 'llm':
      return <PsychologyIcon />;
    case 'agent':
      return <MemoryIcon />;
    case 'consistency':
      return <VerifiedUserIcon />;
    case 'graph':
      return <AccountTreeIcon />;
    default:
      return <AutoStoriesIcon />;
  }
};

// 获取状态对应的图标
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircleIcon color="success" />;
    case 'failed':
      return <ErrorIcon color="error" />;
    case 'running':
      return <PlayArrowIcon color="primary" />;
    case 'pending':
      return <HourglassEmptyIcon color="disabled" />;
    default:
      return <HourglassEmptyIcon color="disabled" />;
  }
};

// 获取状态对应的颜色
const getStatusColor = (status: string): 'success' | 'error' | 'primary' | 'default' => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'failed':
      return 'error';
    case 'running':
      return 'primary';
    default:
      return 'default';
  }
};

// 格式化时长
const formatDuration = (ms: number | null | undefined): string => {
  if (!ms) return '-';
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
};

const AgentWorkflowVisualization: React.FC<AgentWorkflowVisualizationProps> = ({
  workflowTrace,
  isGenerating = false,
}) => {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [showDetails, setShowDetails] = useState<boolean>(true);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  if (!workflowTrace) return null;

  const steps = workflowTrace.steps || [];
  const totalDuration = steps.reduce((sum, step) => sum + (step.duration_ms || 0), 0);

  const toggleStepExpanded = (stepId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId);
    } else {
      newExpanded.add(stepId);
    }
    setExpandedSteps(newExpanded);
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        {/* 标题栏 */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <AccountTreeIcon color="primary" />
            <Typography variant="h6">Agent 工作流追踪</Typography>
            <Chip
              label={`${steps.length} 个步骤`}
              size="small"
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`总耗时: ${formatDuration(totalDuration)}`}
              size="small"
              color="default"
              variant="outlined"
            />
          </Box>
          <IconButton
            size="small"
            onClick={() => setShowDetails(!showDetails)}
            aria-label="toggle details"
          >
            {showDetails ? <VisibilityOffIcon /> : <VisibilityIcon />}
          </IconButton>
        </Box>

        {/* 工作流摘要 */}
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2" fontWeight="medium">
            {workflowTrace.summary}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            运行ID: {workflowTrace.run_id}
          </Typography>
        </Alert>

        {/* 步骤时间线 */}
        <Collapse in={showDetails}>
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => (
              <Step key={step.id} expanded>
                <StepLabel
                  StepIconComponent={() => getStatusIcon(step.status)}
                  optional={
                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                      <Chip
                        label={step.agent_name}
                        size="small"
                        icon={getAgentIcon(step.type)}
                        variant="outlined"
                      />
                      <Chip
                        label={formatDuration(step.duration_ms)}
                        size="small"
                        color={getStatusColor(step.status)}
                        variant="outlined"
                      />
                    </Box>
                  }
                >
                  <Typography variant="subtitle2" fontWeight="medium">
                    {step.title}
                  </Typography>
                </StepLabel>
                <StepContent>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {step.description}
                  </Typography>

                  {/* 输入输出详情 */}
                  <Accordion
                    expanded={expandedSteps.has(step.id)}
                    onChange={() => toggleStepExpanded(step.id)}
                    sx={{ mb: 1 }}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="caption" fontWeight="medium">
                        查看详细信息
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      {/* 输入参数 */}
                      {Object.keys(step.input).length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="caption" fontWeight="bold" color="primary">
                            输入参数:
                          </Typography>
                          <Box
                            component="pre"
                            sx={{
                              mt: 1,
                              p: 1,
                              bgcolor: 'grey.100',
                              borderRadius: 1,
                              fontSize: '0.75rem',
                              overflow: 'auto',
                              maxHeight: 200,
                            }}
                          >
                            {JSON.stringify(step.input, null, 2)}
                          </Box>
                        </Box>
                      )}

                      {/* 输出结果 */}
                      {Object.keys(step.output).length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="caption" fontWeight="bold" color="success.main">
                            输出结果:
                          </Typography>
                          <Box
                            component="pre"
                            sx={{
                              mt: 1,
                              p: 1,
                              bgcolor: 'grey.100',
                              borderRadius: 1,
                              fontSize: '0.75rem',
                              overflow: 'auto',
                              maxHeight: 200,
                            }}
                          >
                            {JSON.stringify(step.output, null, 2)}
                          </Box>
                        </Box>
                      )}

                      {/* 数据源 */}
                      {Object.keys(step.data_sources).length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="caption" fontWeight="bold" color="info.main">
                            数据源:
                          </Typography>
                          <Box
                            component="pre"
                            sx={{
                              mt: 1,
                              p: 1,
                              bgcolor: 'grey.100',
                              borderRadius: 1,
                              fontSize: '0.75rem',
                              overflow: 'auto',
                              maxHeight: 200,
                            }}
                          >
                            {JSON.stringify(step.data_sources, null, 2)}
                          </Box>
                        </Box>
                      )}

                      {/* LLM 信息 */}
                      {Object.keys(step.llm).length > 0 && (
                        <Box>
                          <Typography variant="caption" fontWeight="bold" color="secondary.main">
                            LLM 配置:
                          </Typography>
                          <Box
                            component="pre"
                            sx={{
                              mt: 1,
                              p: 1,
                              bgcolor: 'grey.100',
                              borderRadius: 1,
                              fontSize: '0.75rem',
                              overflow: 'auto',
                              maxHeight: 200,
                            }}
                          >
                            {JSON.stringify(step.llm, null, 2)}
                          </Box>
                        </Box>
                      )}

                      {/* 时间信息 */}
                      <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        {step.started_at && (
                          <Chip
                            label={`开始: ${new Date(step.started_at).toLocaleTimeString()}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {step.finished_at && (
                          <Chip
                            label={`结束: ${new Date(step.finished_at).toLocaleTimeString()}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default AgentWorkflowVisualization;
