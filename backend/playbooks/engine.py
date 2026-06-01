"""Playbook execution engine - runs playbook steps and tracks execution state."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.response_action import ResponseAction
from backend.models.playbook import PlaybookExecution, PlaybookExecutionStep
from backend.models.alert import Alert
from backend.playbooks.registry import get_playbook, find_matching_playbooks

logger = logging.getLogger(__name__)


def generate_action_id() -> str:
    import uuid
    return f"ACT-{uuid.uuid4().hex[:8].upper()}"


def generate_execution_id() -> str:
    import uuid
    return f"EXEC-{uuid.uuid4().hex[:8].upper()}"


class PlaybookEngine:
    """Executes SOAR playbooks step by step."""

    def __init__(self, db: Session):
        self.db = db

    def find_and_trigger(self, alert_id: int) -> List[Dict]:
        """Find matching playbooks for an alert and trigger them."""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return []

        alert_dict = {
            "id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity,
            "source_ip": alert.source_ip,
            "dest_ip": alert.dest_ip,
            "username": alert.username,
            "evidence": alert.evidence,
        }

        playbooks = find_matching_playbooks(alert_dict)
        results = []

        for pb in playbooks:
            result = self.execute_playbook(pb["id"], alert_dict)
            results.append(result)

        return results

    def execute_playbook(self, playbook_id: str, alert_context: Dict) -> Dict:
        """Execute a playbook for a given alert context."""
        playbook = get_playbook(playbook_id)
        if not playbook:
            return {"playbook_id": playbook_id, "status": "error", "error": "Playbook not found"}

        execution = PlaybookExecution(
            execution_id=generate_execution_id(),
            playbook_id=playbook_id,
            playbook_name=playbook["name"],
            triggered_by=f"alert-{alert_context.get('id', 'unknown')}",
            status="running",
            started_at=datetime.utcnow(),
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        steps_results = []
        all_succeeded = True

        for step in playbook["steps"]:
            target = self._resolve_target(step, alert_context)
            if not target:
                logger.warning(f"Could not resolve target for step {step['label']}")
                step_result = {"step": step, "status": "skipped", "reason": "target_not_resolved"}
                steps_results.append(step_result)
                continue

            step_record = PlaybookExecutionStep(
                execution_id=execution.id,
                order=step["order"],
                action_type=step["action_type"],
                target=target,
                label=step["label"],
                status="pending" if step.get("requires_approval") else "executing",
                requires_approval=step.get("requires_approval", False),
            )
            self.db.add(step_record)
            self.db.commit()
            self.db.refresh(step_record)

            if step.get("requires_approval"):
                step_result = {
                    "step": step,
                    "target": target,
                    "status": "pending_approval",
                    "step_record_id": step_record.id,
                }
                steps_results.append(step_result)
                continue

            try:
                action = self._execute_action(
                    action_type=step["action_type"],
                    target=target,
                    trigger_source=f"playbook-{playbook_id}",
                )
                step_record.status = "completed"
                step_record.completed_at = datetime.utcnow()
                self.db.commit()

                step_result = {
                    "step": step,
                    "target": target,
                    "status": "completed",
                    "action_id": action.action_id if action else None,
                }
                steps_results.append(step_result)
            except Exception as e:
                logger.error(f"Step execution failed: {e}")
                step_record.status = "failed"
                step_record.error_message = str(e)
                self.db.commit()
                all_succeeded = False
                steps_results.append({"step": step, "target": target, "status": "failed", "error": str(e)})

        execution.status = "completed" if all_succeeded else "partial_failure"
        execution.completed_at = datetime.utcnow()
        self.db.commit()

        return {
            "execution_id": execution.execution_id,
            "playbook_id": playbook_id,
            "playbook_name": playbook["name"],
            "status": execution.status,
            "steps": steps_results,
        }

    def approve_step(self, step_id: int):
        """Approve a pending step and execute it."""
        step = self.db.query(PlaybookExecutionStep).filter(PlaybookExecutionStep.id == step_id).first()
        if not step or step.status != "pending":
            return {"status": "error", "error": "Step not found or not pending"}

        try:
            execution = self.db.query(PlaybookExecution).filter(PlaybookExecution.id == step.execution_id).first()
            action = self._execute_action(
                action_type=step.action_type,
                target=step.target,
                trigger_source=f"playbook-{execution.playbook_id if execution else 'unknown'}-approved",
            )
            step.status = "completed"
            step.completed_at = datetime.utcnow()
            step.approved_by = "manual"
            self.db.commit()
            return {"status": "completed", "action_id": action.action_id if action else None}
        except Exception as e:
            step.status = "failed"
            step.error_message = str(e)
            self.db.commit()
            return {"status": "failed", "error": str(e)}

    def deny_step(self, step_id: int):
        """Deny a pending step."""
        step = self.db.query(PlaybookExecutionStep).filter(PlaybookExecutionStep.id == step_id).first()
        if not step:
            return {"status": "error", "error": "Step not found"}
        step.status = "denied"
        self.db.commit()
        return {"status": "denied"}

    def _resolve_target(self, step: Dict, alert_context: Dict) -> Optional[str]:
        """Resolve a step target from alert context."""
        target_from = step.get("target_from")
        if target_from:
            return alert_context.get(target_from)
        return step.get("target")

    def _execute_action(self, action_type: str, target: str, trigger_source: str = "playbook") -> Optional[ResponseAction]:
        """Execute a single response action."""
        action = ResponseAction(
            action_id=generate_action_id(),
            action_type=action_type,
            target=target,
            triggered_by="playbook",
            trigger_source=trigger_source,
            status="completed",
            details=self._generate_details(action_type, target),
            executed_at=datetime.utcnow(),
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def _generate_details(self, action_type: str, target: str) -> str:
        """Generate human-readable details for an action."""
        details_map = {
            "block_ip": f"Blocked IP address: {target}",
            "disable_user": f"Disabled user account: {target}",
            "quarantine_file": f"Quarantined file: {target}",
            "isolate_endpoint": f"Isolated endpoint: {target}",
            "notify": f"Notification sent to: {target}",
        }
        return details_map.get(action_type, f"Executed {action_type} on {target}")
