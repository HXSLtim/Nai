'use client';

import { useEffect, useRef, useCallback } from 'react';
import { Chip, Typography } from '@mui/material';
import { api } from '@/lib/api';

interface AutoSaverProps {
  novelId: number;
  chapterId: number | null;
  title: string;
  content: string;
  lastSavedTitle: string;
  lastSavedContent: string;
  onSaved: (savedAt: Date) => void;
  onError: (error: string) => void;
  autoSaveDelay?: number;
}

export default function AutoSaver({
  novelId,
  chapterId,
  title,
  content,
  lastSavedTitle,
  lastSavedContent,
  onSaved,
  onError,
  autoSaveDelay = 5000,
}: AutoSaverProps) {
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isSavingRef = useRef(false);

  const hasUnsavedChanges = title !== lastSavedTitle || content !== lastSavedContent;

  const performAutoSave = useCallback(async () => {
    if (!chapterId || isSavingRef.current || !hasUnsavedChanges) {
      return;
    }

    if (!title.trim() || !content.trim()) {
      return; // 不保存空内容
    }

    isSavingRef.current = true;

    try {
      await api.updateChapter(novelId, chapterId, {
        title: title.trim(),
        content: content.trim(),
      });
      onSaved(new Date());
    } catch (err) {
      onError(err instanceof Error ? err.message : '自动保存失败');
    } finally {
      isSavingRef.current = false;
    }
  }, [novelId, chapterId, title, content, hasUnsavedChanges, onSaved, onError]);

  // 设置自动保存定时器
  useEffect(() => {
    if (!hasUnsavedChanges) {
      return;
    }

    // 清除之前的定时器
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    // 设置新的定时器
    autoSaveTimerRef.current = setTimeout(() => {
      performAutoSave();
    }, autoSaveDelay);

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [hasUnsavedChanges, performAutoSave, autoSaveDelay]);

  // 组件卸载时清理定时器
  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, []);

  // 页面失去焦点时立即保存
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '您有未保存的更改，确定要离开吗？';
        // 尝试立即保存
        performAutoSave();
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden && hasUnsavedChanges) {
        performAutoSave();
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [hasUnsavedChanges, performAutoSave]);

  if (!hasUnsavedChanges) {
    return null;
  }

  return (
    <Chip
      label="自动保存中..."
      size="small"
      color="info"
      sx={{
        animation: 'pulse 2s infinite',
        '@keyframes pulse': {
          '0%': { opacity: 1 },
          '50%': { opacity: 0.5 },
          '100%': { opacity: 1 },
        },
      }}
    />
  );
}
