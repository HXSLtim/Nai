'use client';

import { useState, useEffect, useRef } from 'react';
import { Box, Typography, Chip, Paper, Fade } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';

interface TypewriterDisplayProps {
  /** 正在生成的文本 */
  currentText: string;
  /** 当前正在生成的Agent名称 */
  currentAgent?: string;
  /** 当前生成状态 */
  status?: 'thinking' | 'generating' | 'done';
  /** 显示标签 */
  label?: string;
  /** 最大高度 */
  maxHeight?: number;
  /** 简洁模式：不显示外框和标题栏 */
  simpleMode?: boolean;
}

/**
 * 打字机效果显示组件
 * 逐字显示AI生成的内容，并提供流畅的视觉反馈
 */
export default function TypewriterDisplay({
  currentText,
  currentAgent,
  status = 'done',
  label = 'AI生成内容',
  maxHeight = 200,
  simpleMode = false,
}: TypewriterDisplayProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const typingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastLengthRef = useRef(0);

  useEffect(() => {
    // 新文本开始生成
    if (currentText.length > 0 && lastLengthRef.current === 0) {
      setDisplayedText('');
      setIsTyping(true);
      lastLengthRef.current = currentText.length;

      // 清除旧的定时器
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }

      // 开始打字机效果
      let index = 0;
      typingIntervalRef.current = setInterval(() => {
        if (index < currentText.length) {
          setDisplayedText(prev => prev + currentText.charAt(index));
          index++;
        } else {
          setIsTyping(false);
          if (typingIntervalRef.current) {
            clearInterval(typingIntervalRef.current);
          }
        }
      }, 20); // 加快打字速度
    } else if (currentText.length > lastLengthRef.current) {
      // 追加文本
      const newText = currentText.slice(lastLengthRef.current);
      setIsTyping(true);

      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }

      let index = 0;
      typingIntervalRef.current = setInterval(() => {
        if (index < newText.length) {
          setDisplayedText(prev => prev + newText.charAt(index));
          index++;
        } else {
          setIsTyping(false);
          if (typingIntervalRef.current) {
            clearInterval(typingIntervalRef.current);
          }
        }
      }, 10); // 追加时更快

      lastLengthRef.current = currentText.length;
    } else if (currentText.length === 0 && lastLengthRef.current > 0) {
      // 文本被清空
      setDisplayedText('');
      lastLengthRef.current = 0;
      setIsTyping(false);

      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
    }

    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
    };
  }, [currentText]);

  if (!currentText && !displayedText) {
    return null;
  }

  if (simpleMode) {
    return (
      <Box
        sx={{
          p: 1.5,
          maxHeight,
          overflow: 'auto',
          bgcolor: 'grey.50',
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'divider',
          position: 'relative',
        }}
      >
        <Typography
          variant="body2"
          sx={{
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6,
            fontFamily: '"Noto Serif SC", serif',
            color: 'text.primary',
          }}
        >
          {displayedText}
          {isTyping && (
            <Box
              component="span"
              sx={{
                display: 'inline-block',
                width: '2px',
                height: '1em',
                bgcolor: 'primary.main',
                ml: 0.5,
                animation: 'blink 1s infinite',
                '@keyframes blink': {
                  '0%, 50%': { opacity: 1 },
                  '51%, 100%': { opacity: 0 },
                },
              }}
            />
          )}
        </Typography>
      </Box>
    );
  }

  return (
    <Fade in={true}>
      <Paper
        elevation={2}
        sx={{
          mb: 2,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: status === 'generating' ? 'primary.300' : 'divider',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            borderColor: 'primary.main',
          },
        }}
      >
        {/* 标题栏 */}
        <Box
          sx={{
            p: 2,
            bgcolor: status === 'generating' ? 'primary.50' : 'grey.50',
            borderBottom: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <SmartToyIcon
              fontSize="small"
              color={status === 'generating' ? 'primary' : 'success'}
              sx={{
                animation: status === 'generating' ? 'pulse 1.5s infinite' : 'none',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.6 },
                  '100%': { opacity: 1 },
                },
              }}
            />
            <Typography variant="subtitle2" fontWeight={600}>
              {label}
            </Typography>
            {status === 'generating' && (
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
                  },
                }}
              />
            )}
            {status === 'thinking' && (
              <Chip label="思考中" size="small" color="warning" />
            )}
          </Box>
          {currentAgent && (
            <Chip
              label={`Agent: ${currentAgent}`}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </Box>

        {/* 内容区域 */}
        <Box
          sx={{
            p: 2,
            maxHeight,
            overflow: 'auto',
            bgcolor: 'background.paper',
            position: 'relative',
          }}
        >
          <Typography
            variant="body2"
            sx={{
              whiteSpace: 'pre-wrap',
              lineHeight: 1.6,
              fontFamily: '"Noto Serif SC", serif',
              position: 'relative',
            }}
          >
            {displayedText}
            {isTyping && (
              <Box
                component="span"
                sx={{
                  display: 'inline-block',
                  width: '2px',
                  height: '1em',
                  bgcolor: 'primary.main',
                  ml: 0.5,
                  animation: 'blink 1s infinite',
                  '@keyframes blink': {
                    '0%, 50%': { opacity: 1 },
                    '51%, 100%': { opacity: 0 },
                  },
                }}
              />
            )}
          </Typography>
        </Box>

        {/* 统计信息 */}
        <Box
          sx={{
            p: 1.5,
            bgcolor: 'grey.50',
            borderTop: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            {currentText.length} 字
          </Typography>
          {status === 'generating' && (
            <Typography variant="caption" color="primary" sx={{ fontWeight: 500 }}>
              正在生成...
            </Typography>
          )}
        </Box>
      </Paper>
    </Fade>
  );
}
