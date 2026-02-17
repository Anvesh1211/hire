# ProofSAR AI - Secrets Configuration Guide

## 📋 **Overview**

ProofSAR AI uses a production-grade secrets management system with multiple fallback layers:
1. **Streamlit Secrets** (Production deployment)
2. **Environment Variables** (Docker/development)
3. **Default Values** (Safe fallback)

## 🔧 **Setup Instructions**

### **Option 1: Streamlit Cloud/Production Deployment**

1. **Create secrets.toml file**:
   ```bash
   mkdir -p .streamlit
   cp frontend/secrets.toml.example .streamlit/secrets.toml
   ```

2. **Edit the secrets file**:
   ```toml
   # Production values
   SHOW_DEBUG_INFO = false
   JWT_SECRET_KEY = "your-very-secure-secret-key"
   DATABASE_URL = "postgresql://user:pass@host:5432/db"
   EMAIL_USERNAME = "your_email@barclays.com"
   EMAIL_PASSWORD = "your_gmail_app_password"
   GEMINI_API_KEY = "your_gemini_api_key"
   ```

3. **Deploy to Streamlit Cloud**:
   - The `.streamlit/secrets.toml` will be automatically used
   - No additional configuration needed

### **Option 2: Local Development**

1. **Set environment variables**:
   ```bash
   export SHOW_DEBUG_INFO=true
   export JWT_SECRET_KEY="dev-secret-key"
   export DATABASE_URL="sqlite:///./proofsar.db"
   export EMAIL_USERNAME="dev@barclays.com"
   export EMAIL_PASSWORD="dev_password"
   export GEMINI_API_KEY="dev_api_key"
   ```

2. **Or create .env file**:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

### **Option 3: Docker Deployment**

1. **Using docker-compose.yml**:
   ```yaml
   services:
     proofsar-ai:
       environment:
         - SHOW_DEBUG_INFO=false
         - JWT_SECRET_KEY=${JWT_SECRET_KEY}
         - DATABASE_URL=${DATABASE_URL}
         - EMAIL_USERNAME=${EMAIL_USERNAME}
         - EMAIL_PASSWORD=${EMAIL_PASSWORD}
         - GEMINI_API_KEY=${GEMINI_API_KEY}
   ```

2. **Create .env file**:
   ```bash
   JWT_SECRET_KEY=your-secure-key
   DATABASE_URL=postgresql://postgres:password@db:5432/proofsar_ai
   EMAIL_USERNAME=your_email@barclays.com
   EMAIL_PASSWORD=your_gmail_app_password
   GEMINI_API_KEY=your_gemini_api_key
   ```

## 🔒 **Security Best Practices**

### **Production Security**
- ✅ Use strong JWT secret keys (32+ characters)
- ✅ Enable TLS for email services
- ✅ Use PostgreSQL in production
- ✅ Set `SHOW_DEBUG_INFO=false`
- ✅ Rotate API keys regularly
- ✅ Use environment-specific configurations

### **Development Security**
- ✅ Use separate development database
- ✅ Use demo email credentials
- ✅ Enable debug mode locally only
- ✅ Never commit real secrets to git

## 📁 **File Structure**

```
lolpro/
├── .env.example                    # Environment template
├── .env                           # Local environment (git-ignored)
├── .streamlit/
│   └── secrets.toml               # Streamlit secrets (git-ignored)
├── frontend/
│   ├── config/
│   │   └── secrets.py             # Secrets manager
│   └── secrets.toml.example       # Secrets template
└── docker-compose.yml              # Docker configuration
```

## 🧪 **Testing Configuration**

### **Test if secrets are loaded correctly**:
```python
from frontend.config.secrets import get_secret, get_secrets_manager

# Test individual secrets
debug_mode = get_secret("SHOW_DEBUG_INFO", False)
print(f"Debug mode: {debug_mode}")

# Test full configuration
manager = get_secrets_manager()
config = manager.get_config()
print(f"JWT configured: {bool(config.jwt_secret_key)}")
print(f"Email configured: {bool(config.email_username)}")
```

### **Verify in Streamlit app**:
```python
import streamlit as st
from frontend.config.secrets import get_secret

# This will NOT crash if secrets.toml doesn't exist
if get_secret("SHOW_DEBUG_INFO", False):
    st.success("✅ Secrets loaded successfully!")
else:
    st.info("ℹ️ Running in safe mode with defaults")
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **"No secrets found" Error**:
   - ✅ Create `.streamlit/secrets.toml`
   - ✅ Set environment variables
   - ✅ Check file permissions

2. **"Secret not found" Error**:
   - ✅ Verify secret name in secrets.toml
   - ✅ Check environment variable name
   - ✅ Restart application after changes

3. **Debug mode not working**:
   - ✅ Set `SHOW_DEBUG_INFO=true`
   - ✅ Restart Streamlit
   - ✅ Check environment priority

### **Debug Information**

The secrets manager provides detailed logging:
```bash
# Check logs for configuration loading
tail -f logs/proofsar_ai.log | grep -i "configuration"
```

## 🔧 **Configuration Priority**

1. **Streamlit Secrets** (highest priority)
   - Used in Streamlit Cloud deployment
   - Automatically encrypted and secure

2. **Environment Variables** (medium priority)
   - Used in Docker/local development
   - Override secrets.toml values

3. **Default Values** (lowest priority)
   - Safe fallback for development
   - Never use in production

## 📋 **Configuration Checklist**

### **Pre-Deployment Checklist**
- [ ] JWT_SECRET_KEY is strong and unique
- [ ] DATABASE_URL points to production database
- [ ] EMAIL credentials are correct
- [ ] GEMINI_API_KEY is valid
- [ ] SHOW_DEBUG_INFO is false
- [ ] All sensitive values are set
- [ ] Test with staging environment first

### **Post-Deployment Verification**
- [ ] Application starts without errors
- [ ] Secrets are loaded correctly
- [ ] Debug mode is disabled
- [ ] All services are operational
- [ ] Error handling works properly

## 🆘 **Support**

If you encounter issues with secrets configuration:

1. **Check the logs**: `logs/proofsar_ai.log`
2. **Verify file locations**: Ensure secrets are in correct paths
3. **Test environment**: Use the provided test script
4. **Review examples**: Compare with templates provided

**Remember**: The secrets manager is designed to never crash the application, even with missing configuration files.
