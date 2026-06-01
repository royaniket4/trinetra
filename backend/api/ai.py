import json
import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.ai import (
    AlertExplainRequest,
    PlaybookRequest,
    NarrativeRequest,
    ThreatHuntRequest,
    IncidentReportRequest,
    ChatRequest,
    AIHealthResponse,
    ThreatHuntResponse,
    ThreatHuntFilters,
    WorkflowListResponse,
    WorkflowInfo,
)
from ai.trinetra_mind import TrinetraMind
from ai.context_builder import get_context_builder
from ai.providers.factory import get_provider
from backend.services.conversation_store import (
    get_history,
    add_message,
    clear_session,
    create_session,
)
from backend.models.alert import Alert
from backend.models.incident import Incident
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/ai", tags=["AI"])

_workflows = [
    WorkflowInfo(
        id="explain",
        name="Explain Alert",
        description="Get detailed analysis of a security alert",
        requires_input="alert_id",
    ),
    WorkflowInfo(
        id="playbook",
        name="Generate Playbook",
        description="Create incident response playbook for an alert",
        requires_input="alert_id",
    ),
    WorkflowInfo(
        id="narrative",
        name="Build Narrative",
        description="Create chronological attack story from multiple alerts",
        requires_input="alert_ids",
    ),
    WorkflowInfo(
        id="threat_hunt",
        name="Threat Hunt",
        description="Convert natural language to search queries",
        requires_input="query",
    ),
    WorkflowInfo(
        id="incident_report",
        name="Incident Report",
        description="Generate professional incident report",
        requires_input="incident_id",
    ),
    WorkflowInfo(
        id="chat",
        name="Chat",
        description="General conversation with AI assistant",
        requires_input="message",
    ),
]


async def get_mind() -> TrinetraMind:
    """Get TrinetraMind instance."""
    return TrinetraMind()


@router.get("/health", response_model=AIHealthResponse)
async def health_check():
    """Check AI provider health status."""
    start = time.time()
    provider = get_provider()
    
    try:
        is_available = await provider.health_check()
        latency = int((time.time() - start) * 1000)
        
        models = []
        if hasattr(provider, 'list_models'):
            try:
                models = await provider.list_models()
            except Exception:
                pass
        
        return AIHealthResponse(
            provider=settings.ai_provider,
            model=settings.ollama_model,
            status="healthy" if is_available else "unavailable",
            latency_ms=latency,
            available_models=models,
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return AIHealthResponse(
            provider=settings.ai_provider,
            model=settings.ollama_model,
            status="error",
            latency_ms=None,
        )


@router.get("/models")
async def list_models():
    """List available models from the AI provider."""
    provider = get_provider()
    if hasattr(provider, 'list_models'):
        try:
            models = await provider.list_models()
            return {"models": models, "current": settings.ollama_model}
        except Exception as e:
            return {"models": [], "current": settings.ollama_model, "error": str(e)}
    return {"models": [], "current": settings.ollama_model, "error": "Provider does not support listing models"}


@router.get("/workflows", response_model=WorkflowListResponse)
async def list_workflows():
    """Get list of available AI workflows."""
    return WorkflowListResponse(workflows=_workflows)


@router.post("/explain-alert")
async def explain_alert(request: AlertExplainRequest, db: Session = Depends(get_db)):
    """Explain an alert using AI with SSE streaming."""
    alert = db.query(Alert).filter(Alert.id == request.alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    mind = await get_mind()
    context_builder = get_context_builder()
    
    async def generate():
        try:
            async for token in mind.explain_alert(request.alert_id, db):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Explain alert error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/playbook")
async def generate_playbook(request: PlaybookRequest, db: Session = Depends(get_db)):
    """Generate remediation playbook with SSE streaming."""
    alert = db.query(Alert).filter(Alert.id == request.alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    mind = await get_mind()
    
    async def generate():
        try:
            async for token in mind.generate_playbook(request.alert_id, db):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Playbook error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/narrative")
async def build_narrative(request: NarrativeRequest, db: Session = Depends(get_db)):
    """Build attack narrative from multiple alerts."""
    if not request.alert_ids:
        raise HTTPException(status_code=400, detail="No alert IDs provided")
    
    alerts = db.query(Alert).filter(Alert.id.in_(request.alert_ids)).all()
    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found")
    
    mind = await get_mind()
    
    async def generate():
        try:
            async for token in mind.build_narrative(request.alert_ids, db):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Narrative error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/threat-hunt", response_model=ThreatHuntResponse)
async def threat_hunt(request: ThreatHuntRequest, db: Session = Depends(get_db)):
    """Parse threat hunt query and execute (non-streaming)."""
    mind = await get_mind()
    
    try:
        result = await mind.parse_threat_hunt(request.query)
        
        filters = result.get('filters', {})
        # Only pass known fields to avoid Pydantic validation errors from LLM hallucinations
        known_filter_fields = {
            'event_type', 'geo_country', 'severity_min',
            'time_window_hours', 'source_ip_pattern', 'username_pattern', 'mitre_technique'
        }
        safe_filters = {k: v for k, v in filters.items() if k in known_filter_fields}
        filters_obj = ThreatHuntFilters(**safe_filters)
        
        return ThreatHuntResponse(
            filters=filters_obj,
            explanation=result.get('explanation', ''),
            estimated_result_size=result.get('estimated_result_size', 'medium'),
            results=result.get('results', []),
            count=len(result.get('results', [])),
        )
    except Exception as e:
        logger.error(f"Threat hunt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incident-report")
async def generate_incident_report(request: IncidentReportRequest, db: Session = Depends(get_db)):
    """Generate incident report with SSE streaming."""
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    linked_alerts = db.query(Alert).filter(Alert.incident_id == request.incident_id).all()
    
    mind = await get_mind()
    
    async def generate():
        try:
            async for token in mind.generate_incident_report(request.incident_id, db):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Incident report error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat with AI assistant."""
    history = get_history(request.session_id)
    add_message(request.session_id, "user", request.message)
    
    mind = await get_mind()
    
    async def generate():
        try:
            full_response = ""
            async for token in mind.chat(request.session_id, request.message, history, db):
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
            
            add_message(request.session_id, "assistant", full_response)
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Chat error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get conversation history for a session."""
    return {"history": get_history(session_id)}


@router.delete("/chat/{session_id}")
async def delete_chat(session_id: str):
    """Clear conversation history for a session."""
    clear_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@router.post("/chat/new-session")
async def new_session():
    """Create a new chat session."""
    session_id = create_session()
    return {"session_id": session_id}