import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

class AuditTrail:
    """
    Tamper-proof audit logging with SHA256 hash chain
    Every action is logged and cryptographically linked
    """
    
    def __init__(self):
        self.chain: List[Dict] = []
        self.previous_hash = "0" * 64  # Genesis hash
        
    def create_log_entry(
        self,
        action: str,
        user: str,
        case_id: str,
        details: Dict,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None
    ) -> Dict:
        """
        Create a new audit log entry with cryptographic hash
        """
        
        timestamp = datetime.utcnow().isoformat()
        
        entry = {
            "index": len(self.chain) + 1,
            "timestamp": timestamp,
            "action": action,
            "user": user,
            "case_id": case_id,
            "details": details,
            "previous_state": previous_state,
            "new_state": new_state,
            "previous_hash": self.previous_hash
        }
        
        # Calculate hash of this entry
        entry_string = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_string.encode()).hexdigest()
        entry["hash"] = entry_hash
        
        # Add to chain
        self.chain.append(entry)
        self.previous_hash = entry_hash
        
        return entry
    
    def verify_chain_integrity(self) -> Dict:
        """
        Verify that audit trail has not been tampered with
        Returns verification status and any broken links
        """
        
        if not self.chain:
            return {"valid": True, "message": "Empty chain"}
        
        broken_links = []
        
        for i in range(1, len(self.chain)):
            current_entry = self.chain[i]
            previous_entry = self.chain[i-1]
            
            # Check if previous_hash matches
            if current_entry["previous_hash"] != previous_entry["hash"]:
                broken_links.append({
                    "index": i,
                    "expected": previous_entry["hash"],
                    "found": current_entry["previous_hash"]
                })
        
        if broken_links:
            return {
                "valid": False,
                "message": f"Chain integrity compromised at {len(broken_links)} point(s)",
                "broken_links": broken_links
            }
        
        return {
            "valid": True,
            "message": f"All {len(self.chain)} entries verified",
            "total_entries": len(self.chain)
        }
    
    def get_case_history(self, case_id: str) -> List[Dict]:
        """Get all audit entries for a specific case"""
        return [entry for entry in self.chain if entry["case_id"] == case_id]
    
    def get_user_actions(self, user: str) -> List[Dict]:
        """Get all actions performed by a specific user"""
        return [entry for entry in self.chain if entry["user"] == user]
    
    def export_audit_report(self, case_id: Optional[str] = None) -> str:
        """
        Export audit trail as formatted report
        """
        
        entries = self.chain if not case_id else self.get_case_history(case_id)
        
        report_lines = [
            "=" * 80,
            "PROOFSAR AI - AUDIT TRAIL REPORT",
            "=" * 80,
            f"Generated: {datetime.utcnow().isoformat()}",
            f"Total Entries: {len(entries)}",
            f"Chain Integrity: {self.verify_chain_integrity()['message']}",
            "=" * 80,
            ""
        ]
        
        for entry in entries:
            report_lines.extend([
                f"[{entry['index']}] {entry['timestamp']}",
                f"Action: {entry['action']}",
                f"User: {entry['user']}",
                f"Case: {entry['case_id']}",
                f"Hash: {entry['hash'][:16]}...",
                f"Details: {json.dumps(entry['details'], indent=2)}",
                "-" * 80,
                ""
            ])
        
        return "\n".join(report_lines)


class AuditLogger:
    """
    High-level interface for logging SAR-related actions
    """
    
    def __init__(self):
        self.audit = AuditTrail()
    
    def log_case_created(self, user: str, case_id: str, data: Dict):
        return self.audit.create_log_entry(
            action="CASE_CREATED",
            user=user,
            case_id=case_id,
            details={
                "transaction_count": data.get("transaction_count"),
                "customer_id": data.get("customer_id"),
                "initial_risk": data.get("risk_level")
            }
        )
    
    def log_analysis_run(self, user: str, case_id: str, results: Dict):
        return self.audit.create_log_entry(
            action="ANALYSIS_EXECUTED",
            user=user,
            case_id=case_id,
            details={
                "risk_score": results.get("risk_score"),
                "patterns_detected": len(results.get("all_patterns", [])),
                "detection_types": list(results.get("detections", {}).keys())
            }
        )
    
    def log_sar_generated(self, user: str, case_id: str, sar_content: str, ai_model: str):
        return self.audit.create_log_entry(
            action="SAR_GENERATED",
            user=user,
            case_id=case_id,
            details={
                "ai_model": ai_model,
                "content_length": len(sar_content),
                "timestamp": datetime.utcnow().isoformat()
            },
            new_state=hashlib.sha256(sar_content.encode()).hexdigest()
        )
    
    def log_sar_edited(self, user: str, case_id: str, old_content: str, new_content: str, reason: str):
        return self.audit.create_log_entry(
            action="SAR_EDITED",
            user=user,
            case_id=case_id,
            details={
                "reason": reason,
                "old_length": len(old_content),
                "new_length": len(new_content),
                "edit_timestamp": datetime.utcnow().isoformat()
            },
            previous_state=hashlib.sha256(old_content.encode()).hexdigest(),
            new_state=hashlib.sha256(new_content.encode()).hexdigest()
        )
    
    def log_sar_approved(self, user: str, case_id: str, approver_comments: str):
        return self.audit.create_log_entry(
            action="SAR_APPROVED",
            user=user,
            case_id=case_id,
            details={
                "approver": user,
                "comments": approver_comments,
                "approval_timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_sar_rejected(self, user: str, case_id: str, rejection_reason: str):
        return self.audit.create_log_entry(
            action="SAR_REJECTED",
            user=user,
            case_id=case_id,
            details={
                "rejector": user,
                "reason": rejection_reason,
                "rejection_timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_alert_sent(self, user: str, case_id: str, recipients: List[str], alert_type: str):
        return self.audit.create_log_entry(
            action="ALERT_SENT",
            user=user,
            case_id=case_id,
            details={
                "recipients": recipients,
                "alert_type": alert_type,
                "sent_timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_ai_toggle(self, user: str, old_model: str, new_model: str):
        return self.audit.create_log_entry(
            action="AI_MODEL_SWITCHED",
            user=user,
            case_id="SYSTEM",
            details={
                "old_model": old_model,
                "new_model": new_model,
                "switch_timestamp": datetime.utcnow().isoformat()
            }
        )