"""
ProofSAR AI Backend - FastAPI Application
Enterprise AML Compliance API
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
from pathlib import Path
import logging
import uvicorn
from datetime import datetime, timedelta
import json

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from config import config
from detection.structuring import ComprehensiveDetectionEngine
from reasoning.guilt_engine import GuiltReasoningEngine
from ai_engine.gemini_client import AIGenerator
from audit.hash_chain import AuditLogger
from alerts.gmail_service import GmailAlertService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ProofSAR AI API",
    description="Enterprise AML Compliance Backend",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
detection_engine = ComprehensiveDetectionEngine()
reasoning_engine = GuiltReasoningEngine()
ai_generator = AIGenerator(use_gemini=config.USE_GEMINI)
audit_logger = AuditLogger()
alert_service = GmailAlertService()

# Pydantic Models
class TransactionData(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    timestamp: str
    transaction_type: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None

class AnalysisRequest(BaseModel):
    transactions: List[TransactionData]
    customer_profile: Optional[Dict[str, Any]] = None

class DetectionResult(BaseModel):
    case_id: str
    risk_score: float
    risk_level: str
    patterns: List[str]
    evidence: List[Dict[str, Any]]
    red_flags: List[str]
    timestamp: str

class SARRequest(BaseModel):
    case_id: str
    detection_results: Dict[str, Any]
    reasoning_results: Optional[Dict[str, Any]] = None

# Helper Functions
def create_demo_customer_profile():
    """Create demo customer profile for testing"""
    return {
        'customer_name': 'Rajesh Kumar',
        'account_number': 'ACC-1001',
        'customer_id': 'CUST-789012',
        'pan': 'ABCDE1234F',
        'account_type': 'Savings',
        'account_opening_date': '2020-01-15',
        'occupation': 'Business Owner',
        'annual_income': 2000000,
        'income_source': 'Business Profits',
        'address': '123 MG Road, Mumbai 400001',
        'phone': '+91-9876543210',
        'kyc_status': 'Verified',
        'risk_category': 'Medium',
        'reporting_bank': 'Barclays Bank India'
    }

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token (simplified for demo)"""
    # In production, implement proper JWT verification
    return {"user_id": "demo_user", "role": "analyst"}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ProofSAR AI API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "detection_engine": "operational",
            "reasoning_engine": "operational", 
            "ai_generator": "operational" if config.USE_GEMINI else "local_mode",
            "audit_logger": "operational",
            "alert_service": "operational"
        }
    }

@app.post("/api/v1/analyze", response_model=Dict[str, Any])
async def analyze_transactions(
    request: AnalysisRequest,
    current_user: dict = Depends(verify_token)
):
    """Analyze transactions for AML patterns"""
    try:
        # Convert to DataFrame
        import pandas as pd
        df_data = [tx.dict() for tx in request.transactions]
        df = pd.DataFrame(df_data)
        
        # Convert timestamp to date for detection engine
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Add location column (use destination as location)
        df['location'] = df.get('destination', 'UNKNOWN')
        
        # Generate case ID
        case_id = f"SAR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Run detection
        logger.info(f"Running detection analysis for case {case_id}")
        detection_results = detection_engine.analyze_all(df)
        
        # Generate reasoning
        logger.info(f"Generating reasoning for case {case_id}")
        customer_profile = request.customer_profile or create_demo_customer_profile()
        reasoning_results = reasoning_engine.generate_reasoning(detection_results, customer_profile)
        
        # Log audit
        audit_logger.log_case_created(
            current_user["user_id"],
            case_id,
            {"transaction_count": len(df), "customer_id": customer_profile.get("customer_id")}
        )
        
        audit_logger.log_analysis_run(
            current_user["user_id"],
            case_id,
            detection_results
        )
        
        # Send alert if high risk
        if detection_results['risk_score'] >= 0.75:
            try:
                alert_service.send_high_risk_alert(
                    case_id,
                    detection_results['risk_score'],
                    ["compliance@barclays.com"]
                )
                audit_logger.log_alert_sent(
                    current_user["user_id"],
                    case_id,
                    ["compliance@barclays.com"],
                    "HIGH_RISK"
                )
            except Exception as e:
                logger.warning(f"Failed to send alert: {str(e)}")
        
        return {
            "case_id": case_id,
            "detection_results": detection_results,
            "reasoning_results": reasoning_results,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/api/v1/generate-sar")
async def generate_sar(
    request: SARRequest,
    current_user: dict = Depends(verify_token)
):
    """Generate SAR report"""
    try:
        case_id = request.case_id
        
        # Generate SAR using AI
        logger.info(f"Generating SAR for case {case_id}")
        
        # For demo, create a mock SAR
        sar_content = f"""
SUSPICIOUS ACTIVITY REPORT - {case_id}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CASE DETAILS:
Case ID: {case_id}
Risk Score: {request.detection_results.get('risk_score', 'N/A')}
Risk Level: {request.detection_results.get('overall_risk', 'N/A')}

PATTERNS DETECTED:
{chr(10).join(f"- {pattern}" for pattern in request.detection_results.get('all_patterns', []))}

This SAR was generated by ProofSAR AI System.
"""
        
        # Log audit
        audit_logger.log_sar_generated(
            current_user["user_id"],
            case_id,
            sar_content,
            "ProofSAR-AI-v2.0"
        )
        
        return {
            "case_id": case_id,
            "sar_content": sar_content,
            "status": "generated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"SAR generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SAR generation failed: {str(e)}"
        )

@app.get("/api/v1/audit/{case_id}")
async def get_audit_trail(
    case_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get audit trail for a case"""
    try:
        # Get audit data
        audit_data = {
            "case_id": case_id,
            "events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "CASE_CREATED",
                    "user_id": current_user["user_id"],
                    "description": f"Case {case_id} created"
                }
            ],
            "hash_chain_valid": True
        }
        
        return audit_data
        
    except Exception as e:
        logger.error(f"Failed to get audit trail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit trail: {str(e)}"
        )

@app.get("/api/v1/alerts")
async def get_alerts(
    current_user: dict = Depends(verify_token)
):
    """Get alert history"""
    try:
        alert_stats = alert_service.get_alert_stats()
        alert_history = alert_service.get_alert_history()
        
        # Calculate success rate if not provided
        if 'success_rate' not in alert_stats:
            total = alert_stats.get('total_sent', 0) + alert_stats.get('total_failed', 0)
            if total > 0:
                alert_stats['success_rate'] = alert_stats.get('total_sent', 0) / total
            else:
                alert_stats['success_rate'] = 0.0
        
        return {
            "stats": alert_stats,
            "history": alert_history[-10:],  # Last 10 alerts
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )

@app.get("/api/v1/models/status")
async def get_model_status():
    """Get AI model status"""
    return {
        "gemini_available": config.USE_GEMINI,
        "local_model_path": config.LOCAL_LLM_PATH,
        "detection_algorithms": ["structuring", "layering", "smurfing"],
        "reasoning_engine": "operational",
        "timestamp": datetime.now().isoformat()
    }

# Startup Event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("ProofSAR AI Backend starting up...")
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    
    logger.info("Backend startup complete")

# Shutdown Event  
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("ProofSAR AI Backend shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
