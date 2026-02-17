"""
Enterprise Secrets Management for ProofSAR AI
Production-safe configuration with fallback mechanisms
"""

import os
import streamlit as st
import logging
from typing import Any, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SecretConfig:
    """Configuration for secret management"""
    show_debug_info: bool = False
    jwt_secret_key: str = "demo-secret-key-change-in-production"
    database_url: str = "sqlite:///./proofsar.db"
    email_username: str = ""
    email_password: str = ""
    gemini_api_key: str = ""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True

class SecretsManager:
    """
    Enterprise-grade secrets management with multiple fallback layers
    Priority: 1. Streamlit secrets, 2. Environment variables, 3. Defaults
    """
    
    def __init__(self):
        self._config = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration with fallback mechanism"""
        try:
            self._config = SecretConfig()
            
            # Try Streamlit secrets first (production deployment)
            if self._has_streamlit_secrets():
                self._load_from_streamlit_secrets()
                logger.info("Loaded configuration from Streamlit secrets")
            
            # Fallback to environment variables
            else:
                self._load_from_environment()
                logger.info("Loaded configuration from environment variables")
            
            # Apply defaults for missing values
            self._apply_defaults()
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            # Use safe defaults if everything fails
            self._config = SecretConfig()
            logger.warning("Using default configuration")
    
    def _has_streamlit_secrets(self) -> bool:
        """Check if Streamlit secrets are available"""
        try:
            # This will raise StreamlitSecretNotFoundError if no secrets exist
            secrets = st.secrets
            # Try to access a key to verify secrets are loaded
            _ = secrets.get("SHOW_DEBUG_INFO", None)
            return True
        except st.errors.StreamlitSecretNotFoundError:
            return False
        except Exception:
            return False
    
    def _load_from_streamlit_secrets(self):
        """Load configuration from Streamlit secrets"""
        secrets = st.secrets
        
        # Debug settings
        self._config.show_debug_info = secrets.get("SHOW_DEBUG_INFO", False)
        
        # Security settings
        self._config.jwt_secret_key = secrets.get("JWT_SECRET_KEY", self._config.jwt_secret_key)
        
        # Database settings
        self._config.database_url = secrets.get("DATABASE_URL", self._config.database_url)
        
        # Email settings
        self._config.email_username = secrets.get("EMAIL_USERNAME", "")
        self._config.email_password = secrets.get("EMAIL_PASSWORD", "")
        self._config.smtp_server = secrets.get("SMTP_SERVER", self._config.smtp_server)
        self._config.smtp_port = int(secrets.get("SMTP_PORT", self._config.smtp_port))
        self._config.use_tls = secrets.get("EMAIL_USE_TLS", self._config.use_tls)
        
        # AI settings
        self._config.gemini_api_key = secrets.get("GEMINI_API_KEY", "")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Debug settings
        self._config.show_debug_info = os.getenv("SHOW_DEBUG_INFO", "false").lower() == "true"
        
        # Security settings
        self._config.jwt_secret_key = os.getenv("JWT_SECRET_KEY", self._config.jwt_secret_key)
        
        # Database settings
        self._config.database_url = os.getenv("DATABASE_URL", self._config.database_url)
        
        # Email settings
        self._config.email_username = os.getenv("EMAIL_USERNAME", "")
        self._config.email_password = os.getenv("EMAIL_PASSWORD", "")
        self._config.smtp_server = os.getenv("SMTP_SERVER", self._config.smtp_server)
        self._config.smtp_port = int(os.getenv("SMTP_PORT", str(self._config.smtp_port)))
        self._config.use_tls = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
        
        # AI settings
        self._config.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    
    def _apply_defaults(self):
        """Apply safe defaults for any missing values"""
        if not self._config.jwt_secret_key or self._config.jwt_secret_key == "demo-secret-key-change-in-production":
            logger.warning("Using demo JWT secret key - please configure in production")
        
        if not self._config.database_url:
            self._config.database_url = "sqlite:///./proofsar.db"
            logger.info("Using SQLite fallback database")
        
        if not self._config.email_username:
            logger.info("Email service not configured - using demo mode")
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """
        Get a secret value with fallback mechanism
        
        Args:
            key: The secret key to retrieve
            default: Default value if secret not found
            
        Returns:
            The secret value or default
        """
        if not self._config:
            self._load_configuration()
        
        # Map common secret keys to config attributes
        secret_map = {
            "SHOW_DEBUG_INFO": self._config.show_debug_info,
            "JWT_SECRET_KEY": self._config.jwt_secret_key,
            "DATABASE_URL": self._config.database_url,
            "EMAIL_USERNAME": self._config.email_username,
            "EMAIL_PASSWORD": self._config.email_password,
            "GEMINI_API_KEY": self._config.gemini_api_key,
            "SMTP_SERVER": self._config.smtp_server,
            "SMTP_PORT": self._config.smtp_port,
            "EMAIL_USE_TLS": self._config.use_tls
        }
        
        return secret_map.get(key, default)
    
    def get_config(self) -> SecretConfig:
        """Get the complete configuration object"""
        if not self._config:
            self._load_configuration()
        return self._config
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get_secret("SHOW_DEBUG_INFO", False)

# Global instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager

def get_secret(key: str, default: Any = None) -> Any:
    """
    Convenience function to get a secret value
    
    Args:
        key: The secret key to retrieve
        default: Default value if secret not found
        
    Returns:
        The secret value or default
    """
    return get_secrets_manager().get_secret(key, default)
