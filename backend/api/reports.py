from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.incident import Incident
from backend.models.alert import Alert
from backend.services.pdf_generator import generate_incident_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/incidents/{incident_id}")
async def get_incident_report(incident_id: int, db: Session = Depends(get_db)):
    """Generate PDF report for an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    alerts = db.query(Alert).filter(Alert.incident_id == incident_id).all()
    
    pdf_bytes = generate_incident_pdf(incident, alerts)
    
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=incident_{incident.incident_id}.pdf"
        },
    )


@router.get("/alerts/{alert_id}")
async def get_alert_report(alert_id: int, db: Session = Depends(get_db)):
    """Generate PDF report for a single alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    pdf_bytes = generate_incident_pdf(None, [alert], single_alert=True)
    
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=alert_{alert.alert_id}.pdf"
        },
    )