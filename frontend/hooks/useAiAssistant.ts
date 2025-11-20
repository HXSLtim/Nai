'use client';

import { useRef, useCallback } from 'react';

export interface AiWritingAssistantHandle {
  triggerContinue: () => void;
}

/**
 * AI写作助手Ref管理Hook
 * 用于从父组件触发AI续写操作
 */
export function useAiAssistant() {
  const aiAssistantRef = useRef<AiWritingAssistantHandle>(null);

  /**
   * 触发AI续写
   */
  const triggerContinue = useCallback(() => {
    if (aiAssistantRef.current) {
      aiAssistantRef.current.triggerContinue();
    }
  }, []);

  return {
    aiAssistantRef,
    triggerContinue,
  };
}
