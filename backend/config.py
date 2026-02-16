import os
from typing import Optional

class Config:
    # Application
    APP_NAME = "ProofSAR AI"
    VERSION = "1.0.0"
    
    # AI Models
    USE_GEMINI = True  # Toggle for Gemini vs Local LLM
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "demo-key")
    LOCAL_LLM_PATH = "./models/llama-2-7b"
    
    # Database
    DATABASE_URL = "sqlite:///./proofsar.db"
    
    # Security
    SECRET_KEY = "hackathon-demo-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 480
    
    # Email Alerts
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_FROM = "proofsar.alerts@demo.com"
    EMAIL_PASSWORD = "demo-password"
    
    # Regulatory Thresholds (India)
    CTR_THRESHOLD = 10000  # ₹10 Lakhs for CTR
    HIGH_RISK_THRESHOLD = 0.75
    
    # Audit
    ENABLE_AUDIT_TRAIL = True
    HASH_ALGORITHM = "sha256"
    
    # RAG
    CHROMA_PERSIST_DIR = "./chroma_db"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

config = Config()