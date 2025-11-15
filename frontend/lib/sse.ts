export type SSEEvent =
  | { type: 'chunk'; content: string }
  | { type: 'metadata'; data: any }
  | { type: 'done' }
  | { type: string; [key: string]: any };

export interface SSECallbacks {
  /** 收到任意原始事件时的回调 */
  onEvent?: (event: SSEEvent) => void;
  /** 收到文本块事件时的回调 */
  onChunk?: (content: string) => void;
  /** 收到元数据事件时的回调 */
  onMetadata?: (metadata: any) => void;
  /** 收到完成事件或流结束时的回调 */
  onDone?: () => void;
}

/**
 * 通用 SSE 解析工具
 *
 * 约定后端以 `data: { json }` 形式推送，每个事件一行，以 `\n\n` 分隔。
 * 事件结构形如：
 * - { "type": "chunk", "content": "..." }
 * - { "type": "metadata", "data": { ... } }
 * - { "type": "done" }
 */
export async function readSSEFromResponse(
  res: Response,
  callbacks: SSECallbacks,
): Promise<void> {
  if (!res.body) {
    throw new Error('SSE 响应没有 body');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let receivedDone = false;

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        // 如果流正常结束但没有收到 done 事件，说明连接异常中断
        if (!receivedDone) {
          console.warn('SSE 流异常中断：未收到完成事件');
        }
        callbacks.onDone?.();
        break;
      }

      // 累积当前 chunk
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      // 保留最后一行（可能是不完整的 JSON）
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = line.slice(6);

        try {
          const json = JSON.parse(payload) as SSEEvent;
          callbacks.onEvent?.(json);

          if (json.type === 'chunk' && typeof (json as any).content === 'string') {
            callbacks.onChunk?.((json as any).content);
          } else if (json.type === 'metadata') {
            callbacks.onMetadata?.((json as any).data);
          } else if (json.type === 'done') {
            receivedDone = true;
            callbacks.onDone?.();
            return;
          } else if (json.type === 'error') {
            // 处理后端发送的错误事件
            const errorMsg = (json as any).message || '未知错误';
            console.error('SSE 后端错误:', errorMsg);
            throw new Error(`SSE 后端错误: ${errorMsg}`);
          }
        } catch (e) {
          // 解析失败时仅在控制台打印，不打断整个流
          // eslint-disable-next-line no-console
          if (e instanceof Error && e.message.startsWith('SSE 后端错误')) {
            throw e;
          }
          console.error('解析 SSE 数据失败:', e, line);
        }
      }
    }
  } catch (e) {
    // 确保调用 onDone，让前端知道流已结束（无论成功还是失败）
    if (!receivedDone) {
      callbacks.onDone?.();
    }
    throw e;
  }
}
