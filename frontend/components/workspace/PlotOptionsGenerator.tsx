'use client';

import { useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import WarningIcon from '@mui/icons-material/Warning';
import { api } from '@/lib/api';

interface PlotOption {
  id: number;
  title: string;
  summary: string;
  impact?: string | null;
  risk?: string | null;
}

interface PlotOptionsGeneratorProps {
  novelId: number;
  chapterId: number | null;
  currentContent: string;
  onPlotSelected: (option: PlotOption) => void;
  onError: (error: string) => void;
}

export default function PlotOptionsGenerator({
  novelId,
  chapterId,
  currentContent,
  onPlotSelected,
  onError,
}: PlotOptionsGeneratorProps) {
  const [plotOptions, setPlotOptions] = useState<PlotOption[]>([]);
  const [plotOptionsLoading, setPlotOptionsLoading] = useState(false);
  const [selectedPlotOptionId, setSelectedPlotOptionId] = useState<number | null>(null);

  const handleGeneratePlotOptions = useCallback(async () => {
    if (!chapterId) {
      onError('未找到当前章节');
      return;
    }

    if (!currentContent.trim()) {
      onError('章节内容为空，无法生成剧情选项');
      return;
    }

    setPlotOptionsLoading(true);
    setPlotOptions([]);
    setSelectedPlotOptionId(null);

    try {
      const result = await api.getPlotOptions({
        novel_id: novelId,
        chapter_id: chapterId,
        current_content: currentContent,
        num_options: 4,
      });

      setPlotOptions(result.options);
    } catch (err) {
      onError(err instanceof Error ? err.message : '生成剧情选项失败');
    } finally {
      setPlotOptionsLoading(false);
    }
  }, [novelId, chapterId, currentContent, onError]);

  const handleSelectPlotOption = useCallback((option: PlotOption) => {
    setSelectedPlotOptionId(option.id);
    onPlotSelected(option);
  }, [onPlotSelected]);

  const getRiskColor = (risk: string | null | undefined) => {
    if (!risk) return 'default';
    const lowerRisk = risk.toLowerCase();
    if (lowerRisk.includes('高') || lowerRisk.includes('high')) return 'error';
    if (lowerRisk.includes('中') || lowerRisk.includes('medium')) return 'warning';
    return 'success';
  };

  const getImpactColor = (impact: string | null | undefined) => {
    if (!impact) return 'default';
    const lowerImpact = impact.toLowerCase();
    if (lowerImpact.includes('重大') || lowerImpact.includes('major')) return 'error';
    if (lowerImpact.includes('中等') || lowerImpact.includes('moderate')) return 'warning';
    return 'info';
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
          <Typography variant="subtitle2">剧情走向</Typography>
          <Button
            size="small"
            variant="outlined"
            startIcon={<TrendingUpIcon />}
            onClick={handleGeneratePlotOptions}
            disabled={plotOptionsLoading || !chapterId}
          >
            {plotOptionsLoading ? '生成中...' : '生成选项'}
          </Button>
        </Box>
        <Divider sx={{ my: 1 }} />

        {plotOptionsLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress size={24} />
            <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
              AI正在分析当前剧情，生成可能的发展方向...
            </Typography>
          </Box>
        )}

        {plotOptions.length > 0 ? (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                基于当前章节内容，AI为您生成了以下剧情发展选项。选择一个方向来指导后续写作。
              </Typography>
            </Alert>

            <List>
              {plotOptions.map((option) => (
                <ListItem key={option.id} disablePadding sx={{ mb: 1 }}>
                  <ListItemButton
                    selected={selectedPlotOptionId === option.id}
                    onClick={() => handleSelectPlotOption(option)}
                    sx={{
                      border: '1px solid',
                      borderColor: selectedPlotOptionId === option.id ? 'primary.main' : 'divider',
                      borderRadius: 1,
                      '&:hover': {
                        borderColor: 'primary.main',
                      },
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <LightbulbIcon color="primary" fontSize="small" />
                          <Typography variant="subtitle2" fontWeight="medium">
                            {option.title}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {option.summary}
                          </Typography>
                          
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {option.impact && (
                              <Chip
                                label={`影响: ${option.impact}`}
                                size="small"
                                color={getImpactColor(option.impact) as any}
                                variant="outlined"
                              />
                            )}
                            {option.risk && (
                              <Chip
                                label={`风险: ${option.risk}`}
                                size="small"
                                color={getRiskColor(option.risk) as any}
                                variant="outlined"
                                icon={<WarningIcon fontSize="small" />}
                              />
                            )}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>

            {selectedPlotOptionId && (
              <Alert severity="success" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  已选择剧情方向。AI续写时将参考此选项来发展故事情节。
                </Typography>
              </Alert>
            )}
          </Box>
        ) : !plotOptionsLoading ? (
          <Typography variant="body2" color="text.secondary">
            基于当前章节内容，AI将为您生成多个可能的剧情发展方向，帮助您选择最合适的故事走向。
          </Typography>
        ) : null}
      </CardContent>
    </Card>
  );
}
