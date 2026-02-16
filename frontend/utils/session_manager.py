"""
Enterprise Session Manager for ProofSAR AI
Production-grade session state management
"""

import streamlit as st
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)

class SessionManager:
    """Enterprise-grade session state manager"""
    
    def __init__(self):
        self.session_timeout = 3600  # 1 hour default
        self.session_key_prefix = "proofsar_"
    
    def initialize_session(self) -> None:
        """Initialize session state with default values"""
        if 'session_initialized' not in st.session_state:
            st.session_state.session_initialized = True
            st.session_state.session_start = datetime.now()
            st.session_state.last_activity = datetime.now()
            
            # User session data
            st.session_state.user_id = "demo_user"
            st.session_state.user_role = "analyst"
            st.session_state.user_permissions = ["read", "write", "analyze"]
            
            # Application state
            st.session_state.current_page = "🏠 Dashboard"
            st.session_state.case_id = None
            st.session_state.uploaded_df = None
            st.session_state.detection_results = None
            st.session_state.reasoning_results = None
            st.session_state.generated_sar = None
            st.session_state.sar_status = "Not Generated"
            
            # UI state
            st.session_state.theme = "light"
            st.session_state.notifications = []
            
            logger.info(f"Session initialized for user: {st.session_state.user_id}")
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        st.session_state.last_activity = datetime.now()
    
    def is_session_valid(self) -> bool:
        """Check if session is still valid"""
        if 'session_start' not in st.session_state:
            return False
        
        last_activity = st.session_state.get('last_activity', datetime.now())
        time_diff = (datetime.now() - last_activity).total_seconds()
        
        return time_diff < self.session_timeout
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            "user_id": st.session_state.get('user_id', 'unknown'),
            "user_role": st.session_state.get('user_role', 'unknown'),
            "session_start": st.session_state.get('session_start'),
            "last_activity": st.session_state.get('last_activity'),
            "current_page": st.session_state.get('current_page'),
            "case_id": st.session_state.get('case_id'),
            "session_duration": str(datetime.now() - st.session_state.get('session_start', datetime.now()))
        }
    
    def set_user_data(self, user_id: str, role: str, permissions: list) -> None:
        """Set user session data"""
        st.session_state.user_id = user_id
        st.session_state.user_role = role
        st.session_state.user_permissions = permissions
        self.update_activity()
        logger.info(f"User session updated: {user_id} ({role})")
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in st.session_state.get('user_permissions', [])
    
    def set_page(self, page_name: str) -> None:
        """Set current page"""
        st.session_state.current_page = page_name
        self.update_activity()
    
    def set_case_data(self, case_id: str, detection_results: Dict = None, reasoning_results: Dict = None) -> None:
        """Set case-related data"""
        st.session_state.case_id = case_id
        if detection_results:
            st.session_state.detection_results = detection_results
        if reasoning_results:
            st.session_state.reasoning_results = reasoning_results
        self.update_activity()
    
    def get_case_data(self) -> Dict[str, Any]:
        """Get current case data"""
        return {
            "case_id": st.session_state.get('case_id'),
            "detection_results": st.session_state.get('detection_results'),
            "reasoning_results": st.session_state.get('reasoning_results'),
            "sar_status": st.session_state.get('sar_status', 'Not Generated')
        }
    
    def clear_case_data(self) -> None:
        """Clear current case data"""
        st.session_state.case_id = None
        st.session_state.detection_results = None
        st.session_state.reasoning_results = None
        st.session_state.generated_sar = None
        st.session_state.sar_status = "Not Generated"
        self.update_activity()
        logger.info("Case data cleared from session")
    
    def add_notification(self, message: str, notification_type: str = "info") -> None:
        """Add notification to session"""
        notification = {
            "id": self._generate_notification_id(),
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now(),
            "read": False
        }
        
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        st.session_state.notifications.append(notification)
        
        # Keep only last 50 notifications
        if len(st.session_state.notifications) > 50:
            st.session_state.notifications = st.session_state.notifications[-50:]
    
    def get_notifications(self, unread_only: bool = False) -> list:
        """Get notifications"""
        notifications = st.session_state.get('notifications', [])
        
        if unread_only:
            notifications = [n for n in notifications if not n['read']]
        
        return sorted(notifications, key=lambda x: x['timestamp'], reverse=True)
    
    def mark_notification_read(self, notification_id: str) -> None:
        """Mark notification as read"""
        notifications = st.session_state.get('notifications', [])
        for notification in notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                break
    
    def mark_all_notifications_read(self) -> None:
        """Mark all notifications as read"""
        notifications = st.session_state.get('notifications', [])
        for notification in notifications:
            notification['read'] = True
    
    def clear_notifications(self) -> None:
        """Clear all notifications"""
        st.session_state.notifications = []
    
    def set_theme(self, theme: str) -> None:
        """Set UI theme"""
        if theme in ['light', 'dark']:
            st.session_state.theme = theme
            self.update_activity()
    
    def get_theme(self) -> str:
        """Get current theme"""
        return st.session_state.get('theme', 'light')
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export session data for backup/analysis"""
        session_data = {
            "session_info": self.get_session_info(),
            "case_data": self.get_case_data(),
            "notifications": self.get_notifications(),
            "theme": self.get_theme(),
            "export_timestamp": datetime.now().isoformat()
        }
        return session_data
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        timestamp = datetime.now().isoformat()
        message = f"{timestamp}_{len(st.session_state.get('notifications', []))}"
        return hashlib.md5(message.encode()).hexdigest()[:8]
    
    def cleanup_expired_data(self) -> None:
        """Clean up expired session data"""
        # Clear old notifications (older than 7 days)
        notifications = st.session_state.get('notifications', [])
        cutoff_date = datetime.now() - timedelta(days=7)
        
        filtered_notifications = [
            n for n in notifications 
            if datetime.fromisoformat(n['timestamp'].replace('Z', '+00:00')) > cutoff_date
        ]
        
        st.session_state.notifications = filtered_notifications
    
    def validate_session_integrity(self) -> Dict[str, Any]:
        """Validate session data integrity"""
        validation_results = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check required session variables
        required_vars = ['session_initialized', 'user_id', 'user_role']
        for var in required_vars:
            if var not in st.session_state:
                validation_results["issues"].append(f"Missing required session variable: {var}")
                validation_results["is_valid"] = False
        
        # Check session timeout
        if not self.is_session_valid():
            validation_results["issues"].append("Session has expired")
            validation_results["is_valid"] = False
        
        # Check data consistency
        case_id = st.session_state.get('case_id')
        detection_results = st.session_state.get('detection_results')
        
        if case_id and not detection_results:
            validation_results["warnings"].append("Case ID exists but no detection results")
        
        if detection_results and not case_id:
            validation_results["warnings"].append("Detection results exist but no case ID")
        
        return validation_results

# Global session manager instance
session_manager = SessionManager()

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    return session_manager
