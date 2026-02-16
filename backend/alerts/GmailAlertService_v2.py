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
    """Email sending status"""
    status: str  # "SENT", "FAILED", "RETRYING"
    message_id: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

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
    
    def __init__(self, config: Optional[EmailConfig] = None):
        """Initialize email service with configuration"""
        self.config = config or self._load_config_from_env()
        self.sent_alerts = []  # Store for audit trail
        self.failed_alerts = []  # Store failed attempts
        
        # Validate configuration
        self._validate_config()
        
        logger.info(f"GmailAlertServiceV2 initialized with server: {self.config.smtp_server}")
    
    def _load_config_from_env(self) -> EmailConfig:
        """Load configuration from environment variables"""
        return EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("EMAIL_USERNAME", ""),
            password=os.getenv("EMAIL_PASSWORD", ""),
            use_tls=os.getenv("EMAIL_USE_TLS", "true").lower() == "true",
            timeout=int(os.getenv("EMAIL_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("EMAIL_RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("EMAIL_RETRY_DELAY", "1.0"))
        )
    
    def _validate_config(self) -> None:
        """Validate email configuration"""
        if not self.config.username:
            raise ValueError("EMAIL_USERNAME environment variable is required")
        
        if not self.config.password:
            raise ValueError("EMAIL_PASSWORD environment variable is required")
        
        if self.config.smtp_port < 1 or self.config.smtp_port > 65535:
            raise ValueError("Invalid SMTP port")
        
        if self.config.timeout < 1:
            raise ValueError("Email timeout must be at least 1 second")
    
    def send_high_risk_alert(self, case_id: str, risk_score: float, recipients: List[str]) -> Dict[str, Any]:
        """
        Send immediate alert for high-risk cases
        
        Args:
            case_id: Unique case identifier
            risk_score: Risk score (0.0 to 1.0)
            recipients: List of email addresses
            
        Returns:
            Dictionary with status and details
        """
        try:
            subject = f"🚨 ProofSAR Alert: HIGH RISK Case {case_id}"
            
            # Create HTML body
            html_body = self._create_high_risk_html_body(case_id, risk_score)
            text_body = self._create_high_risk_text_body(case_id, risk_score)
            
            # Send email with retry mechanism
            status = self._send_email_with_retry(
                subject=subject,
                text_body=text_body,
                html_body=html_body,
                recipients=recipients,
                priority="high"
            )
            
            # Log the attempt
            alert_record = {
                "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
                "type": "HIGH_RISK",
                "case_id": case_id,
                "risk_score": risk_score,
                "subject": subject,
                "recipients": recipients,
                "status": status.status,
                "error": status.error,
                "attempts": status.attempts,
                "sent_at": status.timestamp.isoformat()
            }
            
            if status.status == "SENT":
                self.sent_alerts.append(alert_record)
                logger.info(f"High risk alert sent successfully for case {case_id}")
            else:
                self.failed_alerts.append(alert_record)
                logger.error(f"Failed to send high risk alert for case {case_id}: {status.error}")
            
            return alert_record
            
        except Exception as e:
            logger.error(f"Exception in send_high_risk_alert: {str(e)}")
            logger.debug(traceback.format_exc())
            
            error_record = {
                "alert_id": f"ALERT-{len(self.failed_alerts) + 1:04d}",
                "type": "HIGH_RISK",
                "case_id": case_id,
                "status": "FAILED",
                "error": str(e),
                "sent_at": datetime.now().isoformat()
            }
            self.failed_alerts.append(error_record)
            return error_record
    
    def send_pending_review_alert(self, case_id: str, assigned_to: str, recipients: List[str]) -> Dict[str, Any]:
        """
        Send alert for pending review
        
        Args:
            case_id: Unique case identifier
            assigned_to: Person assigned to review
            recipients: List of email addresses
            
        Returns:
            Dictionary with status and details
        """
        try:
            subject = f"📋 ProofSAR: Review Pending - Case {case_id}"
            
            html_body = self._create_pending_review_html_body(case_id, assigned_to)
            text_body = self._create_pending_review_text_body(case_id, assigned_to)
            
            status = self._send_email_with_retry(
                subject=subject,
                text_body=text_body,
                html_body=html_body,
                recipients=recipients,
                priority="medium"
            )
            
            alert_record = {
                "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
                "type": "PENDING_REVIEW",
                "case_id": case_id,
                "assigned_to": assigned_to,
                "subject": subject,
                "recipients": recipients,
                "status": status.status,
                "error": status.error,
                "attempts": status.attempts,
                "sent_at": status.timestamp.isoformat()
            }
            
            if status.status == "SENT":
                self.sent_alerts.append(alert_record)
                logger.info(f"Pending review alert sent for case {case_id}")
            else:
                self.failed_alerts.append(alert_record)
                logger.error(f"Failed to send pending review alert for case {case_id}: {status.error}")
            
            return alert_record
            
        except Exception as e:
            logger.error(f"Exception in send_pending_review_alert: {str(e)}")
            
            error_record = {
                "alert_id": f"ALERT-{len(self.failed_alerts) + 1:04d}",
                "type": "PENDING_REVIEW",
                "case_id": case_id,
                "status": "FAILED",
                "error": str(e),
                "sent_at": datetime.now().isoformat()
            }
            self.failed_alerts.append(error_record)
            return error_record
    
    def send_approval_notification(self, case_id: str, approver: str, recipients: List[str]) -> Dict[str, Any]:
        """
        Send notification when SAR is approved
        
        Args:
            case_id: Unique case identifier
            approver: Person who approved
            recipients: List of email addresses
            
        Returns:
            Dictionary with status and details
        """
        try:
            subject = f"✅ ProofSAR: SAR Approved - Case {case_id}"
            
            html_body = self._create_approval_html_body(case_id, approver)
            text_body = self._create_approval_text_body(case_id, approver)
            
            status = self._send_email_with_retry(
                subject=subject,
                text_body=text_body,
                html_body=html_body,
                recipients=recipients,
                priority="low"
            )
            
            alert_record = {
                "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
                "type": "APPROVED",
                "case_id": case_id,
                "approver": approver,
                "subject": subject,
                "recipients": recipients,
                "status": status.status,
                "error": status.error,
                "attempts": status.attempts,
                "sent_at": status.timestamp.isoformat()
            }
            
            if status.status == "SENT":
                self.sent_alerts.append(alert_record)
                logger.info(f"Approval notification sent for case {case_id}")
            else:
                self.failed_alerts.append(alert_record)
                logger.error(f"Failed to send approval notification for case {case_id}: {status.error}")
            
            return alert_record
            
        except Exception as e:
            logger.error(f"Exception in send_approval_notification: {str(e)}")
            
            error_record = {
                "alert_id": f"ALERT-{len(self.failed_alerts) + 1:04d}",
                "type": "APPROVED",
                "case_id": case_id,
                "status": "FAILED",
                "error": str(e),
                "sent_at": datetime.now().isoformat()
            }
            self.failed_alerts.append(error_record)
            return error_record
    
    def send_rejection_notification(self, case_id: str, rejector: str, reason: str, recipients: List[str]) -> Dict[str, Any]:
        """
        Send notification when SAR is rejected
        
        Args:
            case_id: Unique case identifier
            rejector: Person who rejected
            reason: Rejection reason
            recipients: List of email addresses
            
        Returns:
            Dictionary with status and details
        """
        try:
            subject = f"❌ ProofSAR: SAR Rejected - Case {case_id}"
            
            html_body = self._create_rejection_html_body(case_id, rejector, reason)
            text_body = self._create_rejection_text_body(case_id, rejector, reason)
            
            status = self._send_email_with_retry(
                subject=subject,
                text_body=text_body,
                html_body=html_body,
                recipients=recipients,
                priority="medium"
            )
            
            alert_record = {
                "alert_id": f"ALERT-{len(self.sent_alerts) + 1:04d}",
                "type": "REJECTED",
                "case_id": case_id,
                "rejector": rejector,
                "reason": reason,
                "subject": subject,
                "recipients": recipients,
                "status": status.status,
                "error": status.error,
                "attempts": status.attempts,
                "sent_at": status.timestamp.isoformat()
            }
            
            if status.status == "SENT":
                self.sent_alerts.append(alert_record)
                logger.info(f"Rejection notification sent for case {case_id}")
            else:
                self.failed_alerts.append(alert_record)
                logger.error(f"Failed to send rejection notification for case {case_id}: {status.error}")
            
            return alert_record
            
        except Exception as e:
            logger.error(f"Exception in send_rejection_notification: {str(e)}")
            
            error_record = {
                "alert_id": f"ALERT-{len(self.failed_alerts) + 1:04d}",
                "type": "REJECTED",
                "case_id": case_id,
                "status": "FAILED",
                "error": str(e),
                "sent_at": datetime.now().isoformat()
            }
            self.failed_alerts.append(error_record)
            return error_record
    
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
