# Phase 4 Testing Guide - TrinetraMind AI

## Prerequisites

1. **Ollama Running**: Start Ollama server
   ```bash
   ollama serve
   # Or on Windows: ollama serve (in PowerShell)
   ```

2. **Model Available**: Ensure llama3.2:3b is pulled
   ```bash
   ollama pull llama3.2:3b
   ```

3. **Backend Running**: Start TRINETRA backend
   ```bash
   cd trinetra
   python run_backend.py
   ```

4. **Frontend Running**: Start Vite dev server
   ```bash
   cd trinetra/frontend
   npm run dev
   ```

## API Endpoint Testing

### 1. Health Check

```bash
curl http://localhost:8000/api/ai/health
```

Expected response:
```json
{
  "provider": "ollama",
  "model": "llama3.2:3b",
  "status": "healthy",
  "latency_ms": 150
}
```

### 2. List Workflows

```bash
curl http://localhost:8000/api/ai/workflows
```

Expected: Array of 6 workflow objects

### 3. Explain Alert (SSE)

```bash
curl -N -X POST http://localhost:8000/api/ai/explain-alert \
  -H "Content-Type: application/json" \
  -d '{"alert_id": 1}'
```

Expected: Streaming SSE tokens with plain English explanation

### 4. Generate Playbook (SSE)

```bash
curl -N -X POST http://localhost:8000/api/ai/playbook \
  -H "Content-Type: application/json" \
  -d '{"alert_id": 1}'
```

Expected: Streaming SSE with step-by-step remediation

### 5. Threat Hunt Query

```bash
curl -X POST http://localhost:8000/api/ai/threat-hunt \
  -H "Content-Type: application/json" \
  -d '{"query": "show failed SSH logins from Russia"}'
```

Expected: JSON with parsed filters and search results

### 6. Chat (SSE)

```bash
curl -N -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "message": "what are the top threats?"}'
```

Expected: Streaming SSE response

### 7. New Session

```bash
curl -X POST http://localhost:8000/api/ai/chat/new-session
```

Expected: `{"session_id": "uuid..."}`

## Frontend Testing

### 1. Dashboard AI Panel

1. Navigate to Dashboard
2. Click Brain icon in top right
3. Verify TrinetraMind panel opens
4. Check health indicator shows green (if Ollama running)

### 2. Alert Detail AI Button

1. Go to Alerts page
2. Click on any alert
3. Verify "Ask TrinetraMind" button appears
4. Click button → Select "Explain" or "Playbook"
5. Verify panel opens with context pre-filled

### 3. Workflow Selection

1. In TrinetraMind panel, click each workflow
2. Verify:
   - Explain Alert → Requires alert context
   - Remediation Playbook → Requires alert context
   - Attack Narrative → Requires multiple alerts
   - Threat Hunt → Free text input
   - Incident Report → Requires incident context
   - General Chat → Default mode

### 4. Streaming Response

1. Select "General Chat" workflow
2. Type: "What is the current threat level?"
3. Submit and verify:
   - Loading indicator appears
   - Response streams in token by token
   - Markdown renders correctly (headers, lists, code blocks)
   - Final response is complete

### 5. Context Passing

1. Go to Alerts → Select alert #1
2. Click "Ask TrinetraMind" → "Explain Alert"
3. Verify panel shows "Alert: #1" in context area
4. Submit question - should explain that specific alert

## Workflow-Specific Tests

### Explain Alert Test

**Input**: Alert with high severity SQL injection
**Expected**: Plain English explanation covering:
- What triggered the alert
- Why it's concerning
- Potential impact
- Priority level

### Playbook Test

**Input**: Alert #1 (any)
**Expected**: Step-by-step remediation:
1. Initial containment steps
2. Investigation actions
3. Remediation steps
4. Post-incident actions

### Narrative Test

**Input**: 3-5 alerts from same attack sequence
**Expected**: Chronological story:
- Initial compromise vector
- Lateral movement steps
- Final impact
- TTMC ( Tactics, Techniques, Mitigation)

### Threat Hunt Test

**Input**: "show failed SSH from 192.168.1.0/24"
**Expected**: Parsed filters:
- action: "failed"
- source_ip subnet match
- service: "SSH"

## Troubleshooting

### Ollama Not Running

```
Error: Connection refused to localhost:11434
```

**Fix**: Run `ollama serve` in terminal

### Model Not Available

```
Error: model 'llama3.2:3b' not found
```

**Fix**: Run `ollama pull llama3.2:3b`

### SSE Not Streaming

If responses come back immediately (no streaming):
1. Check browser DevTools → Network → filter "SSE"
2. Verify `text/event-stream` content-type
3. Check for nginx buffering (if applicable)

### Frontend Panel Not Opening

1. Check browser console for errors
2. Verify `toggleAiPanel` action in store
3. Check TrinetraMind component mounts correctly

## Performance Benchmarks

| Workflow | Expected Latency (llama3.2:3b) |
|----------|-------------------------------|
| Explain Alert | 2-5 seconds |
| Playbook | 3-8 seconds |
| Narrative | 5-15 seconds |
| Threat Hunt | 1-3 seconds |
| Chat | 2-5 seconds |

*Latency depends on prompt complexity and system resources*