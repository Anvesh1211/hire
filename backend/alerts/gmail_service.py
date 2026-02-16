from typing import List, Dict
from datetime import datetime
import json

class GmailAlertService:
    """
    Professional email alert system for SAR workflow
    In production, this would use real SMTP
    For demo, we simulate and log alerts
    """
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sent_alerts = []  # Store for demo purposes
        
    def send_high_risk_alert(self, case_id: str, risk_score: float, recipients: List[str]) -> Dict:
        """
        Send immediate alert for high-risk cases
        """
        
        subject = f"🚨 ProofSAR Alert: HIGH RISK Case {case_id}"
        
        body = f"""
URGENT: High Risk SAR Case Detected
{'=' * 50}

Case ID: {case_id}
Risk Score: {risk_score:.1%}
Severity: CRITICAL
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Immediate review needed
- Review deadline: 24 hours
- Escalation to compliance head

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
Do not reply to this email.
        """
        
        alert_record = {
            "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
            "type": "HIGH_RISK",
            "case_id": case_id,
            "subject": subject,
            "body": body,
            "recipients": recipients,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "SENT"
        }
        
        self.sent_alerts.append(alert_record)
        
        # In production: Actually send via SMTP
        # self._send_smtp(subject, body, recipients)
        
        return alert_record
    
    def send_pending_review_alert(self, case_id: str, assigned_to: str, recipients: List[str]) -> Dict:
        """
        Send alert for pending review
        """
        
        subject = f"📋 ProofSAR: Review Pending - Case {case_id}"
        
        body = f"""
SAR Review Pending
{'=' * 50}

Case ID: {case_id}
Assigned To: {assigned_to}
Status: AWAITING APPROVAL
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Review generated SAR narrative
- Verify evidence linkage
- Approve or request modifications

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
        """
        
        alert_record = {
            "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
            "type": "PENDING_REVIEW",
            "case_id": case_id,
            "subject": subject,
            "body": body,
            "recipients": recipients,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "SENT"
        }
        
        self.sent_alerts.append(alert_record)
        return alert_record
    
    def send_approval_notification(self, case_id: str, approver: str, recipients: List[str]) -> Dict:
        """
        Send notification when SAR is approved
        """
        
        subject = f"✅ ProofSAR: SAR Approved - Case {case_id}"
        
        body = f"""
SAR Approved and Filed
{'=' * 50}

Case ID: {case_id}
Approved By: {approver}
Status: FILED WITH FIU-IND
Timestamp: {datetime.utcnow().isoformat()}

Next Steps:
- SAR transmitted to Financial Intelligence Unit
- Case archived in compliance records
- 5-year retention period activated

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
        """
        
        alert_record = {
            "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
            "type": "APPROVED",
            "case_id": case_id,
            "subject": subject,
            "body": body,
            "recipients": recipients,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "SENT"
        }
        
        self.sent_alerts.append(alert_record)
        return alert_record
    
    def send_rejection_notification(self, case_id: str, rejector: str, reason: str, recipients: List[str]) -> Dict:
        """
        Send notification when SAR is rejected
        """
        
        subject = f"❌ ProofSAR: SAR Rejected - Case {case_id}"
        
        body = f"""
SAR Rejected - Revision Required
{'=' * 50}

Case ID: {case_id}
Rejected By: {rejector}
Reason: {reason}
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Review rejection reason
- Revise SAR narrative
- Re-submit for approval

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
        """
        
        alert_record = {
            "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
            "type": "REJECTED",
            "case_id": case_id,
            "subject": subject,
            "body": body,
            "recipients": recipients,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "SENT"
        }
        
        self.sent_alerts.append(alert_record)
        return alert_record
    
    def get_alert_history(self, case_id: str = None) -> List[Dict]:
        """
        Retrieve alert history
        """
        if case_id:
            return [alert for alert in self.sent_alerts if alert["case_id"] == case_id]
        return self.sent_alerts
    
    def get_alert_stats(self) -> Dict:
        """
        Get statistics about sent alerts
        """
        return {
            "total_sent": len(self.sent_alerts),
            "by_type": {
                "HIGH_RISK": len([a for a in self.sent_alerts if a["type"] == "HIGH_RISK"]),
                "PENDING_REVIEW": len([a for a in self.sent_alerts if a["type"] == "PENDING_REVIEW"]),
                "APPROVED": len([a for a in self.sent_alerts if a["type"] == "APPROVED"]),
                "REJECTED": len([a for a in self.sent_alerts if a["type"] == "REJECTED"])
            },
            "last_sent": self.sent_alerts[-1]["sent_at"] if self.sent_alerts else None
        }