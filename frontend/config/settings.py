"""
Enterprise Configuration Settings for ProofSAR AI
Production-grade configuration management
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "proofsar_ai")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    ssl_mode: str = os.getenv("DB_SSL_MODE", "require")

@dataclass
class EmailConfig:
    """Email service configuration"""
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    username: str = os.getenv("EMAIL_USERNAME", "")
    password: str = os.getenv("EMAIL_PASSWORD", "")
    use_tls: bool = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
    timeout: int = int(os.getenv("EMAIL_TIMEOUT", "30"))

@dataclass
class AIModelConfig:
    """AI model configuration"""
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    local_model_path: str = os.getenv("LOCAL_MODEL_PATH", "/models/llama-2-7b")
    use_gemini: bool = os.getenv("USE_GEMINI", "true").lower() == "true"
    temperature: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "2048"))

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    session_timeout: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    allowed_file_types: list = None
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ["csv"]

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: str = os.getenv("LOG_FILE_PATH", "logs/proofsar_ai.log")
    max_file_size: int = int(os.getenv("LOG_MAX_FILE_SIZE", "10485760"))  # 10MB
    backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

@dataclass
class UIConfig:
    """UI configuration settings"""
    theme: str = os.getenv("UI_THEME", "light")
    page_title: str = "ProofSAR AI - Glass-Box AML Copilot"
    page_icon: str = "🛡️"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    show_developer_mode: bool = os.getenv("SHOW_DEVELOPER_MODE", "false").lower() == "true"

class EnterpriseConfig:
    """Enterprise configuration manager"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.demo_data_dir = self.base_dir / "demo_data"
        self.logs_dir = self.base_dir / "logs"
        
        # Initialize configuration sections
        self.database = DatabaseConfig()
        self.email = EmailConfig()
        self.ai_model = AIModelConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self.ui = UIConfig()
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Load environment-specific settings
        self._load_environment_settings()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.demo_data_dir,
            self.logs_dir,
            self.base_dir / "uploads",
            self.base_dir / "exports"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_environment_settings(self):
        """Load environment-specific settings"""
        env = os.getenv("ENVIRONMENT", "development").lower()
        
        if env == "production":
            self.logging.level = "WARNING"
            self.security.session_timeout = 1800  # 30 minutes
            self.ui.show_developer_mode = False
        elif env == "staging":
            self.logging.level = "INFO"
            self.security.session_timeout = 3600  # 1 hour
        else:  # development
            self.logging.level = "DEBUG"
            self.ui.show_developer_mode = True
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return f"postgresql://{self.database.user}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.name}"
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration as dictionary"""
        return {
            "smtp_server": self.email.smtp_server,
            "smtp_port": self.email.smtp_port,
            "username": self.email.username,
            "password": self.email.password,
            "use_tls": self.email.use_tls,
            "timeout": self.email.timeout
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI model configuration as dictionary"""
        return {
            "gemini_api_key": self.ai_model.gemini_api_key,
            "local_model_path": self.ai_model.local_model_path,
            "use_gemini": self.ai_model.use_gemini,
            "temperature": self.ai_model.temperature,
            "max_tokens": self.ai_model.max_tokens
        }
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Get Streamlit configuration"""
        return {
            "page_title": self.ui.page_title,
            "page_icon": self.ui.page_icon,
            "layout": self.ui.layout,
            "initial_sidebar_state": self.ui.initial_sidebar_state,
            "menu_items": {
                'Get Help': 'https://github.com/barclays/proofsar-ai',
                'Report a bug': "https://github.com/barclays/proofsar-ai/issues",
                'About": "# ProofSAR AI\nGlass-Box AML Compliance Copilot\n\nEnterprise-grade AML compliance platform with explainable AI and cryptographic audit trails."
            }
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration settings"""
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Validate critical settings
        if not self.email.username:
            validation_results["warnings"].append("Email username not configured")
        
        if not self.email.password:
            validation_results["warnings"].append("Email password not configured")
        
        if not self.ai_model.gemini_api_key and self.ai_model.use_gemini:
            validation_results["errors"].append("Gemini API key required when using Gemini")
            validation_results["is_valid"] = False
        
        if self.security.jwt_secret_key == "your-secret-key-change-in-production":
            validation_results["errors"].append("JWT secret key must be changed in production")
            validation_results["is_valid"] = False
        
        # Validate file paths
        if not self.demo_data_dir.exists():
            validation_results["warnings"].append(f"Demo data directory not found: {self.demo_data_dir}")
        
        return validation_results
    
    def get_risk_thresholds(self) -> Dict[str, float]:
        """Get risk assessment thresholds"""
        return {
            "critical": float(os.getenv("RISK_THRESHOLD_CRITICAL", "0.75")),
            "high": float(os.getenv("RISK_THRESHOLD_HIGH", "0.5")),
            "medium": float(os.getenv("RISK_THRESHOLD_MEDIUM", "0.25")),
            "low": float(os.getenv("RISK_THRESHOLD_LOW", "0.0"))
        }
    
    def get_alert_recipients(self) -> Dict[str, list]:
        """Get alert recipient configurations"""
        return {
            "high_risk": os.getenv("ALERT_RECIPIENTS_HIGH_RISK", "compliance@barclays.com,supervisor@barclays.com").split(","),
            "pending_review": os.getenv("ALERT_RECIPIENTS_PENDING_REVIEW", "analyst@barclays.com").split(","),
            "approved": os.getenv("ALERT_RECIPIENTS_APPROVED", "compliance@barclays.com").split(","),
            "rejected": os.getenv("ALERT_RECIPIENTS_REJECTED", "analyst@barclays.com,supervisor@barclays.com").split(",")
        }

# Global configuration instance
config = EnterpriseConfig()

def get_config() -> EnterpriseConfig:
    """Get global configuration instance"""
    return config
