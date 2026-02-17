"""
Reusable UI components for ProofSAR AI
Minimal, enterprise fintech style
"""
import streamlit as st

# Local configuration for UI components
class Colors:
    PRIMARY = "#667eea"
    SECONDARY = "#764ba2"
    SUCCESS = "#28a745"
    WARNING = "#ffc107"
    DANGER = "#dc3545"
    INFO = "#17a2b8"
    LIGHT = "#f8f9fa"
    DARK = "#343a40"

class RISK_CONFIG:
    CRITICAL = 0.75
    HIGH = 0.5
    MEDIUM = 0.25
    LOW = 0.0


def init_theme_css():
    """Initialize clean, professional theme CSS"""
    st.markdown("""
    <style>
        /* Import clean font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Main container - clean gradient background */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #f0f3f7 100%);
            padding: 2rem 0;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
            padding-top: 2rem;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        
        [data-testid="stSidebar"] .stRadio > label {
            color: white !important;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Clean card styling */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* Typography */
        h1, h2, h3 {
            color: #2d3436;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        h2 { font-size: 1.5rem; margin-bottom: 1rem; }
        h3 { font-size: 1.25rem; margin-bottom: 0.75rem; }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Secondary button */
        .stButton > button[kind="secondary"] {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            box-shadow: none;
        }
        
        /* Data table */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Status badges */
        .badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .badge-critical {
            background: #ffe0e0;
            color: #c92a2a;
        }
        
        .badge-high {
            background: #fff4e0;
            color: #d97706;
        }
        
        .badge-medium {
            background: #fffde0;
            color: #b45309;
        }
        
        .badge-low {
            background: #e0f2e0;
            color: #16a34a;
        }
        
        /* Info box */
        .info-box {
            background: white;
            padding: 1.25rem;
            border-left: 4px solid #00a9e0;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            line-height: 1.6;
        }
        
        /* Success box */
        .success-box {
            background: #f0fdf4;
            border-left: 4px solid #16a34a;
            color: #166534;
        }
        
        /* Error box */
        .error-box {
            background: #fef2f2;
            border-left: 4px solid #dc2626;
            color: #991b1b;
        }
        
        /* Alert badge animation */
        @keyframes subtle-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        .pulse {
            animation: subtle-pulse 2s ease-in-out infinite;
        }
        
        /* Code block */
        .stCode {
            background: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
            border-radius: 6px !important;
        }
    </style>
    """, unsafe_allow_html=True)


def header_banner(title: str, subtitle: str = None, icon: str = "🛡️"):
    """Professional header banner"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"# {icon} {title}")
        if subtitle:
            st.markdown(f"<p style='color: #636e72; font-size: 1rem; margin-top: -1rem;'>{subtitle}</p>", 
                       unsafe_allow_html=True)
    
    with col2:
        # Placeholder for logo/branding
        st.markdown(
            "<div style='text-align: right; padding: 1rem;'><strong style='color: #667eea;'>v1.0</strong></div>",
            unsafe_allow_html=True
        )


def metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal", icon: str = "📊"):
    """Clean metric card display"""
    with st.container():
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="color: #636e72; font-size: 0.9rem; font-weight: 500; margin-bottom: 0.5rem;">{label}</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #2d3436;">{value}</div>
                    {f'<div style="color: #667eea; font-size: 0.85rem; margin-top: 0.5rem;">{delta}</div>' if delta else ''}
                </div>
                <div style="font-size: 2.5rem;">{icon}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def risk_badge(risk_level: str):
    """Display risk level badge"""
    config = RISK_CONFIG.get(risk_level, RISK_CONFIG["LOW"])
    
    st.markdown(f"""
    <div style="display: inline-block; margin: 0.5rem 0;">
        <span class="badge badge-{risk_level.lower()}">
            {config.emoji} {risk_level}
        </span>
    </div>
    """, unsafe_allow_html=True)


def info_section(title: str, content: str, icon: str = "ℹ️", box_type: str = "info"):
    """Information box with styled content"""
    box_classes = {
        "info": "info-box",
        "success": "info-box success-box",
        "error": "info-box error-box"
    }
    
    box_class = box_classes.get(box_type, "info-box")
    
    st.markdown(f"""
    <div class="{box_class}">
        <strong>{icon} {title}</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def data_table(df, title: str = None, height: int = 300, use_container_width: bool = True):
    """Display dataframe with consistent styling"""
    if title:
        st.markdown(f"#### {title}")
    
    st.dataframe(df, use_container_width=use_container_width, height=height)


def column_divider():
    """Add a subtle divider"""
    st.markdown("<hr style='border: 1px solid #e9ecef; margin: 2rem 0;'>", unsafe_allow_html=True)


def section_header(title: str, icon: str = None):
    """Section header with icon"""
    if icon:
        st.markdown(f"## {icon} {title}")
    else:
        st.markdown(f"## {title}")


def risk_gauge(risk_score: float, risk_level: str = "MEDIUM"):
    """Professional risk gauge display"""
    config = RISK_CONFIG.get(risk_level, RISK_CONFIG["LOW"])
    
    # Create gauge-like visualization
    percentage = risk_score * 100
    
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 8px; 
                border: 1px solid #e9ecef; margin: 1rem 0;">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 0.9rem; color: #636e72; margin-bottom: 0.5rem;">Risk Score</div>
            <div style="font-size: 3rem; font-weight: 700; color: {config.color}; margin-bottom: 0.5rem;">
                {config.emoji} {percentage:.0f}%
            </div>
        </div>
        <div style="background: #e9ecef; border-radius: 8px; overflow: hidden; height: 24px;">
            <div style="background: linear-gradient(90deg, #28a745 0%, #ffc107 50%, #dc3545 100%);
                        width: {percentage}%; height: 100%; transition: width 0.5s ease;"></div>
        </div>
        <div style="text-align: center; margin-top: 1rem; font-weight: 600; color: {config.color};">
            {risk_level} RISK
        </div>
    </div>
    """, unsafe_allow_html=True)


def footer():
    """Professional footer"""
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #636e72; padding-top: 2rem; padding-bottom: 1rem;">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">ProofSAR AI v1.0</div>
        <div style="font-size: 0.9rem; margin-bottom: 1rem;">Glass-Box AML Compliance Platform</div>
        <div style="font-size: 0.85rem; opacity: 0.7;">
            Built with ❤️ for Enterprise AML Compliance | Powered by Advanced AI & Cryptographic Audit
        </div>
    </div>
    """, unsafe_allow_html=True)
