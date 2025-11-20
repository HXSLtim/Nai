'use client';

import { useState, useRef, useCallback } from 'react';

interface UseEditHistoryOptions {
  maxHistorySize?: number;
}

interface UseEditHistoryReturn {
  history: string[];
  historyIndex: number;
  canUndo: boolean;
  canRedo: boolean;
  addToHistory: (content: string) => void;
  undo: () => string | null;
  redo: () => string | null;
  clearHistory: (initialContent: string) => void;
}

/**
 * 编辑历史管理Hook（撤销/重做）
 * @param maxHistorySize - 最大历史记录条数（默认100）
 */
export function useEditHistory(
  options: UseEditHistoryOptions = {}
): UseEditHistoryReturn {
  const { maxHistorySize = 100 } = options;

  // 编辑历史
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // 用于标记是否正在应用历史记录（避免循环添加到历史）
  const isApplyingHistoryRef = useRef(false);

  /**
   * 添加到历史记录
   */
  const addToHistory = useCallback(
    (content: string) => {
      if (isApplyingHistoryRef.current) return;

      setHistory((prevHistory) => {
        const newHistory = prevHistory.slice(0, historyIndex + 1);
        newHistory.push(content);

        // 限制历史记录数量
        if (newHistory.length > maxHistorySize) {
          newHistory.shift();
        }

        return newHistory;
      });

      setHistoryIndex((prevIndex) => {
        const newIndex = Math.min(prevIndex + 1, maxHistorySize - 1);
        return newIndex;
      });
    },
    [historyIndex, maxHistorySize]
  );

  /**
   * 撤销
   */
  const undo = useCallback((): string | null => {
    if (historyIndex <= 0) return null;

    isApplyingHistoryRef.current = true;
    const newIndex = historyIndex - 1;
    setHistoryIndex(newIndex);

    // 短暂延迟后重置标记，确保状态更新完成
    setTimeout(() => {
      isApplyingHistoryRef.current = false;
    }, 100);

    return history[newIndex];
  }, [history, historyIndex]);

  /**
   * 重做
   */
  const redo = useCallback((): string | null => {
    if (historyIndex >= history.length - 1) return null;

    isApplyingHistoryRef.current = true;
    const newIndex = historyIndex + 1;
    setHistoryIndex(newIndex);

    // 短暂延迟后重置标记，确保状态更新完成
    setTimeout(() => {
      isApplyingHistoryRef.current = false;
    }, 100);

    return history[newIndex];
  }, [history, historyIndex]);

  /**
   * 清空历史记录
   */
  const clearHistory = useCallback((initialContent: string) => {
    isApplyingHistoryRef.current = false;
    setHistory([initialContent]);
    setHistoryIndex(0);
  }, []);

  // 是否可撤销/重做
  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;

  return {
    history,
    historyIndex,
    canUndo,
    canRedo,
    addToHistory,
    undo,
    redo,
    clearHistory,
  };
}

/**
 * 是否正在应用历史记录的标记Hook
 * 用于避免在应用历史记录时将其添加到历史
 */
export function useIsApplyingHistoryRef() {
  const isApplyingHistoryRef = useRef(false);
  return isApplyingHistoryRef;
}
