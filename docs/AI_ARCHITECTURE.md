# AI Architecture - TRINETRA Phase 4

## Overview

TrinetraMind is a provider-agnostic AI layer that provides security-focused AI capabilities through specialized workflows. It abstracts away the underlying AI provider (Ollama, HuggingFace, GGUF, Custom API) and provides context-aware responses for security operations.

## Architecture Components

### 1. Provider Layer (`ai/providers/`)

**Factory Pattern** (`ai/providers/factory.py`):
- Singleton provider instance with caching
- Supports: Ollama, HuggingFace, Local GGUF, Custom API
- Health check capability for each provider

**Provider Implementations**:
- `ollama.py` - Local Ollama server (default, uses llama3.2:3b)
- `huggingface.py` - HuggingFace Inference API
- `local_gguf.py` - Local GGUF model files
- `custom_api.py` - External API (OpenAI-compatible)

### 2. Context Builder (`ai/context_builder.py`)

Provides context enrichment for different workflows:
- **Alert Context**: Full alert details, severity, timestamps, related logs
- **Narrative Context**: Multiple alerts with timeline
- **Incident Context**: Incident details with linked alerts and metrics
- **Platform Stats**: Dashboard statistics for general queries

### 3. TrinetraMind Orchestrator (`ai/trinetra_mind.py`)

Main AI orchestration with 5 specialized workflows:

1. **Explain Alert** - Plain English explanation of security alerts
2. **Generate Playbook** - Step-by-step remediation instructions
3. **Build Narrative** - Chronological attack story from multiple alerts
4. **Threat Hunt** - Convert natural language to search queries
5. **Generate Incident Report** - Professional incident documentation
6. **Chat** - General conversation (context-aware)

### 4. Backend API (`backend/api/ai.py`)

RESTful endpoints with SSE streaming:
- `GET /ai/health` - Provider health check
- `GET /ai/workflows` - List available workflows
- `POST /ai/explain-alert` - Explain single alert (SSE)
- `POST /ai/playbook` - Generate playbook (SSE)
- `POST /ai/narrative` - Build attack narrative (SSE)
- `POST /ai/threat-hunt` - Parse & execute hunt query
- `POST /ai/incident-report` - Generate report (SSE)
- `POST /ai/chat` - General chat (SSE)

### 5. Conversation Store (`backend/services/in_memory.py`)

In-memory session storage:
- Session creation/management
- Message history per session
- Auto-cleanup of old sessions

## Frontend Integration

### SSE Client (`frontend/src/utils/sseClient.js`)
- Handles Server-Sent Events for streaming responses
- Automatic JSON parsing of SSE data format
- Abort controller support for cancellation

### Store State (`frontend/src/store/useStore.js`)
```javascript
{
  aiSessionId: string,      // Current session ID
  aiHealth: object,         // { status, provider, model, latency }
  aiPanelOpen: boolean,     // Panel visibility
  aiContext: object,        // { alertId, alertIds, incidentId, workflow }
}
```

### TrinetraMind Component (`frontend/src/components/ai/TrinetraMind.jsx`)
- Workflow selector sidebar
- Context-aware prompts
- Streaming response display
- Markdown rendering support

## Data Flow

```
User Input → Frontend → SSE → Backend API → TrinetraMind → Context Builder
                                                            ↓
                                                      Provider (Ollama/HF/GGUF)
                                                            ↓
                                    SSE Stream ← Response
```

## Configuration (`backend/config.py`)

```python
ai_provider = "ollama"           # Provider choice
ollama_base_url = "http://localhost:11434"
ollama_model = "llama3.2:3b"     # Default model
hf_model = "microsoft/phi-3"    # HuggingFace model
gguf_model_path = "./models/"   # Local GGUF path
custom_api_url = ""             # OpenAI-compatible endpoint
custom_api_key = ""             # API key
```

## Prompt Templates (`ai/prompts/`)

Security-focused prompts designed for:
- Minimal hallucinations
- Actionable recommendations
- Proper markdown formatting
- Severity-aware responses

## Security & Privacy

- **Local Processing**: Default Ollama runs locally - no data leaves the network
- **No Cloud APIs**: Phase 4 intentionally excludes OpenAI/Anthropic
- **Context Isolation**: Alert data only used for specific queries
- **Session Cleanup**: Old conversation sessions auto-expire

## Testing

See `PHASE4_TESTING.md` for:
- Manual testing procedures
- API endpoint verification
- SSE streaming validation
- Workflow-specific tests