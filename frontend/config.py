"""
Centralized configuration for ProofSAR AI
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple

# Color Palette - Professional Fintech Style
class Colors:
    # Primary
    PRIMARY = "#667EEA"
    PRIMARY_DARK = "#764BA2"
    
    # States
    SUCCESS = "#28A745"
    WARNING = "#FFC107"
    DANGER = "#DC3545"
    INFO = "#00A9E0"
    
    # Neutral
    LIGHT = "#F5F7FA"
    DARK = "#2C3E50"
    GRAY = "#6C757D"
    BORDER = "#E9ECEF"
    
    # Status Colors
    CRITICAL = "#DC3545"
    HIGH_RISK = "#FD7E14"
    MEDIUM_RISK = "#FFC107"
    LOW_RISK = "#28A745"
    
    # Text
    TEXT_PRIMARY = "#2D3436"
    TEXT_SECONDARY = "#636E72"
    
    @staticmethod
    def gradient(color1: str, color2: str) -> str:
        """Create CSS gradient"""
        return f"linear-gradient(135deg, {color1} 0%, {color2} 100%)"


# Risk Levels
class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class RiskLevelConfig:
    """Configuration for each risk level"""
    color: str
    emoji: str
    badge_class: str
    description: str


# Risk Configuration Map
RISK_CONFIG: Dict[str, RiskLevelConfig] = {
    "CRITICAL": RiskLevelConfig(
        color=Colors.CRITICAL,
        emoji="🔴",
        badge_class="critical-badge",
        description="Immediate action required"
    ),
    "HIGH": RiskLevelConfig(
        color=Colors.HIGH_RISK,
        emoji="🟠",
        badge_class="high-badge",
        description="High priority review needed"
    ),
    "MEDIUM": RiskLevelConfig(
        color=Colors.MEDIUM_RISK,
        emoji="🟡",
        badge_class="medium-badge",
        description="Standard review required"
    ),
    "LOW": RiskLevelConfig(
        color=Colors.LOW_RISK,
        emoji="🟢",
        badge_class="low-badge",
        description="Low priority"
    )
}


# Streamlit Configuration
STREAMLIT_CONFIG = {
    "layout": "wide",
    "init_sidebar_state": "expanded",
    "theme": {
        "primaryColor": Colors.PRIMARY,
        "backgroundColor": Colors.LIGHT,
        "secondaryBackgroundColor": "#FFFFFF",
        "textColor": Colors.TEXT_PRIMARY,
        "font": "sans serif"
    }
}


# Required CSV Columns for Upload
REQUIRED_CSV_COLUMNS = [
    'transaction_id',
    'date',
    'amount',
    'account_number',
    'source',
    'transaction_type'
]


# Alert Thresholds
ALERT_THRESHOLDS = {
    "high_risk_score": 0.75,
    "critical_risk_score": 0.90,
    "auto_escalate_delay_hours": 24
}


# Email Configuration (for environment variable fallback)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "timeout": 10,
    "max_retries": 3,
    "retry_delay_seconds": 5
}


# UI Messages - Professional Tone
MESSAGES = {
    "upload_success": "✅ File uploaded successfully",
    "analysis_complete": "✅ Analysis complete",
    "error_invalid_csv": "❌ Invalid CSV format. Missing required columns.",
    "error_empty_file": "❌ CSV file is empty",
    "error_analysis_failed": "❌ Analysis failed. Please check your data.",
    "loading_analysis": "🔬 Running detection analysis...",
    "loading_reasoning": "🧠 Generating reasoning...",
    "loading_audit": "📝 Logging audit trail...",
    "loading_alerts": "📧 Sending alerts...",
}


# Fintech Theme Transitions
SMOOTH_TRANSITIONS = {
    "duration": "0.3s",
    "easing": "ease-out"
}
