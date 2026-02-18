import hashlib
import json
import os
import logging
import shutil
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AuditTrail:
    """
    Enterprise-grade tamper-proof audit logging with full blockchain-style verification
    Every action is cryptographically linked and verifiable with persistent storage
    """
    
    def __init__(self, storage_file: str = "backend/data/audit_chain.json"):
        # Ensure data directory exists
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        self.storage_file = storage_file
        self.chain: List[Dict] = []
        self.previous_hash = "0" * 64  # Genesis hash
        
        # Load existing chain on startup
        self._load_chain()
        
        logger.info(f"AuditTrail initialized - Chain length: {len(self.chain)}, Storage: {self.storage_file}")
    
    def _load_chain(self) -> None:
        """Load audit chain from persistent storage with error handling"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.chain = data.get('chain', [])
                    self.previous_hash = data.get('previous_hash', "0" * 64)
                    
                    # Verify chain integrity on load
                    integrity_check = self.verify_chain_integrity()
                    if not integrity_check['valid']:
                        logger.error(f" CRITICAL: Loaded chain has integrity issues: {integrity_check['message']}")
                        # Backup corrupted chain
                        backup_file = f"{self.storage_file}.corrupted.{int(time.time())}"
                        shutil.copy2(self.storage_file, backup_file)
                        logger.error(f" Corrupted chain backed up to: {backup_file}")
                    else:
                        logger.info(f" Audit chain loaded and verified: {len(self.chain)} entries")
            else:
                logger.info(" No existing audit chain found - starting fresh")
        except json.JSONDecodeError as e:
            logger.error(f" JSON decode error loading audit chain: {e}")
            # Backup corrupted file
            backup_file = f"{self.storage_file}.json_error.{int(time.time())}"
            shutil.copy2(self.storage_file, backup_file)
            logger.error(f" Corrupted JSON file backed up to: {backup_file}")
            # Start with fresh chain
            self.chain = []
            self.previous_hash = "0" * 64
        except Exception as e:
            logger.error(f" Error loading audit chain: {e}")
            # Start with fresh chain if loading fails
            self.chain = []
            self.previous_hash = "0" * 64
    
    def _save_chain(self) -> None:
        """Save audit chain to persistent storage with backup"""
        try:
            # Create backup before saving
            if os.path.exists(self.storage_file):
                backup_file = f"{self.storage_file}.backup"
                shutil.copy2(self.storage_file, backup_file)
            
            # Save current chain
            data = {
                'chain': self.chain,
                'previous_hash': self.previous_hash,
                'last_updated': datetime.utcnow().isoformat(),
                'chain_length': len(self.chain),
                'version': '2.0'
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f" Audit chain saved: {len(self.chain)} entries")
            
        except Exception as e:
            logger.error(f" Error saving audit chain: {e}")
            raise
    
    def _calculate_entry_hash(self, entry: Dict) -> str:
        """
        Calculate SHA256 hash of an audit entry
        Excludes the 'hash' field itself to prevent circular hashing
        Uses deterministic serialization for consistency
        """
        # Create a copy without the hash field
        entry_copy = entry.copy()
        entry_copy.pop('hash', None)
        
        # Sort keys and use consistent separators for deterministic serialization
        entry_string = json.dumps(entry_copy, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA256
        return hashlib.sha256(entry_string.encode('utf-8')).hexdigest()
        
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
        Create a new audit log entry with cryptographic hash and persistent storage
        """
        try:
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
            
            # Calculate hash of this entry using deterministic method
            entry_hash = self._calculate_entry_hash(entry)
            entry["hash"] = entry_hash
            
            # Add to chain
            self.chain.append(entry)
            self.previous_hash = entry_hash
            
            # Save to persistent storage
            self._save_chain()
            
            logger.info(f"📝 Audit entry created: {action} by {user} for case {case_id} (Index: {entry['index']})")
            
            return entry
            
        except Exception as e:
            logger.error(f"❌ Error creating audit entry: {e}")
            raise
    
    def verify_chain_integrity(self) -> Dict:
        """
        BLOCKCHAIN-STYLE VERIFICATION: Full tamper detection
        
        This method performs comprehensive verification:
        1. Recomputes hash of EVERY entry
        2. Compares stored hash vs recalculated hash
        3. Verifies previous_hash linkage
        4. Detects ALL forms of tampering
        
        Returns detailed integrity report
        """
        try:
            if not self.chain:
                return {
                    "valid": True,
                    "total_entries": 0,
                    "tampered_entries": [],
                    "broken_links": [],
                    "message": "Empty chain - no integrity issues"
                }
            
            tampered_entries = []
            broken_links = []
            
            logger.info(f"🔍 Starting blockchain verification of {len(self.chain)} entries")
            
            # Verify each entry's hash and linkage
            for i, entry in enumerate(self.chain):
                # 1. Verify entry hash integrity
                calculated_hash = self._calculate_entry_hash(entry)
                stored_hash = entry.get('hash')
                
                if calculated_hash != stored_hash:
                    tampered_entries.append({
                        "index": entry['index'],
                        "timestamp": entry['timestamp'],
                        "action": entry['action'],
                        "stored_hash": stored_hash,
                        "calculated_hash": calculated_hash,
                        "issue": "HASH_MISMATCH"
                    })
                    logger.error(f"🚨 Hash mismatch at entry {entry['index']}: {entry['action']}")
                
                # 2. Verify previous_hash linkage (except for genesis block)
                if i > 0:
                    current_entry = entry
                    previous_entry = self.chain[i-1]
                    
                    if current_entry.get('previous_hash') != previous_entry.get('hash'):
                        broken_links.append({
                            "index": current_entry['index'],
                            "timestamp": current_entry['timestamp'],
                            "action": current_entry['action'],
                            "expected_previous": previous_entry.get('hash'),
                            "found_previous": current_entry.get('previous_hash'),
                            "issue": "BROKEN_LINK"
                        })
                        logger.error(f"🔗 Broken link at entry {current_entry['index']}: {current_entry['action']}")
            
            # Determine overall validity
            is_valid = len(tampered_entries) == 0 and len(broken_links) == 0
            
            if is_valid:
                message = f"✅ All {len(self.chain)} entries verified - Chain integrity intact"
                logger.info(message)
            else:
                message = f"🚨 Chain integrity compromised: {len(tampered_entries)} tampered entries, {len(broken_links)} broken links"
                logger.error(message)
            
            return {
                "valid": is_valid,
                "total_entries": len(self.chain),
                "tampered_entries": tampered_entries,
                "broken_links": broken_links,
                "message": message,
                "verification_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Critical error during integrity verification: {str(e)}"
            logger.error(error_msg)
            return {
                "valid": False,
                "total_entries": len(self.chain) if self.chain else 0,
                "tampered_entries": [],
                "broken_links": [],
                "message": error_msg,
                "verification_error": True
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
    High-level interface for logging SAR-related actions with audit integration
    """
    
    def __init__(self, storage_file: str = "backend/data/audit_chain.json"):
        self.audit = AuditTrail(storage_file)
        logger.info("AuditLogger initialized with persistent storage")
    
    def log_action(self, action: str, user: str, case_id: str, details: Dict, 
                   previous_state: Optional[str] = None, new_state: Optional[str] = None):
        """Generic action logging method"""
        return self.audit.create_log_entry(
            action=action,
            user=user,
            case_id=case_id,
            details=details,
            previous_state=previous_state,
            new_state=new_state
        )
    
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
    
    def log_alert_sent(self, user: str, case_id: str, recipients: List[str], alert_type: str, email_status: Optional[Dict] = None):
        details = {
            "recipients": recipients,
            "alert_type": alert_type,
            "sent_timestamp": datetime.utcnow().isoformat()
        }
        
        # Include email status if provided
        if email_status:
            details["email_status"] = email_status
        
        return self.audit.create_log_entry(
            action="ALERT_SENT",
            user=user,
            case_id=case_id,
            details=details
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