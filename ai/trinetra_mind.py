import logging
import json
import os
from typing import AsyncGenerator, List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ai.providers.factory import get_provider
from ai.context_builder import get_context_builder
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def load_prompt_template(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    template_path = os.path.join(prompts_dir, f'{name}.txt')
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            return f.read()
    
    return ""


class TrinetraMind:
    """AI assistant orchestrator for Trinetra."""
    
    def __init__(self):
        self.provider = get_provider()
        self.context_builder = get_context_builder()
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompt templates."""
        self.system_prompt = load_prompt_template('system')
        self.alert_explain_template = load_prompt_template('alert_explain')
        self.playbook_template = load_prompt_template('playbook')
        self.narrative_template = load_prompt_template('narrative')
        self.threat_hunt_template = load_prompt_template('threat_hunt')
        self.incident_report_template = load_prompt_template('incident_report')
        self.chat_template = load_prompt_template('chat')
    
    async def explain_alert(self, alert_id: int, db: Session) -> AsyncGenerator[str, None]:
        """Explain an alert in plain English."""
        context = self.context_builder.build_alert_context(alert_id, db)
        
        if 'error' in context:
            yield f"Error: {context['error']}"
            return
        
        prompt = self._build_alert_explain_prompt(context)
        
        try:
            async for chunk in self.provider.stream(prompt, system=self.system_prompt):
                yield chunk
        except Exception as e:
            logger.error(f"Explain alert error: {e}")
            yield f"Error: {str(e)}"
    
    async def generate_playbook(self, alert_id: int, db: Session) -> AsyncGenerator[str, None]:
        """Generate a remediation playbook."""
        context = self.context_builder.build_alert_context(alert_id, db)
        
        if 'error' in context:
            yield f"Error: {context['error']}"
            return
        
        prompt = self._build_playbook_prompt(context)
        
        try:
            async for chunk in self.provider.stream(prompt, system=self.system_prompt):
                yield chunk
        except Exception as e:
            logger.error(f"Playbook error: {e}")
            yield f"Error: {str(e)}"
    
    async def build_narrative(self, alert_ids: List[int], db: Session) -> AsyncGenerator[str, None]:
        """Create attack narrative from multiple alerts."""
        context = self.context_builder.build_narrative_context(alert_ids, db)
        
        if 'error' in context:
            yield f"Error: {context['error']}"
            return
        
        prompt = self._build_narrative_prompt(context)
        
        try:
            async for chunk in self.provider.stream(prompt, system=self.system_prompt):
                yield chunk
        except Exception as e:
            logger.error(f"Narrative error: {e}")
            yield f"Error: {str(e)}"
    
    async def parse_threat_hunt(self, query: str) -> Dict[str, Any]:
        """Parse threat hunt query into structured filters."""
        if not self.threat_hunt_template:
            prompt = f"""Convert this query to JSON filters.
Query: {query}
Respond with JSON only."""
        else:
            prompt = self.threat_hunt_template.format(query=query)
        
        try:
            response = ""
            async for chunk in self.provider.generate(prompt, system=self.system_prompt):
                response += chunk
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
                return result
            else:
                return {
                    'filters': {},
                    'explanation': 'Could not parse query',
                    'estimated_result_size': 'small',
                }
        except Exception as e:
            logger.error(f"Threat hunt parse error: {e}")
            return {
                'filters': {},
                'explanation': f'Error: {str(e)}',
                'estimated_result_size': 'small',
            }
    
    async def generate_incident_report(self, incident_id: int, db: Session) -> AsyncGenerator[str, None]:
        """Generate incident report."""
        context = self.context_builder.build_incident_context(incident_id, db)
        
        if 'error' in context:
            yield f"Error: {context['error']}"
            return
        
        prompt = self._build_incident_report_prompt(context)
        
        try:
            async for chunk in self.provider.stream(prompt, system=self.system_prompt):
                yield chunk
        except Exception as e:
            logger.error(f"Incident report error: {e}")
            yield f"Error: {str(e)}"
    
    async def chat(
        self,
        session_id: str,
        user_message: str,
        history: List[Dict],
        db: Session
    ) -> AsyncGenerator[str, None]:
        """General chat with context awareness."""
        platform_context = self.context_builder.build_platform_context(db)
        
        prompt = self._build_chat_prompt(user_message, history, platform_context)
        
        try:
            async for chunk in self.provider.stream(prompt, system=self.system_prompt):
                yield chunk
        except Exception as e:
            logger.error(f"Chat error: {e}")
            yield f"Error: {str(e)}"
    
    def _build_alert_explain_prompt(self, context: Dict) -> str:
        """Build alert explanation prompt."""
        if self.alert_explain_template:
            alert_json = json.dumps(context.get('alert', {}), indent=2)
            return self.alert_explain_template.format(
                alert_data=alert_json, # Legacy support
                alert_json=alert_json,
                related_alerts=json.dumps(context.get('related_alerts', []), indent=2),
                asset_info=json.dumps(context.get('asset_info', {}), indent=2),
                severity=context.get('alert', {}).get('severity', 3),
                tactic_name=context.get('mitre_details', {}).get('tactic', 'Unknown'),
                technique=context.get('mitre_details', {}).get('technique', 'Unknown'),
                technique_name=context.get('mitre_details', {}).get('name', 'Unknown'),
            )
        
        alert = context.get('alert', {})
        return f"""You are TrinetraMind, a senior SOC analyst.

Explain this security alert:

Alert: {alert.get('rule_name')}
Severity: {alert.get('severity')}/5
Source IP: {alert.get('source_ip')}
MITRE: {alert.get('mitre_tactic')} - {alert.get('mitre_technique')}
Evidence: {alert.get('evidence', 'N/A')}

Provide analysis in:
1. What Happened
2. Severity Justification  
3. MITRE ATT&CK Context
4. Risk Assessment
5. Recommended Actions"""
    
    def _build_playbook_prompt(self, context: Dict) -> str:
        """Build playbook prompt."""
        if self.playbook_template:
            alert_json = json.dumps(context.get('alert', {}), indent=2)
            return self.playbook_template.format(
                alert_data=alert_json, # Legacy support
                alert_json=alert_json,
            )
        
        alert = context.get('alert', {})
        return f"""Generate a remediation playbook:

Alert: {alert.get('rule_name')}
Severity: {alert.get('severity')}
Source: {alert.get('source_ip')}

Include:
1. Immediate Containment
2. Investigation Steps
3. Eradication
4. Recovery
5. Lessons Learned"""
    
    def _build_narrative_prompt(self, context: Dict) -> str:
        """Build narrative prompt."""
        if self.narrative_template:
            alerts = context.get('alerts', [])
            alerts_json = json.dumps(alerts, indent=2, default=str)
            return self.narrative_template.format(
                alert_data=alerts_json, # Legacy support
                alerts_json=alerts_json,
                start_time=context.get('start_time', ''),
                end_time=context.get('end_time', ''),
            )
        
        alerts = context.get('alerts', [])
        timeline = "\n".join([
            f"- {a.get('timestamp')}: {a.get('rule_name')} from {a.get('source_ip')}"
            for a in alerts
        ])
        return f"""Create attack narrative from these alerts:

{timeline}

Format:
- Attack Summary
- Timeline
- Kill Chain Stages
- Attribution Hints
- Current Status
- Next Steps"""
    
    def _build_incident_report_prompt(self, context: Dict) -> str:
        """Build incident report prompt."""
        if self.incident_report_template:
            incident_json = json.dumps(context.get('incident', {}), indent=2)
            return self.incident_report_template.format(
                incident_data=incident_json, # Legacy support
                incident_json=incident_json,
                alerts_json=json.dumps(context.get('alerts', []), indent=2, default=str),
                assets_json=json.dumps(context.get('assets', []), indent=2),
                incident_title=context.get('incident', {}).get('title', 'Security Incident'),
            )
        
        incident = context.get('incident', {})
        return f"""Generate incident report:

Title: {incident.get('title')}
Severity: {incident.get('severity')}
Status: {incident.get('status')}

Include:
1. Executive Summary
2. Timeline
3. Technical Analysis
4. IOCs
5. MITRE Mapping
6. Recommendations"""
    
    def _build_chat_prompt(
        self,
        user_message: str,
        history: List[Dict],
        platform_context: Dict
    ) -> str:
        """Build chat prompt with context."""
        if self.chat_template:
            return self.chat_template.format(
                platform_context=json.dumps(platform_context, indent=2),
                history="\n".join([
                    f"{msg['role']}: {msg['content'][:200]}"
                    for msg in history[-10:]
                ]),
                user_message=user_message,
            )
        
        history_str = "\n".join([
            f"{msg['role']}: {msg['content'][:200]}"
            for msg in history[-10:]
        ])
        return f"""Platform context:
- Active alerts: {platform_context.get('active_alerts_count', 0)}
- Critical in last hour: {platform_context.get('critical_alerts_last_hour', 0)}
- Top techniques: {platform_context.get('top_mitre_techniques', [])}

Conversation:
{history_str}

User: {user_message}

Respond helpfully and technically."""