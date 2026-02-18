"""
Enterprise Gmail Alert Service v2 for ProofSAR AI
Production-grade email service with security, retry, and structured logging
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Dict, Optional, Any
import logging
import os
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import traceback
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    """Email configuration data class"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    use_tls: bool = True
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class EmailStatus:
    """Email delivery status tracking"""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    attempts: int = 0
    delivery_time: Optional[datetime] = None
    smtp_response: Optional[str] = None

class GmailAlertServiceV2:
    """
    Enterprise-grade email alert service for SAR workflow
    Features:
    - SMTP with STARTTLS enforcement
    - Configurable retry mechanism
    - Structured logging
    - Environment variable configuration
    - Status tracking
    - Attachment support
    - HTML email formatting
    """
    
    def __init__(self, debug_mode: Optional[bool] = None):
        """Initialize Gmail service with environment configuration"""
        
        # Load environment variables
        try:
            load_dotenv()
            logger.info("📦 Environment variables loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load environment variables: {e}")
            raise
        
        # Configuration from environment with validation
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.use_tls = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
        
        # Debug mode from env or parameter
        env_debug = os.getenv("EMAIL_DEBUG", "false").lower() == "true"
        self.debug_mode = debug_mode if debug_mode is not None else env_debug
        
        # Retry configuration from environment
        self.max_retries = int(os.getenv("EMAIL_MAX_RETRIES", "3"))
        self.base_delay = int(os.getenv("EMAIL_BASE_DELAY", "2"))
        self.max_delay = int(os.getenv("EMAIL_MAX_DELAY", "30"))
        self.connection_timeout = int(os.getenv("EMAIL_TIMEOUT", "30"))
        
        # Set debug logging level
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.debug("🐛 Debug mode enabled")
        
        # Alert tracking
        self.sent_alerts = []
        self.failed_alerts = []
        
        # Validate environment setup
        self._validate_environment()
        
        logger.info(f"🚀 GmailAlertServiceV2 initialized - Server: {self.smtp_server}:{self.smtp_port}, TLS: {self.use_tls}, Max Retries: {self.max_retries}")
    
    def _validate_environment(self) -> None:
        """Validate required environment variables"""
        missing_vars = []
        
        if not self.email_username:
            missing_vars.append("EMAIL_USERNAME")
        if not self.email_password:
            missing_vars.append("EMAIL_PASSWORD")
        
        if missing_vars:
            error_msg = f"❌ Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check for potential App Password issues
        if "@" in self.email_username and len(self.email_password) < 16:
            logger.warning("⚠️ Gmail password appears to be a regular password. Consider using an App Password for better security.")
            logger.info("💡 To create an App Password: Google Account → Security → 2-Step Verification → App Passwords")
        
        # Validate SMTP configuration
        if self.smtp_port not in [587, 465, 25]:
            logger.warning(f"⚠️ Unusual SMTP port: {self.smtp_port}. Standard ports: 587 (STARTTLS), 465 (SSL/TLS), 25 (SMTP)")
        
        logger.info("✅ Environment validation completed")
    
    def health_check(self) -> Dict[str, any]:
        """
        Comprehensive health check of the email service
        Returns detailed status of all components
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "recommendations": []
        }
        
        try:
            logger.info("🔍 Starting Gmail service health check...")
            
            # Check environment variables
            env_check = {
                "status": "pass" if self.email_username and self.email_password else "fail",
                "username_configured": bool(self.email_username),
                "password_configured": bool(self.email_password),
                "smtp_server": self.smtp_server,
                "smtp_port": self.smtp_port,
                "tls_enabled": self.use_tls,
                "debug_mode": self.debug_mode,
                "max_retries": self.max_retries
            }
            health_status["checks"]["environment"] = env_check
            
            # Test SMTP connection and authentication
            connection_check = {"status": "unknown", "message": "", "details": {}}
            server = None
            
            try:
                logger.debug(f"🔌 Testing SMTP connection to {self.smtp_server}:{self.smtp_port}")
                
                # Create SSL context for TLS
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout)
                
                if self.debug_mode:
                    server.set_debuglevel(1)
                
                # Initial EHLO
                server.ehlo()
                connection_check["details"]["ehlo_before_tls"] = "success"
                logger.debug("👋 EHLO before TLS successful")
                
                # Enforce STARTTLS
                if self.use_tls:
                    server.starttls(context=context)
                    server.ehlo()  # EHLO after STARTTLS to get updated capabilities
                    connection_check["details"]["starttls"] = "success"
                    connection_check["details"]["ehlo_after_tls"] = "success"
                    logger.debug("🔒 STARTTLS enforced successfully")
                    health_status["checks"]["tls"] = {"status": "pass", "message": "STARTTLS successful"}
                
                # Test authentication
                server.login(self.email_username, self.email_password)
                connection_check["details"]["authentication"] = "success"
                connection_check["status"] = "pass"
                connection_check["message"] = "SMTP connection and authentication successful"
                logger.debug("🔐 SMTP authentication successful")
                
                health_status["checks"]["authentication"] = {"status": "pass", "message": "SMTP login successful"}
                health_status["checks"]["connection"] = {"status": "pass", "message": "SMTP connection successful"}
                
                server.quit()
                logger.debug("👋 SMTP connection closed gracefully")
                
            except smtplib.SMTPAuthenticationError as e:
                error_msg = str(e)
                connection_check["status"] = "fail"
                connection_check["message"] = "Authentication failed"
                connection_check["details"]["authentication_error"] = error_msg
                
                # Detect specific Gmail issues
                if "Application-specific password required" in error_msg:
                    connection_check["recommendation"] = "Use Gmail App Password instead of regular password"
                    health_status["recommendations"].append("Create a Gmail App Password for secure authentication")
                elif "Username and Password not accepted" in error_msg:
                    connection_check["recommendation"] = "Check username and password credentials"
                    health_status["recommendations"].append("Verify EMAIL_USERNAME and EMAIL_PASSWORD are correct")
                
                health_status["checks"]["authentication"] = {
                    "status": "fail", 
                    "message": "Authentication failed - check credentials or use App Password",
                    "error": error_msg,
                    "recommendation": connection_check["recommendation"]
                }
                health_status["status"] = "unhealthy"
                logger.error(f"❌ SMTP Authentication Error: {e}")
                
            except smtplib.SMTPConnectError as e:
                connection_check["status"] = "fail"
                connection_check["message"] = "Cannot connect to SMTP server"
                connection_check["details"]["connection_error"] = str(e)
                
                health_status["checks"]["connection"] = {
                    "status": "fail",
                    "message": "Cannot connect to SMTP server",
                    "error": str(e),
                    "recommendation": "Check SMTP_SERVER and SMTP_PORT, ensure network connectivity"
                }
                health_status["status"] = "unhealthy"
                logger.error(f"❌ SMTP Connection Error: {e}")
                
            except Exception as e:
                connection_check["status"] = "fail"
                connection_check["message"] = "Unexpected connection error"
                connection_check["details"]["unexpected_error"] = str(e)
                
                health_status["checks"]["connection"] = {
                    "status": "fail",
                    "message": "Unexpected connection error",
                    "error": str(e)
                }
                health_status["status"] = "unhealthy"
                logger.error(f"❌ Unexpected Connection Error: {e}")
            
            finally:
                if server:
                    try:
                        server.quit()
                    except Exception as e:
                        logger.warning(f"⚠️ Error closing SMTP connection during health check: {e}")
            
            health_status["checks"]["connection_test"] = connection_check
            
            # Overall status assessment
            if health_status["status"] == "healthy":
                logger.info("✅ Gmail service health check passed")
            else:
                logger.error(f"❌ Gmail service health check failed: {health_status}")
                
        except Exception as e:
            health_status["status"] = "error"
            logger.error(f"❌ Health check critical error: {e}")
        
        return health_status
    
    def _send_smtp_email(self, subject: str, body: str, recipients: List[str], is_html: bool = False) -> EmailStatus:
        """
        Send email via SMTP with enterprise-grade retry mechanism and TLS security
        """
        status = EmailStatus(success=False, attempts=0)
        
        for attempt in range(self.max_retries):
            status.attempts = attempt + 1
            server = None
            
            try:
                if self.debug_mode:
                    logger.info(f"📧 Attempt {attempt + 1}/{self.max_retries} - Sending to {recipients}")
                
                # Create SSL context for enterprise security
                context = ssl.create_default_context()
                
                # Create SMTP connection with timeout
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.connection_timeout)
                
                if self.debug_mode:
                    server.set_debuglevel(1)
                
                # Enterprise TLS sequence
                server.ehlo()  # Initial greeting
                if self.use_tls:
                    server.starttls(context=context)  # Enforce STARTTLS
                    server.ehlo()  # Re-greet after STARTTLS
                    if self.debug_mode:
                        logger.info("🔒 Enterprise STARTTLS enforced")
                
                # Authentication
                server.login(self.email_username, self.email_password)
                if self.debug_mode:
                    logger.info("🔐 SMTP authentication successful")
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.email_username
                msg['To'] = ', '.join(recipients)
                msg['Subject'] = subject
                
                # Add body with proper MIME type
                if is_html:
                    msg.attach(MIMEText(body, 'html'))
                else:
                    msg.attach(MIMEText(body, 'plain'))
                
                # Send email
                smtp_response = server.sendmail(self.email_username, recipients, msg.as_string())
                
                # Parse SMTP response
                if smtp_response:
                    # Some recipients failed
                    failed_recipients = list(smtp_response.keys())
                    status.success = False
                    status.error_message = f"Failed to send to: {failed_recipients}"
                    status.smtp_response = json.dumps(smtp_response)
                    logger.warning(f"⚠️ Partial delivery failure: {failed_recipients}")
                else:
                    # All recipients successful
                    status.success = True
                    status.delivery_time = datetime.utcnow()
                    status.message_id = f"EMAIL-{int(time.time())}-{hash(subject) % 10000:04d}"
                    status.smtp_response = "OK"
                    
                    if self.debug_mode:
                        logger.info(f"✅ Email sent successfully - Message ID: {status.message_id}")
                
                break  # Success, exit retry loop
                
            except smtplib.SMTPAuthenticationError as e:
                status.error_message = f"Authentication failed: {str(e)}"
                logger.error(f"❌ SMTP Authentication Error: {e}")
                
                # Detect Gmail App Password issue
                if "Application-specific password required" in str(e):
                    status.error_message += " - Use Gmail App Password instead of regular password"
                    logger.error("💡 Recommendation: Use Gmail App Password for secure authentication")
                
                break  # Don't retry authentication errors
                
            except smtplib.SMTPRecipientsRefused as e:
                status.error_message = f"All recipients refused: {str(e)}"
                logger.error(f"❌ Recipients Refused: {e}")
                break  # Don't retry recipient errors
                
            except smtplib.SMTPServerDisconnected as e:
                status.error_message = f"Server disconnected: {str(e)}"
                logger.warning(f"⚠️ Server Disconnected (attempt {attempt + 1}): {e}")
                
            except smtplib.SMTPException as e:
                status.error_message = f"SMTP Error: {str(e)}"
                logger.warning(f"⚠️ SMTP Error (attempt {attempt + 1}): {e}")
                
            except Exception as e:
                status.error_message = f"Unexpected error: {str(e)}"
                logger.error(f"❌ Unexpected Error (attempt {attempt + 1}): {e}")
            
            finally:
                if server:
                    try:
                        server.quit()
                        if self.debug_mode:
                            logger.debug("👋 SMTP connection closed gracefully")
                    except Exception as e:
                        logger.warning(f"⚠️ Error closing SMTP connection: {e}")
            
            # Retry delay with exponential backoff
            if attempt < self.max_retries - 1:
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.info(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
        
        return status
    
    def send_alert(self, alert_type: str, case_id: str, subject: str, body: str, 
                   recipients: List[str], audit_logger=None) -> Dict:
        """
        Send alert email with comprehensive audit integration
        """
        try:
            logger.info(f"🚨 Sending {alert_type} alert for case {case_id} to {recipients}")
            
            # Send email
            email_status = self._send_smtp_email(subject, body, recipients)
            
            # Create comprehensive alert record
            alert_record = {
                "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
                "type": alert_type,
                "case_id": case_id,
                "subject": subject,
                "body_preview": body[:200] + "..." if len(body) > 200 else body,
                "recipients": recipients,
                "sent_at": datetime.utcnow().isoformat(),
                "status": "SENT" if email_status.success else "FAILED",
                "email_status": {
                    "success": email_status.success,
                    "message_id": email_status.message_id,
                    "attempts": email_status.attempts,
                    "error_message": email_status.error_message,
                    "delivery_time": email_status.delivery_time.isoformat() if email_status.delivery_time else None,
                    "smtp_response": email_status.smtp_response
                }
            }
            
            # Store alert
            self.sent_alerts.append(alert_record)
            
            # Log to audit if successful and audit logger provided
            if email_status.success and audit_logger:
                try:
                    # Convert email_status to JSON-serializable format
                    audit_email_status = email_status.__dict__.copy()
                    if audit_email_status.get('delivery_time'):
                        audit_email_status['delivery_time'] = audit_email_status['delivery_time'].isoformat()
                    
                    audit_logger.log_alert_sent(
                        user="SYSTEM",
                        case_id=case_id,
                        recipients=recipients,
                        alert_type=alert_type,
                        email_status=audit_email_status
                    )
                    logger.info(f"🔗 Alert logged to audit trail: {alert_record['alert_id']}")
                except Exception as e:
                    logger.error(f"❌ Failed to log alert to audit: {e}")
            
            # Log result
            if email_status.success:
                logger.info(f"✅ Alert sent successfully: {alert_record['alert_id']} to {recipients}")
            else:
                logger.error(f"❌ Alert failed: {alert_record['alert_id']} - {email_status.error_message}")
            
            return alert_record
            
        except Exception as e:
            error_msg = f"Critical error in send_alert: {str(e)}"
            logger.error(error_msg)
            return {
                "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
                "type": alert_type,
                "case_id": case_id,
                "status": "CRITICAL_ERROR",
                "error": error_msg,
                "sent_at": datetime.utcnow().isoformat()
            }

    def send_high_risk_alert(self, case_id: str, risk_score: float, recipients: List[str], audit_logger=None) -> Dict:
        """Send immediate alert for high-risk cases"""
        subject = f"🚨 ProofSAR Alert: HIGH RISK Case {case_id}"
        
        body = f"""
URGENT: High Risk SAR Case Detected
{'=' * 50}

Case ID: {case_id}
Risk Score: {risk_score:.1%}
Severity: CRITICAL
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Immediate review needed
- Review deadline: 24 hours
- Escalation to compliance head

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
Do not reply to this email.
        """
        
        return self.send_alert("HIGH_RISK", case_id, subject, body, recipients, audit_logger)
    
    def send_pending_review_alert(self, case_id: str, assigned_to: str, recipients: List[str], audit_logger=None) -> Dict:
        """Send alert for pending review"""
        subject = f"📋 ProofSAR: Review Pending - Case {case_id}"
        
        body = f"""
SAR Review Pending
{'=' * 50}

Case ID: {case_id}
Assigned To: {assigned_to}
Status: AWAITING APPROVAL
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Review generated SAR narrative
- Verify evidence linkage
- Approve or request modifications

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
        """
        
        return self.send_alert("PENDING_REVIEW", case_id, subject, body, recipients, audit_logger)
    
    def send_approval_notification(self, case_id: str, approver: str, recipients: List[str], audit_logger=None) -> Dict:
        """Send notification when SAR is approved"""
        subject = f"✅ ProofSAR: SAR Approved - Case {case_id}"
        
        body = f"""
SAR Approved and Filed
{'=' * 50}

Case ID: {case_id}
Approved By: {approver}
Status: FILED WITH FIU-IND
Timestamp: {datetime.utcnow().isoformat()}

Next Steps:
- SAR transmitted to Financial Intelligence Unit
- Case archived in compliance records
- 5-year retention period activated

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
        """
        
        return self.send_alert("APPROVED", case_id, subject, body, recipients, audit_logger)
    
    def send_rejection_notification(self, case_id: str, rejector: str, reason: str, recipients: List[str], audit_logger=None) -> Dict:
        """Send notification when SAR is rejected"""
        subject = f"❌ ProofSAR: SAR Rejected - Case {case_id}"
        
        body = f"""
SAR Rejected - Revision Required
{'=' * 50}

Case ID: {case_id}
Rejected By: {rejector}
Reason: {reason}
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Review rejection reason
- Revise SAR narrative
- Re-submit for approval

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
        """
        
        return self.send_alert("REJECTED", case_id, subject, body, recipients, audit_logger)
    
    def get_alert_history(self, case_id: str = None) -> List[Dict]:
        """Retrieve alert history"""
        if case_id:
            return [alert for alert in self.sent_alerts if alert["case_id"] == case_id]
        return self.sent_alerts
    
    def get_alert_stats(self) -> Dict:
        """Get comprehensive statistics about sent alerts"""
        total = len(self.sent_alerts)
        if total == 0:
            return {
                "total_sent": 0, 
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "by_type": {},
                "last_sent": None
            }
        
        successful = len([a for a in self.sent_alerts if a["status"] == "SENT"])
        failed = total - successful
        
        return {
            "total_sent": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total,
            "by_type": {
                alert_type: len([a for a in self.sent_alerts if a["type"] == alert_type])
                for alert_type in set(a["type"] for a in self.sent_alerts)
            },
            "last_sent": self.sent_alerts[-1]["sent_at"] if self.sent_alerts else None,
            "stats_generated": datetime.utcnow().isoformat()
        }
    
    def _send_email_with_retry(self, subject: str, text_body: str, html_body: str, 
                              recipients: List[str], priority: str = "normal") -> EmailStatus:
        """Send email with retry mechanism"""
        
        for attempt in range(self.config.retry_attempts):
            try:
                status = self._send_single_email(subject, text_body, html_body, recipients, priority)
                
                if status.status == "SENT":
                    return status
                else:
                    logger.warning(f"Email send attempt {attempt + 1} failed: {status.error}")
                    
                    if attempt < self.config.retry_attempts - 1:
                        time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                        
            except Exception as e:
                logger.error(f"Email send attempt {attempt + 1} exception: {str(e)}")
                
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
        
        # All attempts failed
        return EmailStatus(
            status="FAILED",
            error=f"Failed after {self.config.retry_attempts} attempts",
            attempts=self.config.retry_attempts
        )
    
    def _send_single_email(self, subject: str, text_body: str, html_body: str,
                          recipients: List[str], priority: str) -> EmailStatus:
        """Send a single email attempt"""
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.username
            msg['To'] = ', '.join(recipients)
            
            # Add priority headers
            if priority == "high":
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            elif priority == "low":
                msg['X-Priority'] = '5'
                msg['X-MSMail-Priority'] = 'Low'
            
            # Add body parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.set_debuglevel(0)  # Set to 1 for debugging
                server.timeout = self.config.timeout
                
                # Enforce STARTTLS
                if self.config.use_tls:
                    server.starttls(context=context)
                    logger.debug("STARTTLS encryption enabled")
                
                # Login
                server.login(self.config.username, self.config.password)
                
                # Send email
                text = msg.as_string()
                server.sendmail(self.config.username, recipients, text)
                
                logger.debug(f"Email sent successfully to {recipients}")
                
                return EmailStatus(
                    status="SENT",
                    message_id=f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    attempts=1
                )
        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "SMTP authentication failed. Check credentials."
            logger.error(f"{error_msg}: {str(e)}")
            return EmailStatus(status="FAILED", error=error_msg, attempts=1)
        
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = "All recipients refused."
            logger.error(f"{error_msg}: {str(e)}")
            return EmailStatus(status="FAILED", error=error_msg, attempts=1)
        
        except smtplib.SMTPServerDisconnected as e:
            error_msg = "SMTP server disconnected."
            logger.error(f"{error_msg}: {str(e)}")
            return EmailStatus(status="FAILED", error=error_msg, attempts=1)
        
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return EmailStatus(status="FAILED", error=error_msg, attempts=1)
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return EmailStatus(status="FAILED", error=error_msg, attempts=1)
    
    def _create_high_risk_html_body(self, case_id: str, risk_score: float) -> str:
        """Create HTML body for high risk alert"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 30px -30px; }}
                .alert-box {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .risk-score {{ font-size: 24px; font-weight: bold; color: #dc3545; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; margin: 30px -30px -30px -30px; text-align: center; color: #6c757d; }}
                .btn {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 HIGH RISK SAR ALERT</h1>
                    <p>Immediate attention required</p>
                </div>
                
                <div class="alert-box">
                    <strong>Case Details:</strong><br>
                    Case ID: {case_id}<br>
                    Risk Score: <span class="risk-score">{risk_score:.1%}</span><br>
                    Severity: CRITICAL<br>
                    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
                
                <h3>Action Required:</h3>
                <ul>
                    <li>Immediate review needed</li>
                    <li>Review deadline: 24 hours</li>
                    <li>Escalation to compliance head</li>
                </ul>
                
                <a href="https://proofsar.ai/case/{case_id}" class="btn">Access Case</a>
                
                <div class="footer">
                    <p>This is an automated alert from ProofSAR AI System.</p>
                    <p>Do not reply to this email. For support, contact compliance@barclays.com</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_high_risk_text_body(self, case_id: str, risk_score: float) -> str:
        """Create text body for high risk alert"""
        return f"""
URGENT: High Risk SAR Case Detected
{'=' * 50}

Case ID: {case_id}
Risk Score: {risk_score:.1%}
Severity: CRITICAL
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Immediate review needed
- Review deadline: 24 hours
- Escalation to compliance head

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
Do not reply to this email.
        """
    
    def _create_pending_review_html_body(self, case_id: str, assigned_to: str) -> str:
        """Create HTML body for pending review alert"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #007bff; color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 30px -30px; }}
                .info-box {{ background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; margin: 30px -30px -30px -30px; text-align: center; color: #6c757d; }}
                .btn {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 SAR Review Pending</h1>
                    <p>Case requires your attention</p>
                </div>
                
                <div class="info-box">
                    <strong>Case Details:</strong><br>
                    Case ID: {case_id}<br>
                    Assigned To: {assigned_to}<br>
                    Status: AWAITING APPROVAL<br>
                    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
                
                <h3>Action Required:</h3>
                <ul>
                    <li>Review generated SAR narrative</li>
                    <li>Verify evidence linkage</li>
                    <li>Approve or request modifications</li>
                </ul>
                
                <a href="https://proofsar.ai/case/{case_id}" class="btn">Access Case</a>
                
                <div class="footer">
                    <p>This is an automated alert from ProofSAR AI System.</p>
                    <p>For support, contact compliance@barclays.com</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_pending_review_text_body(self, case_id: str, assigned_to: str) -> str:
        """Create text body for pending review alert"""
        return f"""
SAR Review Pending
{'=' * 50}

Case ID: {case_id}
Assigned To: {assigned_to}
Status: AWAITING APPROVAL
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Review generated SAR narrative
- Verify evidence linkage
- Approve or request modifications

Access Case: https://proofsar.ai/case/{case_id}

This is an automated alert from ProofSAR AI System.
        """
    
    def _create_approval_html_body(self, case_id: str, approver: str) -> str:
        """Create HTML body for approval notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #28a745; color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 30px -30px; }}
                .success-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; margin: 30px -30px -30px -30px; text-align: center; color: #6c757d; }}
                .btn {{ display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ SAR Approved and Filed</h1>
                    <p>Case successfully processed</p>
                </div>
                
                <div class="success-box">
                    <strong>Case Details:</strong><br>
                    Case ID: {case_id}<br>
                    Approved By: {approver}<br>
                    Status: FILED WITH FIU-IND<br>
                    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
                
                <h3>Next Steps:</h3>
                <ul>
                    <li>SAR transmitted to Financial Intelligence Unit</li>
                    <li>Case archived in compliance records</li>
                    <li>5-year retention period activated</li>
                </ul>
                
                <a href="https://proofsar.ai/case/{case_id}" class="btn">View Case</a>
                
                <div class="footer">
                    <p>This is an automated notification from ProofSAR AI System.</p>
                    <p>For support, contact compliance@barclays.com</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_approval_text_body(self, case_id: str, approver: str) -> str:
        """Create text body for approval notification"""
        return f"""
SAR Approved and Filed
{'=' * 50}

Case ID: {case_id}
Approved By: {approver}
Status: FILED WITH FIU-IND
Timestamp: {datetime.utcnow().isoformat()}

Next Steps:
- SAR transmitted to Financial Intelligence Unit
- Case archived in compliance records
- 5-year retention period activated

Access Case: https://proofsar.ai/case/{case_id}

This is an automated notification from ProofSAR AI System.
        """
    
    def _create_rejection_html_body(self, case_id: str, rejector: str, reason: str) -> str:
        """Create HTML body for rejection notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 30px -30px; }}
                .warning-box {{ background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; margin: 30px -30px -30px -30px; text-align: center; color: #6c757d; }}
                .btn {{ display: inline-block; padding: 12px 24px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ SAR Rejected</h1>
                    <p>Revision required</p>
                </div>
                
                <div class="warning-box">
                    <strong>Case Details:</strong><br>
                    Case ID: {case_id}<br>
                    Rejected By: {rejector}<br>
                    Reason: {reason}<br>
                    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
                
                <h3>Action Required:</h3>
                <ul>
                    <li>Review rejection reason</li>
                    <li>Revise SAR narrative</li>
                    <li>Re-submit for approval</li>
                </ul>
                
                <a href="https://proofsar.ai/case/{case_id}" class="btn">Access Case</a>
                
                <div class="footer">
                    <p>This is an automated notification from ProofSAR AI System.</p>
                    <p>For support, contact compliance@barclays.com</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_rejection_text_body(self, case_id: str, rejector: str, reason: str) -> str:
        """Create text body for rejection notification"""
        return f"""
SAR Rejected - Revision Required
{'=' * 50}

Case ID: {case_id}
Rejected By: {rejector}
Reason: {reason}
Timestamp: {datetime.utcnow().isoformat()}

Action Required:
- Review rejection reason
- Revise SAR narrative
- Re-submit for approval

Access Case: https://proofsar.ai/case/{case_id}

This is an automated notification from ProofSAR AI System.
        """
    
    def get_alert_history(self, case_id: str = None) -> List[Dict]:
        """
        Retrieve alert history
        
        Args:
            case_id: Optional case ID to filter by
            
        Returns:
            List of alert records
        """
        all_alerts = self.sent_alerts + self.failed_alerts
        
        if case_id:
            return [alert for alert in all_alerts if alert.get("case_id") == case_id]
        
        return all_alerts
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """
        Get statistics about sent alerts
        
        Returns:
            Dictionary with alert statistics
        """
        total_sent = len(self.sent_alerts)
        total_failed = len(self.failed_alerts)
        
        sent_by_type = {}
        for alert in self.sent_alerts:
            alert_type = alert.get("type", "UNKNOWN")
            sent_by_type[alert_type] = sent_by_type.get(alert_type, 0) + 1
        
        failed_by_type = {}
        for alert in self.failed_alerts:
            alert_type = alert.get("type", "UNKNOWN")
            failed_by_type[alert_type] = failed_by_type.get(alert_type, 0) + 1
        
        return {
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": total_sent / (total_sent + total_failed) if (total_sent + total_failed) > 0 else 0,
            "sent_by_type": sent_by_type,
            "failed_by_type": failed_by_type,
            "last_sent": self.sent_alerts[-1]["sent_at"] if self.sent_alerts else None,
            "last_failed": self.failed_alerts[-1]["sent_at"] if self.failed_alerts else None
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection
        
        Returns:
            Dictionary with test results
        """
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.set_debuglevel(0)
                server.timeout = self.config.timeout
                
                if self.config.use_tls:
                    server.starttls(context=context)
                
                server.login(self.config.username, self.config.password)
                
                return {
                    "status": "SUCCESS",
                    "message": "SMTP connection test successful",
                    "server": self.config.smtp_server,
                    "port": self.config.smtp_port,
                    "username": self.config.username,
                    "tls_enabled": self.config.use_tls
                }
        
        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"SMTP connection test failed: {str(e)}",
                "server": self.config.smtp_server,
                "port": self.config.smtp_port,
                "username": self.config.username,
                "tls_enabled": self.config.use_tls
            }

# Async wrapper for future use
async def send_alert_async(alert_service: GmailAlertServiceV2, method_name: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Async wrapper for email sending (for future async implementation)
    
    Args:
        alert_service: GmailAlertServiceV2 instance
        method_name: Name of the method to call
        *args: Method arguments
        **kwargs: Method keyword arguments
        
    Returns:
        Dictionary with status and details
    """
    method = getattr(alert_service, method_name)
    return method(*args, **kwargs)
