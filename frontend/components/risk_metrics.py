"""
Risk Metrics Components for ProofSAR AI
Enterprise-grade risk assessment and visualization components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RiskMetricsComponent:
    """Enterprise-grade risk metrics visualization component"""
    
    def __init__(self):
        self.risk_colors = {
            "CRITICAL": ("#dc3545", "🔴"),
            "HIGH": ("#fd7e14", "🟠"),
            "MEDIUM": ("#ffc107", "🟡"),
            "LOW": ("#28a745", "🟢")
        }
    
    def render_risk_assessment_cards(self, detection_results: Dict) -> None:
        """Render risk assessment cards with professional styling"""
        col1, col2, col3 = st.columns(3)
        
        # Risk Level Card
        with col1:
            risk_level = detection_results.get('overall_risk', 'MEDIUM')
            color, emoji = self.risk_colors.get(risk_level, ("#6c757d", "⚪"))
            
            st.markdown(f"""
            <div class="card" style="text-align: center; background: linear-gradient(135deg, {color}22 0%, {color}44 100%);">
                <h3>Overall Risk Level</h3>
                <h1 style="font-size: 4rem; margin: 1rem 0;">{emoji}</h1>
                <h2 style="color: {color}; margin: 0;">{risk_level}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk Score Card
        with col2:
            risk_score = detection_results.get('risk_score', 0.5)
            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <h3>Risk Score</h3>
                <h1 style="font-size: 4rem; color: {color}; margin: 1rem 0;">{risk_score:.0%}</h1>
                <div class="risk-meter">
                    <div class="risk-indicator" style="left: {risk_score*100}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Patterns Detected Card
        with col3:
            pattern_count = len(detection_results.get('all_patterns', []))
            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <h3>Patterns Detected</h3>
                <h1 style="font-size: 4rem; color: #667eea; margin: 1rem 0;">{pattern_count}</h1>
                <p>Suspicious indicators found</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_risk_gauge(self, risk_score: float, title: str = "Risk Assessment") -> None:
        """Render an animated risk gauge chart"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': self._get_risk_color(risk_score)},
                'steps': [
                    {'range': [0, 25], 'color': "#e8f5e9"},
                    {'range': [25, 50], 'color': "#fff3e0"},
                    {'range': [50, 75], 'color': "#ffebee"},
                    {'range': [75, 100], 'color': "#ffebee"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(t=50, b=0, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_pattern_breakdown(self, patterns: List[str]) -> None:
        """Render suspicious patterns with professional styling"""
        if not patterns:
            st.info("No suspicious patterns detected.")
            return
        
        st.markdown("### 🚨 Suspicious Patterns Detected")
        
        for i, pattern in enumerate(patterns, 1):
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #dc3545;">
                <strong style="color: #dc3545;">Pattern {i}:</strong> {pattern}
            </div>
            """, unsafe_allow_html=True)
    
    def render_evidence_viewer(self, evidence_list: List[Dict]) -> None:
        """Render quantitative evidence with expandable sections"""
        if not evidence_list:
            st.info("No quantitative evidence available.")
            return
        
        st.markdown("### 📊 Quantitative Evidence")
        
        for evidence in evidence_list:
            pattern_name = evidence.get('pattern', f"Evidence {evidence_list.index(evidence) + 1}")
            with st.expander(f"🔍 {pattern_name}", expanded=False):
                # Create structured evidence display
                evidence_data = []
                for key, value in evidence.items():
                    if key != 'pattern':
                        evidence_data.append({"Metric": key.replace('_', ' ').title(), "Value": str(value)})
                
                if evidence_data:
                    evidence_df = pd.DataFrame(evidence_data)
                    st.dataframe(evidence_df, use_container_width=True)
    
    def render_red_flags(self, red_flags: List[str]) -> None:
        """Render critical red flags with emphasis"""
        if not red_flags:
            return
        
        st.markdown("### ⚠️ Critical Red Flags")
        
        for i, flag in enumerate(red_flags, 1):
            st.error(f"**{i}.** {flag}")
    
    def render_shap_importance(self, shap_values: Optional[Dict] = None) -> None:
        """Render SHAP feature importance chart"""
        if shap_values is None:
            # Generate sample SHAP data for demonstration
            shap_values = {
                'features': ['Transaction Amount', 'Frequency', 'Time Pattern', 'Account Age', 'Geographic Risk'],
                'values': [0.35, 0.28, 0.18, 0.12, 0.07]
            }
        
        fig = go.Figure(go.Bar(
            x=shap_values['values'],
            y=shap_values['features'],
            orientation='h',
            marker=dict(
                color=shap_values['values'],
                colorscale='RdYlBu_r',
                showscale=True
            ),
            text=[f"{val:.3f}" for val in shap_values['values']],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="SHAP Feature Importance",
            xaxis_title="SHAP Value",
            yaxis_title="Features",
            height=400,
            margin=dict(t=50, b=50, l=150, r=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_risk_timeline(self, timeline_data: Optional[pd.DataFrame] = None) -> None:
        """Render risk assessment timeline"""
        if timeline_data is None:
            # Generate sample timeline data
            dates = pd.date_range(start='2024-02-01', periods=30, freq='D')
            timeline_data = pd.DataFrame({
                'Date': dates,
                'Risk Score': np.random.uniform(0.2, 0.9, 30),
                'Event': [np.random.choice(['Transaction', 'Alert', 'Review']) for _ in range(30)]
            })
        
        fig = go.Figure()
        
        # Add risk score line
        fig.add_trace(go.Scatter(
            x=timeline_data['Date'],
            y=timeline_data['Risk Score'],
            mode='lines+markers',
            name='Risk Score',
            line=dict(color='#667eea', width=2),
            marker=dict(size=6),
            hovertemplate='Date: %{x}<br>Risk Score: %{y:.2%}<extra></extra>'
        ))
        
        # Add threshold line
        fig.add_hline(y=0.75, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
        
        fig.update_layout(
            title="Risk Assessment Timeline",
            xaxis_title="Date",
            yaxis_title="Risk Score",
            height=350,
            margin=dict(t=50, b=50, l=50, r=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_risk_color(self, risk_score: float) -> str:
        """Get color based on risk score"""
        if risk_score >= 0.75:
            return "#dc3545"
        elif risk_score >= 0.5:
            return "#fd7e14"
        elif risk_score >= 0.25:
            return "#ffc107"
        else:
            return "#28a745"
    
    def get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on score"""
        if risk_score >= 0.75:
            return "CRITICAL"
        elif risk_score >= 0.5:
            return "HIGH"
        elif risk_score >= 0.25:
            return "MEDIUM"
        else:
            return "LOW"
