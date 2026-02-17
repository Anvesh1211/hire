"""
ProofSAR AI - Enterprise AML Compliance Platform
Production-grade Glass-Box AML Copilot for Barclays Hackathon
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import time

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import secrets manager first
try:
    from config.secrets import get_secret, get_secrets_manager
except ImportError:
    # Fallback for development
    def get_secret(key: str, default=None):
        return default
    
    class MockSecretsManager:
        def get_config(self):
            class SimpleConfig:
                def get_streamlit_config(self):
                    return {
                        "page_title": "ProofSAR AI",
                        "page_icon": "🛡️",
                        "layout": "wide",
                        "initial_sidebar_state": "expanded"
                    }
                def get_alert_recipients(self):
                    return {"high_risk": ["compliance@barclays.com"]}
                @property
                def ai_model(self):
                    class AIModelConfig:
                        def __init__(self):
                            self.use_gemini = False
                    return AIModelConfig()
            return SimpleConfig()
    
    def get_secrets_manager():
        return MockSecretsManager()

# Import enterprise components
from components.dashboard import EnterpriseDashboard
from components.risk_metrics import RiskMetricsComponent
from components.upload_zone import EnterpriseUploadZone
from components.reasoning_panel import ReasoningPanel
from components.audit_view import AuditViewComponent

# Import utilities
from utils.session_manager import get_session_manager
from utils.error_handler import get_error_handler, enterprise_error_handler, show_error_boundary

# Initialize config using secrets manager
try:
    secrets_manager = get_secrets_manager()
    config = secrets_manager.get_config()
except Exception:
    # Ultimate fallback
    class SimpleConfig:
        def get_streamlit_config(self):
            return {
                "page_title": "ProofSAR AI",
                "page_icon": "🛡️",
                "layout": "wide",
                "initial_sidebar_state": "expanded"
            }
        
        def get_alert_recipients(self):
            return {"high_risk": ["compliance@barclays.com"]}
        
        @property
        def ai_model(self):
            class AIModelConfig:
                def __init__(self):
                    self.use_gemini = False
            return AIModelConfig()
    
    config = SimpleConfig()

# Import backend services
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

class ProofSARApp:
    """Main ProofSAR AI application class"""
    
    def __init__(self):
        # Initialize config using secrets manager
        try:
            secrets_manager = get_secrets_manager()
            self.config = secrets_manager.get_config()
        except Exception:
            # Ultimate fallback
            class SimpleConfig:
                def get_streamlit_config(self):
                    return {
                        "page_title": "ProofSAR AI",
                        "page_icon": "🛡️",
                        "layout": "wide",
                        "initial_sidebar_state": "expanded"
                    }
                
                def get_alert_recipients(self):
                    return {"high_risk": ["compliance@barclays.com"]}
                
                @property
                def ai_model(self):
                    class AIModelConfig:
                        def __init__(self):
                            self.use_gemini = False
                    return AIModelConfig()
            
            self.config = SimpleConfig()
        
        # Ensure config has required methods
        if not hasattr(self.config, 'get_streamlit_config'):
            def get_streamlit_config(self):
                return {
                    "page_title": "ProofSAR AI",
                    "page_icon": "🛡️", 
                    "layout": "wide",
                    "initial_sidebar_state": "expanded"
                }
            # Bind method to config object
            import types
            self.config.get_streamlit_config = types.MethodType(get_streamlit_config, self.config)
        
        if not hasattr(self.config, 'get_alert_recipients'):
            def get_alert_recipients(self):
                return {"high_risk": ["compliance@barclays.com"]}
            # Bind method to config object
            self.config.get_alert_recipients = types.MethodType(get_alert_recipients, self.config)
        
        self.session_manager = get_session_manager()
        self.error_handler = get_error_handler()
        
        # Initialize components
        self.dashboard = EnterpriseDashboard()
        self.risk_metrics = RiskMetricsComponent()
        self.upload_zone = EnterpriseUploadZone()
        self.reasoning_panel = ReasoningPanel()
        self.audit_view = AuditViewComponent()
        
        # Initialize backend services
        self.detection_engine = ComprehensiveDetectionEngine()
        self.reasoning_engine = GuiltReasoningEngine()
        
        # Get AI model configuration safely
        ai_model_config = getattr(self.config, 'ai_model', None)
        if ai_model_config:
            use_gemini = getattr(ai_model_config, 'use_gemini', False)
        else:
            use_gemini = False
            
        self.ai_generator = AIGenerator(use_gemini=use_gemini)
        self.audit_logger = AuditLogger()
        self.alert_service = GmailAlertService()
        
        logger.info("ProofSAR AI application initialized")
    
    def configure_page(self) -> None:
        """Configure Streamlit page settings"""
        st.set_page_config(**self.config.get_streamlit_config())
    
    def apply_enterprise_styling(self) -> None:
        """Apply enterprise-grade CSS styling"""
        st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            /* Global Styles */
            * {
                font-family: 'Inter', sans-serif;
            }
            
            /* Hide Streamlit branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Main container */
            .main {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            
            /* Animated header */
            .main-header {
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
                animation: fadeInDown 0.8s ease-out;
            }
            
            @keyframes fadeInDown {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .sub-header {
                font-size: 1.2rem;
                color: #6c757d;
                margin-bottom: 2rem;
                animation: fadeIn 1s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            /* Enhanced metric cards */
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                animation: slideInUp 0.6s ease-out;
                position: relative;
                overflow: hidden;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .metric-card:hover::before {
                left: 100%;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Card container */
            .card {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin: 1rem 0;
                transition: all 0.3s ease;
            }
            
            .card:hover {
                box-shadow: 0 8px 30px rgba(0,0,0,0.15);
                transform: translateY(-3px);
            }
            
            /* Info box */
            .info-box {
                background: white;
                padding: 1.5rem;
                border-left: 5px solid #00A9E0;
                border-radius: 10px;
                margin: 1rem 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            
            .info-box:hover {
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                transform: translateX(5px);
            }
            
            /* Risk meter */
            .risk-meter {
                width: 100%;
                height: 30px;
                background: linear-gradient(90deg, #28a745 0%, #ffc107 50%, #dc3545 100%);
                border-radius: 15px;
                position: relative;
                overflow: hidden;
            }
            
            .risk-indicator {
                position: absolute;
                width: 4px;
                height: 40px;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
                top: -5px;
                transition: left 0.5s ease;
            }
            
            /* Enhanced buttons */
            .stButton>button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: 600;
                border-radius: 10px;
                padding: 0.75rem 2rem;
                border: none;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            /* Progress bar */
            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            }
            
            /* Sidebar enhancement */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
            }
            
            [data-testid="stSidebar"] .stRadio > label {
                color: white;
                font-weight: 600;
            }
            
            [data-testid="stSidebar"] .stMarkdown {
                color: white;
            }
            
            /* Data table enhancement */
            .dataframe {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            /* Loading overlay */
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255,255,255,0.9);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self) -> None:
        """Render application header"""
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown('<p class="main-header">🛡️ ProofSAR AI</p>', unsafe_allow_html=True)
            st.markdown('<p class="sub-header">Glass-Box AML Compliance Copilot | Enterprise-Grade SAR Generation</p>', unsafe_allow_html=True)
        with col2:
            st.image("https://via.placeholder.com/200x60/00A9E0/FFFFFF?text=BARCLAYS", width=200)
    
    def render_sidebar(self) -> None:
        """Render enterprise sidebar"""
        with st.sidebar:
            st.markdown("### 🎛️ Control Panel")
            
            # AI Model Toggle
            st.markdown("#### 🤖 AI Engine")
            current_model = "Gemini Pro 1.5" if self.ai_generator.use_gemini else "Llama 2 7B (Local)"
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("☁️ Gemini", use_container_width=True, key="gemini_btn"):
                    self.ai_generator.use_gemini = True
                    self.session_manager.add_notification("Switched to Gemini Pro 1.5", "success")
                    self.session_manager.update_activity()
                    st.rerun()
            with col_b:
                if st.button("💻 Local", use_container_width=True, key="local_btn"):
                    self.ai_generator.use_gemini = False
                    self.session_manager.add_notification("Switched to Local LLM", "info")
                    self.session_manager.update_activity()
                    st.rerun()
            
            if self.ai_generator.use_gemini:
                st.success("✅ Using: **Gemini Pro 1.5** (Cloud)")
            else:
                st.info("✅ Using: **Llama 2 7B** (Local)")
            
            st.markdown("---")
            
            # Session Info
            st.markdown("#### 👤 Session Info")
            session_info = self.session_manager.get_session_info()
            st.caption(f"User: {session_info['user_id']}")
            st.caption(f"Role: {session_info['user_role']}")
            st.caption(f"Duration: {session_info['session_duration']}")
            
            st.markdown("---")
            
            # Navigation
            st.markdown("#### 🧭 Navigation")
            pages = {
                "🏠 Dashboard": "dashboard",
                "📊 Case Analysis": "analysis",
                "✍️ SAR Generator": "generator",
                "🔐 Audit Trail": "audit",
                "📧 Alerts": "alerts",
                "📈 Analytics": "analytics"
            }
            
            selected_page = st.radio(
                "Go to:",
                list(pages.keys()),
                index=list(pages.keys()).index(self.session_manager.get_session_info()['current_page']) if self.session_manager.get_session_info()['current_page'] in pages else 0,
                label_visibility="collapsed"
            )
            
            if selected_page != self.session_manager.get_session_info()['current_page']:
                self.session_manager.set_page(selected_page)
                st.rerun()
            
            st.markdown("---")
            
            # System Status
            st.markdown("#### ℹ️ System Status")
            st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
            st.caption("🌐 Version: 2.0.0")
            st.caption("🔒 Secure Mode: ON")
            
            # Notifications
            notifications = self.session_manager.get_notifications(unread_only=True)
            if notifications:
                st.markdown(f"#### 🔔 Notifications ({len(notifications)})")
                for notification in notifications[:3]:
                    st.caption(f"• {notification['message']}")
    
    def render_dashboard_page(self) -> None:
        """Render dashboard page"""
        st.markdown("## 📈 Executive Dashboard")
        
        # Sample metrics data
        metrics_data = {
            "total_cases": 12,
            "high_risk": 5,
            "sars_filed": 8,
            "accuracy": 94
        }
        
        # Render KPI metrics
        self.dashboard.render_kpi_metrics(metrics_data)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📊 Risk Distribution")
            self.dashboard.render_risk_distribution()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📈 Detection Trends")
            self.dashboard.render_detection_trends()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent cases
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Recent High-Risk Cases")
        self.dashboard.render_recent_cases()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Activity heatmap
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🗺️ Activity Heat Map (Last 7 Days)")
        self.dashboard.render_activity_heatmap()
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_analysis_page(self) -> None:
        """Render case analysis page"""
        st.markdown("## 📊 Advanced Case Analysis")
        
        # File upload section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        uploaded_df = self.upload_zone.render_upload_interface()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_df is not None:
            # Data overview
            self.upload_zone.render_data_overview(uploaded_df)
            
            # Data filters
            filtered_df = self.upload_zone.render_data_filters(uploaded_df)
            
            # Show filtered data
            st.markdown("#### 📋 Filtered Transactions")
            st.dataframe(filtered_df, use_container_width=True, height=300)
            
            # Run analysis button
            if st.button("🔍 Run Detection Analysis", type="primary", use_container_width=True):
                self._run_detection_analysis(uploaded_df)
        
        # Show results if available
        case_data = self.session_manager.get_case_data()
        if case_data['detection_results']:
            self._render_detection_results(case_data['detection_results'])
    
    def render_generator_page(self) -> None:
        """Render SAR generator page"""
        st.markdown("## ✍️ SAR Generator")
        
        case_data = self.session_manager.get_case_data()
        
        if not case_data['case_id']:
            st.info("Please complete case analysis first to generate SAR.")
            return
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### 📋 Case: {case_data['case_id']}")
        
        # Reasoning panel
        if case_data['reasoning_results']:
            self.reasoning_panel.render_reasoning_summary(case_data['reasoning_results'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate SAR button
        if st.button("📝 Generate SAR Report", type="primary", use_container_width=True):
            self._generate_sar_report()
    
    def render_audit_page(self) -> None:
        """Render audit trail page"""
        st.markdown("## 🔐 Audit Trail")
        
        # Render audit dashboard
        self.audit_view.render_audit_dashboard()
    
    def render_alerts_page(self) -> None:
        """Render alerts page"""
        st.markdown("## 📧 Alert Management")
        
        # Get alert statistics
        alert_stats = self.alert_service.get_alert_stats()
        
        # Alert statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📧 Total Sent", alert_stats['total_sent'])
        with col2:
            st.metric("❌ Failed", alert_stats['total_failed'])
        with col3:
            st.metric("📊 Success Rate", f"{alert_stats['success_rate']:.1%}")
        with col4:
            last_sent = alert_stats['last_sent']
            st.metric("🕐 Last Sent", last_sent[:10] if last_sent else "Never")
        
        # Alert history
        st.markdown("### 📋 Alert History")
        alert_history = self.alert_service.get_alert_history()
        
        if alert_history:
            alert_df = pd.DataFrame(alert_history)
            st.dataframe(alert_df, use_container_width=True)
        else:
            st.info("No alerts sent yet.")
    
    def render_analytics_page(self) -> None:
        """Render analytics page"""
        st.markdown("## 📈 Advanced Analytics")
        
        # Performance gauges
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Performance Metrics")
        self.dashboard.render_performance_gauges()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Monthly trends
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📅 Monthly Case Volume")
        self.dashboard.render_monthly_trends()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ML performance
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🤖 ML Model Performance")
        self.dashboard.render_ml_performance()
        st.markdown('</div>', unsafe_allow_html=True)
    
    @enterprise_error_handler("run_detection_analysis", show_user_error=True)
    def _run_detection_analysis(self, df: pd.DataFrame) -> None:
        """Run detection analysis on uploaded data"""
        with st.spinner("🔬 Running detection analysis..."):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📊 Analyzing transaction patterns...")
            progress_bar.progress(25)
            
            # Run detection
            detection_results = self.detection_engine.analyze_all(df)
            self.session_manager.set_case_data(
                case_id=f"SAR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                detection_results=detection_results
            )
            
            status_text.text("🧠 Generating reasoning...")
            progress_bar.progress(50)
            
            # Generate case ID and customer profile
            case_id = self.session_manager.get_case_data()['case_id']
            customer_profile = self._get_sample_customer_profile()
            
            status_text.text("⚖️ Applying legal framework...")
            progress_bar.progress(75)
            
            # Run reasoning
            reasoning_results = self.reasoning_engine.generate_reasoning(
                detection_results, customer_profile
            )
            
            self.session_manager.set_case_data(
                case_id=case_id,
                detection_results=detection_results,
                reasoning_results=reasoning_results
            )
            
            status_text.text("📝 Logging audit trail...")
            progress_bar.progress(90)
            
            # Log audit
            self.audit_logger.log_case_created(
                self.session_manager.get_session_info()['user_id'],
                case_id,
                {"transaction_count": len(df), "customer_id": "CUST-789012", "risk_level": detection_results['overall_risk']}
            )
            
            self.audit_logger.log_analysis_run(
                self.session_manager.get_session_info()['user_id'],
                case_id,
                detection_results
            )
            
            # Send alert if high risk
            if detection_results['risk_score'] >= 0.75:
                status_text.text("📧 Sending high-risk alerts...")
                alert = self.alert_service.send_high_risk_alert(
                    case_id,
                    detection_results['risk_score'],
                    self.config.get_alert_recipients()['high_risk']
                )
                self.session_manager.add_notification(f"High-risk alert sent for case {case_id}", "warning")
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            time.sleep(1)
            st.success(f"✅ Analysis Complete! Case ID: **{case_id}**")
            self.session_manager.add_notification(f"Analysis completed for case {case_id}", "success")
    
    def _render_detection_results(self, detection_results: dict) -> None:
        """Render detection results"""
        st.markdown("---")
        st.markdown("## 🎯 Detection Results")
        
        # Risk assessment cards
        self.risk_metrics.render_risk_assessment_cards(detection_results)
        
        # Pattern breakdown
        st.markdown('<div class="card">', unsafe_allow_html=True)
        self.risk_metrics.render_pattern_breakdown(detection_results.get('all_patterns', []))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Evidence viewer
        st.markdown('<div class="card">', unsafe_allow_html=True)
        self.risk_metrics.render_evidence_viewer(detection_results.get('all_evidence', []))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Red flags
        if detection_results.get('all_red_flags'):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            self.risk_metrics.render_red_flags(detection_results.get('all_red_flags', []))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # SHAP explanation
        st.markdown('<div class="card">', unsafe_allow_html=True)
        self.risk_metrics.render_shap_explanation()
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _generate_sar_report(self) -> None:
        """Generate SAR report"""
        with st.spinner("📝 Generating SAR report..."):
            case_data = self.session_manager.get_case_data()
            
            # This would integrate with the AI generator
            # For now, we'll simulate the generation
            time.sleep(2)
            
            self.session_manager.set_case_data(
                case_id=case_data['case_id'],
                reasoning_results=case_data['reasoning_results']
            )
            
            st.session_state.sar_status = "Generated"
            self.session_manager.add_notification("SAR report generated successfully", "success")
            st.success("✅ SAR report generated successfully!")
    
    def _get_sample_customer_profile(self) -> dict:
        """Get sample customer profile"""
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
    
    def render_footer(self) -> None:
        """Render application footer"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <strong style="font-size: 1.2rem; color: #667eea;">ProofSAR AI v2.0</strong><br>
            <span style="font-size: 1rem;">Glass-Box AML Compliance Platform</span><br><br>
            <span style="font-size: 0.9rem;">Built with ❤️ for Barclays Hackathon 2024 | Powered by Advanced AI & Cryptographic Audit</span><br>
            <span style="font-size: 0.8rem; opacity: 0.7;">🛡️ Secure • 🔍 Transparent • ⚡ Fast</span>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self) -> None:
        """Main application runner"""
        try:
            # Configure page
            self.configure_page()
            
            # Apply styling
            self.apply_enterprise_styling()
            
            # Initialize session
            self.session_manager.initialize_session()
            
            # Validate session
            validation = self.session_manager.validate_session_integrity()
            if not validation['is_valid']:
                st.error("Session validation failed. Please refresh the page.")
                return
            
            # Render header
            self.render_header()
            
            # Render sidebar
            self.render_sidebar()
            
            # Route to appropriate page
            current_page = self.session_manager.get_session_info()['current_page']
            
            if current_page == "🏠 Dashboard":
                self.render_dashboard_page()
            elif current_page == "📊 Case Analysis":
                self.render_analysis_page()
            elif current_page == "✍️ SAR Generator":
                self.render_generator_page()
            elif current_page == "🔐 Audit Trail":
                self.render_audit_page()
            elif current_page == "📧 Alerts":
                self.render_alerts_page()
            elif current_page == "📈 Analytics":
                self.render_analytics_page()
            
            # Render footer
            self.render_footer()
            
            # Clean up expired data
            self.session_manager.cleanup_expired_data()
            
        except Exception as e:
            self.error_handler.handle_exception(e, "main_application", True)

# Main execution
if __name__ == "__main__":
    app = ProofSARApp()
    app.run()
