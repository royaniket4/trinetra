# Ollama Setup for TrinetraMind AI

## Prerequisites

This guide assumes you have:
- Trinetra SIEM backend running on port 8000
- Node.js/npm for frontend
- Terminal access

## Installation Steps

### macOS / Linux

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Verify installation**:
   ```bash
   ollama --version
   ```

3. **Pull the recommended model**:
   ```bash
   ollama pull llama3.2:3b
   ```

   Note: This model requires ~2GB disk space and works well on systems with 8GB+ RAM.

4. **Verify model is available**:
   ```bash
   ollama list
   ```

5. **Test the model**:
   ```bash
   ollama run llama3.2:3b "Hello, what are you?"
   ```

### Windows

1. **Download Ollama**:
   - Visit https://ollama.com/download
   - Download the Windows installer
   - Run the installer and follow prompts

2. **Pull the model**:
   ```powershell
   ollama pull llama3.2:3b
   ```

3. **Verify**:
   ```powershell
   ollama list
   ```

## Verifying TrinetraMind Connection

Once Ollama is installed and the model is pulled:

1. **Start Ollama service** (if not already running):
   ```bash
   ollama serve
   ```

2. **Verify service is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

   You should see a JSON response listing available models.

3. **Test via Trinetra API**:
   ```bash
   curl http://localhost:8000/api/ai/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "provider": "ollama",
     "model": "llama3.2:3b",
     "latency_ms": 100
   }
   ```

## Troubleshooting

### Ollama not running

If you see "Connection refused" errors:
```bash
# Start Ollama in background
ollama serve &

# Or on Windows, it should auto-start
```

### Model not found

If health check shows "model not found":
```bash
ollama pull llama3.2:3b
```

### Out of memory

If the model fails to load due to memory constraints:
- Close other applications
- Use a smaller model: `ollama pull llama3.2:1b`
- On Windows, check Task Manager for memory usage

### Port already in use

If port 11434 is busy:
```bash
# Check what's using the port
netstat -an | findstr 11434
```

## Model Specifications

| Model | Size | RAM Required | Context |
|-------|------|--------------|---------|
| llama3.2:3b | 2GB | 8GB | 128K |
| llama3.2:1b | 1GB | 4GB | 128K |

Recommended: `llama3.2:3b` for best quality/performance balance.

## Environment Variables

Trinetra uses these settings in `.env`:

```env
# AI Provider (ollama, huggingface, local_gguf, custom_api)
AI_PROVIDER=ollama

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TEMPERATURE=0.3
OLLAMA_MAX_TOKENS=1024
```

## Performance Notes

- First token latency: ~1-3s on 8GB CPU
- Full response: ~5-15s depending on length
- Streaming provides better UX - tokens appear as generated

## Security Notes

- All AI processing happens locally - no data leaves your network
- Model runs entirely on your hardware
- Suitable for air-gapped environments