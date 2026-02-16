# ProofSAR AI Enterprise Setup Guide

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (for production)
- Gmail account with App Password
- Gemini API key (for AI features)

### Installation Steps

1. **Clone the Repository**
```bash
git clone <repository-url>
cd lolpro
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
# Copy the template
cp .env.example .env

# Edit the configuration
nano .env
```

5. **Initialize Database**
```bash
# Create database schema
python -m backend.database.init_db

# Run migrations
python -m backend.database.migrate
```

6. **Start the Application**
```bash
# Development mode
streamlit run frontend/app.py

# Production mode
export ENVIRONMENT=production
streamlit run frontend/app.py --server.port=8501
```

## Environment Configuration

### Required Environment Variables

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=proofsar_ai
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Email Service
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@barclays.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_USE_TLS=true

# AI Services
GEMINI_API_KEY=your_gemini_api_key
USE_GEMINI=true
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2048

# Security
JWT_SECRET_KEY=your_very_secure_secret_key_change_this
JWT_ALGORITHM=HS256
SESSION_TIMEOUT=3600
MAX_FILE_SIZE=10485760

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
SHOW_DEVELOPER_MODE=true
```

### Gmail App Password Setup

1. Enable 2-factor authentication on your Gmail account
2. Go to Google Account settings
3. Navigate to "Security" → "App passwords"
4. Generate a new app password for ProofSAR AI
5. Use this password in the EMAIL_PASSWORD environment variable

## Production Deployment

### Docker Deployment

1. **Build Docker Image**
```bash
docker build -t proofsar-ai:latest .
```

2. **Run with Docker Compose**
```bash
docker-compose up -d
```

### Kubernetes Deployment

1. **Apply Kubernetes Manifests**
```bash
kubectl apply -f k8s/
```

2. **Check Deployment Status**
```bash
kubectl get pods -n proofsar-ai
```

## Monitoring Setup

### Application Logging

Logs are automatically configured to write to:
- Console output (for containerized environments)
- File: `logs/proofsar_ai.log` (for local development)

### Health Checks

The application exposes health check endpoints:
- `/health` - Basic health status
- `/ready` - Readiness probe
- `/metrics` - Application metrics

## Security Configuration

### SSL/TLS Setup

For production deployment, configure SSL/TLS:

```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Configure Streamlit for HTTPS
streamlit run frontend/app.py --server.sslCertFile cert.pem --server.sslKeyFile key.pem
```

### Firewall Configuration

Ensure only necessary ports are open:
- 8501: Streamlit application
- 5432: PostgreSQL (internal only)
- 587: SMTP (outbound only)

## Backup and Recovery

### Database Backup

```bash
# Create backup
pg_dump -h localhost -U postgres proofsar_ai > backup_$(date +%Y%m%d).sql

# Restore backup
psql -h localhost -U postgres proofsar_ai < backup_20240216.sql
```

### File System Backup

```bash
# Backup application files
tar -czf proofsar_backup_$(date +%Y%m%d).tar.gz \
  --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' .
```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_audit_case_id ON audit(case_id);
```

### Application Caching

Configure Redis for caching (optional):

```bash
# Install Redis
pip install redis

# Configure in environment
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database server is running
   - Verify connection parameters
   - Ensure firewall allows connection

2. **Email Service Not Working**
   - Verify Gmail app password
   - Check SMTP server settings
   - Ensure TLS is enabled

3. **AI Features Not Available**
   - Verify Gemini API key
   - Check internet connectivity
   - Review API quota limits

4. **File Upload Fails**
   - Check file size limits
   - Verify file format (CSV only)
   - Ensure upload directory permissions

### Log Analysis

```bash
# View application logs
tail -f logs/proofsar_ai.log

# Filter for errors
grep ERROR logs/proofsar_ai.log

# Monitor in real-time
tail -f logs/proofsar_ai.log | grep ERROR
```

## Maintenance Tasks

### Daily Tasks
- Monitor application logs for errors
- Check system resource usage
- Verify email service functionality

### Weekly Tasks
- Review audit trail logs
- Update security patches
- Backup database and files

### Monthly Tasks
- Review and rotate secrets
- Update SSL certificates
- Performance optimization review

## Support

For technical support:
1. Check the troubleshooting guide
2. Review application logs
3. Contact the development team at compliance@barclays.com

## Version Information

- **Current Version**: 2.0.0 Enterprise
- **Python Requirements**: 3.8+
- **Streamlit Version**: 1.29.0+
- **Database**: PostgreSQL 12+
- **Operating System**: Linux/Windows/macOS
