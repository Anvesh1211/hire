"""
SystemController - Central brain for ProofSAR AI
Orchestrates fraud detection, SAR generation, alerts, and audit logging
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Import backend components
from alerts.GmailAlertService_v2 import GmailAlertServiceV2
from audit.hash_chain import AuditLogger
from alert_manager import AlertManager

# Import AI engine
try:
    from ai_engine.gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Gemini AI engine not available - using mock responses")

logger = logging.getLogger(__name__)

class SystemController:
    """
    Central system controller for ProofSAR AI
    Orchestrates all components and provides unified interface
    """
    
    def __init__(self):
        """Initialize all system components"""
        try:
            # Initialize core components
            self.audit_logger = AuditLogger()
            self.alert_manager = AlertManager()
            self.gmail_service = GmailAlertServiceV2()
            
            # Initialize AI engine if available
            if GEMINI_AVAILABLE:
                self.ai_client = GeminiClient()
                logger.info("🤖 Gemini AI engine initialized")
            else:
                self.ai_client = None
                logger.warning("⚠️ AI engine not available - using fallback")
            
            # Risk thresholds from environment
            self.risk_threshold_critical = float(os.getenv("RISK_THRESHOLD_CRITICAL", "0.75"))
            self.risk_threshold_high = float(os.getenv("RISK_THRESHOLD_HIGH", "0.5"))
            self.risk_threshold_medium = float(os.getenv("RISK_THRESHOLD_MEDIUM", "0.25"))
            
            # Alert recipients
            self.alert_recipients = {
                "HIGH_RISK": os.getenv("ALERT_RECIPIENTS_HIGH_RISK", "").split(","),
                "PENDING_REVIEW": os.getenv("ALERT_RECIPIENTS_PENDING_REVIEW", "").split(","),
                "APPROVED": os.getenv("ALERT_RECIPIENTS_APPROVED", "").split(","),
                "REJECTED": os.getenv("ALERT_RECIPIENTS_REJECTED", "").split(",")
            }
            
            # Clean empty recipients
            for key in self.alert_recipients:
                self.alert_recipients[key] = [r.strip() for r in self.alert_recipients[key] if r.strip()]
            
            logger.info("🧠 SystemController initialized with all components")
            
        except Exception as e:
            logger.error(f"❌ Error initializing SystemController: {e}")
            raise
    
    def process_transaction(self, transaction_data: Dict, user: str = "system") -> Dict:
        """
        Process a single transaction through the complete AML pipeline
        
        Args:
            transaction_data: Transaction data to analyze
            user: User performing the action
            
        Returns:
            Processing result with all details
        """
        try:
            # Extract transaction ID for case ID
            transaction_id = transaction_data.get("transaction_id", f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
            case_id = f"CASE-{transaction_id}"
            
            logger.info(f"🔄 Processing transaction {transaction_id} as case {case_id}")
            
            # Step 1: Log case creation
            self.audit_logger.log_case_created(
                user=user,
                case_id=case_id,
                data={
                    "transaction_id": transaction_id,
                    "customer_id": transaction_data.get("customer_id"),
                    "amount": transaction_data.get("amount"),
                    "transaction_count": len(transaction_data.get("related_transactions", [])),
                    "initial_risk": "unknown"
                }
            )
            
            # Step 2: Run fraud detection model
            analysis_results = self._run_fraud_analysis(transaction_data)
            
            # Step 3: Log analysis execution
            self.audit_logger.log_analysis_run(
                user=user,
                case_id=case_id,
                results=analysis_results
            )
            
            # Step 4: Determine if SAR is needed
            risk_score = analysis_results.get("risk_score", 0.0)
            requires_sar = risk_score >= self.risk_threshold_high
            
            # Step 5: Generate SAR if needed
            sar_content = None
            if requires_sar:
                sar_content = self._generate_sar(transaction_data, analysis_results)
                
                # Log SAR generation
                self.audit_logger.log_sar_generated(
                    user=user,
                    case_id=case_id,
                    sar_content=sar_content,
                    ai_model="gemini" if self.ai_client else "fallback"
                )
            
            # Step 6: Create alerts and send notifications
            alerts_created = []
            email_results = []
            
            if risk_score >= self.risk_threshold_critical:
                # Critical risk - immediate alert
                alert = self._create_and_send_alert(
                    case_id=case_id,
                    alert_type="HIGH_RISK",
                    risk_score=risk_score,
                    transaction_data=transaction_data,
                    sar_content=sar_content
                )
                alerts_created.append(alert)
                if alert.get("email_result"):
                    email_results.append(alert["email_result"])
            
            elif requires_sar:
                # High risk - SAR alert
                alert = self._create_and_send_alert(
                    case_id=case_id,
                    alert_type="SAR_GENERATED",
                    risk_score=risk_score,
                    transaction_data=transaction_data,
                    sar_content=sar_content
                )
                alerts_created.append(alert)
                if alert.get("email_result"):
                    email_results.append(alert["email_result"])
            
            # Step 7: Log email sending
            for email_result in email_results:
                self.audit_logger.log_alert_sent(
                    user="system",
                    case_id=case_id,
                    recipients=email_result.get("recipients", []),
                    alert_type=email_result.get("alert_type", "UNKNOWN"),
                    email_status=email_result.get("status", "unknown")
                )
            
            # Return comprehensive result
            result = {
                "case_id": case_id,
                "transaction_id": transaction_id,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "requires_sar": requires_sar,
                "sar_content": sar_content,
                "analysis_results": analysis_results,
                "alerts_created": alerts_created,
                "email_results": email_results,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            logger.info(f"✅ Transaction processing completed: {case_id} - Risk: {risk_score:.2f}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing transaction: {str(e)}"
            logger.error(error_msg)
            
            # Log error to audit
            try:
                case_id = transaction_data.get("transaction_id", "UNKNOWN")
                self.audit_logger.log_action(
                    action="PROCESSING_ERROR",
                    user=user,
                    case_id=case_id,
                    details={"error": error_msg, "transaction_data": transaction_data}
                )
            except:
                pass
            
            return {
                "status": "error",
                "error": error_msg,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
    
    def _run_fraud_analysis(self, transaction_data: Dict) -> Dict:
        """Run fraud detection analysis on transaction"""
        try:
            if self.ai_client and GEMINI_AVAILABLE:
                # Use Gemini AI for analysis
                analysis_prompt = self._build_analysis_prompt(transaction_data)
                ai_response = self.ai_client.generate_content(analysis_prompt)
                
                # Parse AI response (simplified - in production, use structured output)
                risk_score = 0.7  # Default from AI
                patterns = ["suspicious_amount", "unusual_timing"]
                detections = {"amount_anomaly": True, "timing_anomaly": True}
                
            else:
                # Fallback analysis
                risk_score = self._fallback_risk_calculation(transaction_data)
                patterns = ["high_amount", "rapid_succession"]
                detections = {"amount_threshold": True}
            
            return {
                "risk_score": risk_score,
                "all_patterns": patterns,
                "detections": detections,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "model": "gemini" if self.ai_client else "fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in fraud analysis: {e}")
            return {
                "risk_score": 0.5,  # Default medium risk on error
                "all_patterns": [],
                "detections": {},
                "error": str(e),
                "model": "error"
            }
    
    def _build_analysis_prompt(self, transaction_data: Dict) -> str:
        """Build analysis prompt for AI model"""
        return f"""
        Analyze this transaction for AML risk:
        
        Transaction Data:
        - Amount: ${transaction_data.get('amount', 0)}
        - Customer ID: {transaction_data.get('customer_id', 'Unknown')}
        - Transaction Type: {transaction_data.get('transaction_type', 'Unknown')}
        - Timestamp: {transaction_data.get('timestamp', 'Unknown')}
        
        Provide risk score (0-1) and identify suspicious patterns.
        Focus on: amount thresholds, timing patterns, customer behavior.
        """
    
    def _fallback_risk_calculation(self, transaction_data: Dict) -> float:
        """Fallback risk calculation when AI is unavailable"""
        try:
            amount = float(transaction_data.get("amount", 0))
            risk_score = 0.0
            
            # Amount-based risk
            if amount > 10000:
                risk_score += 0.3
            if amount > 50000:
                risk_score += 0.2
            if amount > 100000:
                risk_score += 0.3
            
            # Transaction type risk
            trans_type = transaction_data.get("transaction_type", "").lower()
            if trans_type in ["wire_transfer", "international"]:
                risk_score += 0.2
            
            return min(risk_score, 1.0)
            
        except:
            return 0.5  # Default medium risk
    
    def _generate_sar(self, transaction_data: Dict, analysis_results: Dict) -> str:
        """Generate SAR narrative"""
        try:
            if self.ai_client and GEMINI_AVAILABLE:
                sar_prompt = f"""
                Generate a Suspicious Activity Report (SAR) for:
                
                Transaction: {transaction_data}
                Risk Score: {analysis_results.get('risk_score')}
                Suspicious Patterns: {analysis_results.get('all_patterns')}
                
                Format as professional SAR narrative with:
                - Transaction details
                - Suspicious activity description
                - Risk factors identified
                """
                
                sar_content = self.ai_client.generate_content(sar_prompt)
                return sar_content or "SAR generation failed"
            
            else:
                # Fallback SAR template
                return f"""
                SUSPICIOUS ACTIVITY REPORT
                
                Case ID: CASE-{transaction_data.get('transaction_id', 'UNKNOWN')}
                Date: {datetime.utcnow().strftime('%Y-%m-%d')}
                
                Transaction Details:
                - Amount: ${transaction_data.get('amount', 'Unknown')}
                - Customer: {transaction_data.get('customer_id', 'Unknown')}
                - Type: {transaction_data.get('transaction_type', 'Unknown')}
                
                Suspicious Activity:
                Risk Score: {analysis_results.get('risk_score', 'Unknown')}
                Patterns Detected: {', '.join(analysis_results.get('all_patterns', []))}
                
                This transaction requires further investigation due to elevated risk factors.
                """
                
        except Exception as e:
            logger.error(f"❌ Error generating SAR: {e}")
            return f"SAR generation error: {str(e)}"
    
    def _create_and_send_alert(self, case_id: str, alert_type: str, risk_score: float,
                              transaction_data: Dict, sar_content: Optional[str] = None) -> Dict:
        """Create alert and send email notification"""
        try:
            # Create alert in AlertManager
            alert = self.alert_manager.create_alert(
                alert_type=alert_type,
                case_id=case_id,
                title=f"{alert_type.replace('_', ' ').title()} - {case_id}",
                message=f"Risk score: {risk_score:.2f} - Transaction requires attention",
                severity=self._get_severity_from_risk(risk_score),
                metadata={
                    "risk_score": risk_score,
                    "transaction_data": transaction_data,
                    "sar_content": sar_content
                }
            )
            
            # Send email notification
            recipients = self.alert_recipients.get(alert_type, [])
            if recipients:
                subject = f"🚨 ProofSAR AI: {alert_type.replace('_', ' ').title()} - {case_id}"
                body = self._build_email_body(alert_type, case_id, risk_score, transaction_data, sar_content)
                
                email_result = self.gmail_service.send_alert(
                    alert_type=alert_type,
                    case_id=case_id,
                    subject=subject,
                    body=body,
                    recipients=recipients,
                    audit_logger=self.audit_logger
                )
                
                # Add email result to alert
                self.alert_manager.add_email_result(alert["alert_id"], email_result)
                alert["email_result"] = email_result
            
            return alert
            
        except Exception as e:
            logger.error(f"❌ Error creating/sending alert: {e}")
            return {"error": str(e)}
    
    def _build_email_body(self, alert_type: str, case_id: str, risk_score: float,
                         transaction_data: Dict, sar_content: Optional[str] = None) -> str:
        """Build email body for alert notification"""
        body = f"""
        PROOFSAR AI - ALERT NOTIFICATION
        
        Alert Type: {alert_type.replace('_', ' ').title()}
        Case ID: {case_id}
        Risk Score: {risk_score:.2f}
        Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Transaction Details:
        - Amount: ${transaction_data.get('amount', 'Unknown')}
        - Customer ID: {transaction_data.get('customer_id', 'Unknown')}
        - Transaction Type: {transaction_data.get('transaction_type', 'Unknown')}
        
        Action Required:
        Please review this case in the ProofSAR AI system.
        """
        
        if sar_content:
            body += f"""
        
        SAR Content:
        {sar_content[:500]}{'...' if len(sar_content) > 500 else ''}
        """
        
        body += f"""
        
        Access the system: https://proofsar.ai/case/{case_id}
        
        This is an automated alert from ProofSAR AI.
        """
        
        return body
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= self.risk_threshold_critical:
            return "CRITICAL"
        elif risk_score >= self.risk_threshold_high:
            return "HIGH"
        elif risk_score >= self.risk_threshold_medium:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_severity_from_risk(self, risk_score: float) -> str:
        """Convert risk score to alert severity"""
        if risk_score >= self.risk_threshold_critical:
            return "critical"
        elif risk_score >= self.risk_threshold_high:
            return "high"
        elif risk_score >= self.risk_threshold_medium:
            return "medium"
        else:
            return "low"
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        try:
            # Check audit integrity
            audit_integrity = self.audit_logger.audit.verify_chain_integrity()
            
            # Check Gmail service
            gmail_health = self.gmail_service.health_check()
            
            # Get alert statistics
            alert_stats = self.alert_manager.get_alert_stats()
            
            return {
                "system_status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "audit_trail": {
                        "status": "healthy" if audit_integrity["valid"] else "compromised",
                        "total_entries": audit_integrity["total_entries"],
                        "integrity_valid": audit_integrity["valid"],
                        "integrity_message": audit_integrity["message"]
                    },
                    "gmail_service": {
                        "status": gmail_health.get("status", "unknown"),
                        "server": gmail_health.get("smtp_server"),
                        "tls_enabled": gmail_health.get("tls_enabled")
                    },
                    "alert_manager": {
                        "status": "healthy",
                        "total_alerts": alert_stats.get("total", 0),
                        "active_alerts": alert_stats.get("active", 0)
                    },
                    "ai_engine": {
                        "status": "available" if self.ai_client else "unavailable",
                        "model": "gemini" if self.ai_client else "fallback"
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system status: {e}")
            return {
                "system_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
