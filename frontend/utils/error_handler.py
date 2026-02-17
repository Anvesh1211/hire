"""
Enterprise Error Handler for ProofSAR AI
Production-grade error handling and logging
"""

import logging
import traceback
import sys
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime
import streamlit as st

# Import the new secrets manager
try:
    from config.secrets import get_secret
except ImportError:
    # Fallback for development
    def get_secret(key: str, default: Any = None) -> Any:
        return default

logger = logging.getLogger(__name__)

class EnterpriseErrorHandler:
    """Enterprise-grade error handling system"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_threshold = 10  # Max errors before showing system warning
        self.critical_errors = []
    
    def handle_exception(self, exc: Exception, context: str = "", user_friendly: bool = True) -> None:
        """Handle exception with appropriate logging and user notification"""
        error_type = type(exc).__name__
        error_message = str(exc)
        error_traceback = traceback.format_exc()
        
        # Log the error
        logger.error(f"Exception in {context}: {error_type}: {error_message}")
        logger.debug(f"Full traceback: {error_traceback}")
        
        # Track error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Check if this is a critical error
        if self._is_critical_error(exc):
            self.critical_errors.append({
                "timestamp": datetime.now(),
                "error_type": error_type,
                "message": error_message,
                "context": context
            })
        
        # Show user-friendly message
        if user_friendly:
            self._show_user_error(exc, context)
        
        # Check error threshold
        if sum(self.error_counts.values()) > self.error_threshold:
            self._show_system_warning()
    
    def _is_critical_error(self, exc: Exception) -> bool:
        """Determine if error is critical"""
        critical_types = [
            'ConnectionError',
            'DatabaseError', 
            'AuthenticationError',
            'PermissionError'
        ]
        return type(exc).__name__ in critical_types
    
    def _show_user_error(self, exc: Exception, context: str) -> None:
        """Show user-friendly error message"""
        error_type = type(exc).__name__
        
        # Map error types to user-friendly messages
        error_messages = {
            'FileNotFoundError': "The requested file was not found. Please check the file path and try again.",
            'PermissionError': "You don't have permission to perform this action. Please contact your administrator.",
            'ConnectionError': "Unable to connect to the server. Please check your internet connection and try again.",
            'ValueError': "Invalid data provided. Please check your input and try again.",
            'KeyError': "Required data is missing. Please ensure all required fields are filled.",
            'TypeError': "Data type mismatch. Please check the format of your input.",
            'MemoryError': "System memory is low. Please try with a smaller dataset or contact support.",
            'TimeoutError': "Operation timed out. Please try again or contact support if the issue persists."
        }
        
        user_message = error_messages.get(error_type, f"An unexpected error occurred: {str(exc)}")
        
        if context:
            user_message = f"Error in {context}: {user_message}"
        
        st.error(user_message)
        
        # Show debug info in development
        if get_secret("SHOW_DEBUG_INFO", False):
            with st.expander("🔍 Technical Details"):
                st.code(f"Error Type: {error_type}\nMessage: {str(exc)}\n\nTraceback:\n{traceback.format_exc()}")
    
    def _show_system_warning(self) -> None:
        """Show system warning when error threshold is exceeded"""
        st.warning("⚠️ System experiencing multiple errors. Some features may be unavailable. Please contact support if issues persist.")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": dict(self.error_counts),
            "critical_errors": len(self.critical_errors),
            "last_critical_error": self.critical_errors[-1] if self.critical_errors else None
        }
    
    def reset_error_counts(self) -> None:
        """Reset error counts"""
        self.error_counts.clear()
        self.critical_errors.clear()

def enterprise_error_handler(context: str = "", show_user_error: bool = True, reraise: bool = False):
    """Decorator for enterprise-grade error handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                error_handler.handle_exception(exc, context or func.__name__, show_user_error)
                
                if reraise:
                    raise
                return None
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_return: Any = None, context: str = "", **kwargs) -> Any:
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        error_handler.handle_exception(exc, context or f"safe_execute({func.__name__})")
        return default_return

class ValidationError(Exception):
    """Custom validation error"""
    pass

class ConfigurationError(Exception):
    """Custom configuration error"""
    pass

class DataProcessingError(Exception):
    """Custom data processing error"""
    pass

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class AuthorizationError(Exception):
    """Custom authorization error"""
    pass

def validate_file_upload(file) -> None:
    """Validate uploaded file"""
    if file is None:
        raise ValidationError("No file uploaded")
    
    if not file.name.endswith('.csv'):
        raise ValidationError("Only CSV files are allowed")
    
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("File size exceeds 10MB limit")

def validate_dataframe(df, required_columns: list) -> None:
    """Validate DataFrame structure"""
    if df is None or df.empty:
        raise ValidationError("No data provided")
    
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValidationError(f"Missing required columns: {', '.join(missing_columns)}")

def validate_risk_score(score: float) -> None:
    """Validate risk score"""
    if not isinstance(score, (int, float)):
        raise ValidationError("Risk score must be a number")
    
    if score < 0 or score > 1:
        raise ValidationError("Risk score must be between 0 and 1")

def validate_case_id(case_id: str) -> None:
    """Validate case ID format"""
    if not case_id:
        raise ValidationError("Case ID cannot be empty")
    
    if not case_id.startswith("SAR-"):
        raise ValidationError("Case ID must start with 'SAR-'")

def validate_email(email: str) -> None:
    """Validate email address"""
    if not email or '@' not in email:
        raise ValidationError("Invalid email address")

def log_user_action(action: str, details: Dict[str, Any] = None) -> None:
    """Log user action for audit trail"""
    user_id = st.session_state.get('user_id', 'unknown')
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "action": action,
        "details": details or {}
    }
    
    logger.info(f"User action: {user_id} - {action} - {details}")

def log_system_event(event: str, severity: str = "INFO", details: Dict[str, Any] = None) -> None:
    """Log system event"""
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "event": event,
        "severity": severity,
        "details": details or {}
    }
    
    if severity == "CRITICAL":
        logger.critical(f"System event: {event} - {details}")
    elif severity == "ERROR":
        logger.error(f"System event: {event} - {details}")
    elif severity == "WARNING":
        logger.warning(f"System event: {event} - {details}")
    else:
        logger.info(f"System event: {event} - {details}")

# Global error handler instance
error_handler = EnterpriseErrorHandler()

def get_error_handler() -> EnterpriseErrorHandler:
    """Get global error handler instance"""
    return error_handler

# Streamlit error handling utilities
def show_error_boundary(func: Callable) -> Callable:
    """Streamlit-specific error boundary decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            st.error("❌ An unexpected error occurred. The issue has been logged and our team has been notified.")
            
            if get_secret("SHOW_DEBUG_INFO", False):
                st.exception(exc)
            else:
                error_handler.handle_exception(exc, func.__name__)
            
            return None
    return wrapper

def handle_streamlit_error() -> None:
    """Handle Streamlit-specific errors"""
    try:
        # Check for common Streamlit issues
        if st.session_state.get('_streamlit_error'):
            st.error("A Streamlit error occurred. Please refresh the page and try again.")
            del st.session_state['_streamlit_error']
    except Exception:
        pass
