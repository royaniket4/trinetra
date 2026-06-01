from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from datetime import datetime
from io import BytesIO

from backend.models.incident import Incident
from backend.models.alert import Alert


def generate_incident_pdf(incident: Incident = None, alerts: list[Alert] = None, single_alert: bool = False) -> bytes:
    """Generate a PDF report for an incident or alert."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00E5FF'),
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#00E5FF'),
        spaceBefore=20,
        spaceAfter=10,
    )
    
    normal_style = styles['Normal']
    normal_style.textColor = colors.white
    
    story.append(Paragraph("TRINETRA", title_style))
    story.append(Paragraph("Security Incident Report", title_style))
    story.append(Spacer(1, 20))
    
    if incident:
        story.append(Paragraph(f"Incident ID: {incident.incident_id}", normal_style))
        story.append(Paragraph(f"Title: {incident.title}", normal_style))
        story.append(Paragraph(f"Severity: {incident.severity}/5", normal_style))
        story.append(Paragraph(f"Status: {incident.status}", normal_style))
        story.append(Paragraph(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
        
        if incident.description:
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Paragraph(incident.description, normal_style))
            story.append(Spacer(1, 10))
    
    if single_alert and alerts:
        alert = alerts[0]
        story.append(Paragraph("Alert Details", heading_style))
        story.append(Paragraph(f"Alert ID: {alert.alert_id}", normal_style))
        story.append(Paragraph(f"Rule: {alert.rule_name}", normal_style))
        story.append(Paragraph(f"Severity: {alert.severity}/5", normal_style))
        
        if alert.mitre_tactic:
            story.append(Paragraph(f"MITRE Tactic: {alert.mitre_tactic}", normal_style))
        if alert.mitre_technique:
            story.append(Paragraph(f"MITRE Technique: {alert.mitre_technique}", normal_style))
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("Evidence", heading_style))
        story.append(Paragraph(alert.evidence[:500], normal_style))
        story.append(Spacer(1, 10))
    
    if alerts and len(alerts) > 0:
        story.append(Paragraph("Associated Alerts", heading_style))
        
        alert_data = [['Alert ID', 'Rule', 'Severity', 'Source IP', 'Time']]
        
        for alert in alerts[:10]:
            alert_data.append([
                alert.alert_id,
                alert.rule_name[:30],
                str(alert.severity),
                alert.source_ip or 'N/A',
                alert.timestamp.strftime('%H:%M'),
            ])
        
        t = Table(alert_data, colWidths=[1.2*inch, 2*inch, 0.7*inch, 1.2*inch, 0.8*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2744')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00E5FF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2d4a7c')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#111827'), colors.HexColor('#1a2744')]),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 20))
    
    story.append(Paragraph("MITRE ATT&CK Mapping", heading_style))
    
    mitre_tactics = {}
    for alert in (alerts or []):
        if alert.mitre_tactic:
            mitre_tactics[alert.mitre_tactic] = mitre_tactics.get(alert.mitre_tactic, 0) + 1
    
    for tactic, count in mitre_tactics.items():
        story.append(Paragraph(f"• {tactic}: {count} related events", normal_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("Recommendations", heading_style))
    story.append(Paragraph("1. Review and contain affected systems immediately", normal_style))
    story.append(Paragraph("2. Update detection rules to prevent similar incidents", normal_style))
    story.append(Paragraph("3. Conduct root cause analysis", normal_style))
    story.append(Paragraph("4. Implement additional monitoring controls", normal_style))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", normal_style))
    story.append(Paragraph("Trinetra AI-Powered Cyber Defense Command Center", normal_style))
    
    doc.build(story)
    buffer.seek(0)
    
    return buffer.getvalue()