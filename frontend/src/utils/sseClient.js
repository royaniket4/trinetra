export function streamSSE(url, body, onToken, onDone, onError) {
  let controller = null;
  let buffer = '';
  
  const start = async () => {
    try {
      const token = localStorage.getItem('trinetra_token')
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(body),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        onError(new Error(`HTTP ${response.status}: ${errorText}`));
        return;
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          if (buffer.trim()) {
            try {
              const data = JSON.parse(buffer);
              if (data.done) {
                onDone();
              } else if (data.token) {
                onToken(data.token);
              } else if (data.error) {
                onError(new Error(data.error));
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
          break;
        }
        
        buffer += decoder.decode(value, { stream: true });
        
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.done) {
                onDone();
              } else if (data.token) {
                onToken(data.token);
              } else if (data.error) {
                onError(new Error(data.error));
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      onError(error);
    }
  };
  
  const abort = () => {
    if (controller) {
      controller.abort();
    }
  };
  
  start();
  
  return { abort };
}

export const AI_ENDPOINTS = {
  explain: '/api/ai/explain-alert',
  playbook: '/api/ai/playbook',
  narrative: '/api/ai/narrative',
  threatHunt: '/api/ai/threat-hunt',
  report: '/api/ai/incident-report',
  chat: '/api/ai/chat',
  health: '/api/ai/health',
  workflows: '/api/ai/workflows',
  history: (sessionId) => `/api/ai/chat/${sessionId}/history`,
  deleteChat: (sessionId) => `/api/ai/chat/${sessionId}`,
};