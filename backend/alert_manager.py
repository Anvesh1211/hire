"""
AlertManager - Centralized alert management for ProofSAR AI
Handles alert persistence and session state management
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertManager:
    """
    Centralized alert management system
    Maintains alert state and provides session-safe operations
    """
    
    def __init__(self):
        self.alerts: List[Dict] = []
        self.alert_counter = 0
        logger.info("AlertManager initialized")
    
    def create_alert(self, alert_type: str, case_id: str, title: str, 
                    message: str, severity: str = "medium", 
                    metadata: Optional[Dict] = None) -> Dict:
        """
        Create a new alert and store it in memory
        
        Args:
            alert_type: Type of alert (HIGH_RISK, SAR_GENERATED, etc.)
            case_id: Associated case ID
            title: Alert title
            message: Alert message
            severity: Alert severity (low, medium, high, critical)
            metadata: Additional alert metadata
            
        Returns:
            Created alert dictionary
        """
        try:
            self.alert_counter += 1
            
            alert = {
                "alert_id": f"ALERT-{self.alert_counter:04d}",
                "type": alert_type,
                "case_id": case_id,
                "title": title,
                "message": message,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "ACTIVE",
                "metadata": metadata or {},
                "acknowledged": False,
                "acknowledged_by": None,
                "acknowledged_at": None
            }
            
            self.alerts.append(alert)
            logger.info(f"🚨 Alert created: {alert['alert_id']} - {alert_type} for case {case_id}")
            
            return alert
            
        except Exception as e:
            logger.error(f"❌ Error creating alert: {e}")
            raise
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: Alert ID to acknowledge
            user: User acknowledging the alert
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for alert in self.alerts:
                if alert["alert_id"] == alert_id:
                    alert["acknowledged"] = True
                    alert["acknowledged_by"] = user
                    alert["acknowledged_at"] = datetime.utcnow().isoformat()
                    alert["status"] = "ACKNOWLEDGED"
                    
                    logger.info(f"✅ Alert acknowledged: {alert_id} by {user}")
                    return True
            
            logger.warning(f"⚠️ Alert not found for acknowledgment: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error acknowledging alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, user: str, resolution: str = "") -> bool:
        """
        Resolve an alert
        
        Args:
            alert_id: Alert ID to resolve
            user: User resolving the alert
            resolution: Resolution notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for alert in self.alerts:
                if alert["alert_id"] == alert_id:
                    alert["status"] = "RESOLVED"
                    alert["resolved_by"] = user
                    alert["resolved_at"] = datetime.utcnow().isoformat()
                    alert["resolution"] = resolution
                    
                    logger.info(f"✅ Alert resolved: {alert_id} by {user}")
                    return True
            
            logger.warning(f"⚠️ Alert not found for resolution: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error resolving alert: {e}")
            return False
    
    def get_alerts(self, case_id: Optional[str] = None, 
                  severity: Optional[str] = None,
                  status: Optional[str] = None) -> List[Dict]:
        """
        Get alerts with optional filtering
        
        Args:
            case_id: Filter by case ID
            severity: Filter by severity
            status: Filter by status
            
        Returns:
            List of matching alerts
        """
        try:
            filtered_alerts = self.alerts
            
            if case_id:
                filtered_alerts = [a for a in filtered_alerts if a["case_id"] == case_id]
            
            if severity:
                filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]
            
            if status:
                filtered_alerts = [a for a in filtered_alerts if a["status"] == status]
            
            # Sort by timestamp (newest first)
            filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return filtered_alerts
            
        except Exception as e:
            logger.error(f"❌ Error getting alerts: {e}")
            return []
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict]:
        """
        Get a specific alert by ID
        
        Args:
            alert_id: Alert ID to retrieve
            
        Returns:
            Alert dictionary or None if not found
        """
        try:
            for alert in self.alerts:
                if alert["alert_id"] == alert_id:
                    return alert
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting alert by ID: {e}")
            return None
    
    def get_alert_stats(self) -> Dict:
        """
        Get alert statistics
        
        Returns:
            Dictionary with alert statistics
        """
        try:
            total = len(self.alerts)
            
            if total == 0:
                return {
                    "total": 0,
                    "active": 0,
                    "acknowledged": 0,
                    "resolved": 0,
                    "by_severity": {},
                    "by_type": {}
                }
            
            active = len([a for a in self.alerts if a["status"] == "ACTIVE"])
            acknowledged = len([a for a in self.alerts if a["status"] == "ACKNOWLEDGED"])
            resolved = len([a for a in self.alerts if a["status"] == "RESOLVED"])
            
            # Count by severity
            severity_counts = {}
            for alert in self.alerts:
                severity = alert["severity"]
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by type
            type_counts = {}
            for alert in self.alerts:
                alert_type = alert["type"]
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            return {
                "total": total,
                "active": active,
                "acknowledged": acknowledged,
                "resolved": resolved,
                "by_severity": severity_counts,
                "by_type": type_counts,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting alert stats: {e}")
            return {"error": str(e)}
    
    def add_email_result(self, alert_id: str, email_result: Dict) -> bool:
        """
        Add email sending result to an alert
        
        Args:
            alert_id: Alert ID to update
            email_result: Email sending result
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for alert in self.alerts:
                if alert["alert_id"] == alert_id:
                    alert["email_result"] = email_result
                    alert["email_sent_at"] = datetime.utcnow().isoformat()
                    
                    logger.info(f"📧 Email result added to alert: {alert_id}")
                    return True
            
            logger.warning(f"⚠️ Alert not found for email result: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error adding email result: {e}")
            return False
