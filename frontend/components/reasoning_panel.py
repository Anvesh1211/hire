"""
Reasoning Panel Components for ProofSAR AI
Enterprise-grade "Why Guilty" explainability components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ReasoningPanel:
    """Enterprise-grade reasoning and explainability panel"""
    
    def __init__(self):
        self.legal_frameworks = {
            "Prevention of Money Laundering Act, 2002": {
                "sections": ["Section 3", "Section 4", "Section 12"],
                "relevance": "Core AML legislation"
            },
            "PMLA Rules 2005": {
                "sections": ["Rule 9", "Rule 10"],
                "relevance": "Reporting requirements"
            },
            "FEMA Regulations": {
                "sections": ["Chapter III", "Chapter IV"],
                "relevance": "Foreign exchange transactions"
            }
        }
    
    def render_reasoning_summary(self, reasoning_results: Dict) -> None:
        """Render the main reasoning summary with executive focus"""
        if not reasoning_results:
            st.info("No reasoning results available.")
            return
        
        st.markdown("## ⚖️ Legal Reasoning Summary")
        
        # Executive summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_executive_summary(reasoning_results)
        
        with col2:
            self._render_compliance_score(reasoning_results)
        
        # Detailed reasoning sections
        st.markdown("---")
        self._render_legal_citations(reasoning_results)
        self._render_evidence_linkage(reasoning_results)
        self._render_risk_factors(reasoning_results)
    
    def _render_executive_summary(self, reasoning_results: Dict) -> None:
        """Render executive summary of reasoning"""
        st.markdown("### 📋 Executive Summary")
        
        summary = reasoning_results.get('executive_summary', 
            "Based on the analysis of transaction patterns, this case exhibits characteristics consistent with structuring and layering activities commonly associated with money laundering operations.")
        
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
            <p style="font-size: 1.1rem; line-height: 1.6;">{summary}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key findings
        key_findings = reasoning_results.get('key_findings', [
            "Multiple high-value transactions below reporting threshold",
            "Rapid succession of transactions suggesting structured placement",
            "Circular fund movement indicating layering behavior"
        ])
        
        st.markdown("#### 🔍 Key Findings:")
        for i, finding in enumerate(key_findings, 1):
            st.markdown(f"**{i}.** {finding}")
    
    def _render_compliance_score(self, reasoning_results: Dict) -> None:
        """Render compliance score gauge"""
        compliance_score = reasoning_results.get('compliance_score', 0.85)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=compliance_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Compliance Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 60], 'color': "#ffebee"},
                    {'range': [60, 80], 'color': "#fff3e0"},
                    {'range': [80, 100], 'color': "#e8f5e9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(t=50, b=0, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Score interpretation
        if compliance_score >= 0.9:
            st.success("✅ Strong compliance case")
        elif compliance_score >= 0.7:
            st.warning("⚠️ Moderate compliance concerns")
        else:
            st.error("❌ Significant compliance violations")
    
    def _render_legal_citations(self, reasoning_results: Dict) -> None:
        """Render legal framework citations"""
        st.markdown("### ⚖️ Legal Framework Citations")
        
        citations = reasoning_results.get('legal_citations', [])
        
        if not citations:
            # Default citations
            citations = [
                {
                    "act": "Prevention of Money Laundering Act, 2002",
                    "section": "Section 3",
                    "description": "Offence of money laundering",
                    "relevance": "Transaction patterns indicate proceeds of crime"
                },
                {
                    "act": "PMLA Rules 2005", 
                    "section": "Rule 9",
                    "description": "Maintenance of records",
                    "relevance": "Failure to maintain proper transaction records"
                }
            ]
        
        for citation in citations:
            with st.expander(f"📜 {citation.get('act', 'Legal Citation')}", expanded=False):
                st.markdown(f"""
                **Section/Rule:** {citation.get('section', 'N/A')}  
                **Description:** {citation.get('description', 'N/A')}  
                **Relevance:** {citation.get('relevance', 'N/A')}
                """)
    
    def _render_evidence_linkage(self, reasoning_results: Dict) -> None:
        """Render evidence linkage visualization"""
        st.markdown("### 🔗 Evidence Linkage")
        
        evidence_links = reasoning_results.get('evidence_linkage', [])
        
        if not evidence_links:
            # Generate sample evidence linkage
            evidence_links = [
                {
                    "evidence": "Multiple transactions of ₹49,999",
                    "pattern": "Structuring",
                    "legal_breach": "PMLA Section 3",
                    "strength": "Strong"
                },
                {
                    "evidence": "Transactions within 2-hour window",
                    "pattern": "Layering", 
                    "legal_breach": "PMLA Section 4",
                    "strength": "Moderate"
                }
            ]
        
        # Create evidence linkage table
        evidence_df = pd.DataFrame(evidence_links)
        
        def style_strength(val):
            if val == "Strong":
                return 'background-color: #ffebee; color: #c62828; font-weight: bold;'
            elif val == "Moderate":
                return 'background-color: #fff3e0; color: #ef6c00; font-weight: bold;'
            else:
                return 'background-color: #e8f5e9; color: #2e7d32; font-weight: bold;'
        
        styled_df = evidence_df.style.applymap(style_strength, subset=['strength'])
        st.dataframe(styled_df, use_container_width=True)
    
    def _render_risk_factors(self, reasoning_results: Dict) -> None:
        """Render risk factor analysis"""
        st.markdown("### 🎯 Risk Factor Analysis")
        
        risk_factors = reasoning_results.get('risk_factors', [])
        
        if not risk_factors:
            # Default risk factors
            risk_factors = [
                {"factor": "Transaction Structuring", "weight": 0.35, "score": 0.9},
                {"factor": "Timing Patterns", "weight": 0.25, "score": 0.8},
                {"factor": "Amount Patterns", "weight": 0.20, "score": 0.85},
                {"factor": "Account Behavior", "weight": 0.20, "score": 0.7}
            ]
        
        # Create risk factor visualization
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name="Risk Score",
            x=[rf['factor'] for rf in risk_factors],
            y=[rf['score'] for rf in risk_factors],
            marker=dict(color='#667eea'),
            text=[f"{rf['score']:.2f}" for rf in risk_factors],
            textposition='auto'
        ))
        
        fig.add_trace(go.Scatter(
            name="Weight",
            x=[rf['factor'] for rf in risk_factors],
            y=[rf['weight'] for rf in risk_factors],
            mode='markers',
            marker=dict(color='#f093fb', size=15),
            text=[f"Weight: {rf['weight']:.2f}" for rf in risk_factors],
            textposition='top center'
        ))
        
        fig.update_layout(
            title="Risk Factor Breakdown",
            xaxis_title="Risk Factor",
            yaxis_title="Score",
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_shap_explanation(self, shap_data: Optional[Dict] = None) -> None:
        """Render SHAP-based explainability"""
        st.markdown("### 🤖 AI Explainability (SHAP)")
        
        if shap_data is None:
            # Generate sample SHAP data
            shap_data = {
                'features': [
                    'Transaction Amount', 'Time Interval', 'Account Age', 
                    'Transaction Type', 'Geographic Risk', 'Frequency Pattern'
                ],
                'shap_values': [0.42, 0.31, 0.18, 0.15, 0.12, 0.08],
                'base_values': [0.25] * 6,
                'feature_values': [49999, 120, 365, 'DEBIT', 'HIGH', 15]
            }
        
        # SHAP waterfall chart
        fig = go.Figure()
        
        features = shap_data['features']
        shap_values = shap_data['shap_values']
        base_values = shap_data['base_values']
        
        # Calculate cumulative values for waterfall
        cumulative = [base_values[0]]
        for val in shap_values[:-1]:
            cumulative.append(cumulative[-1] + val)
        cumulative.append(cumulative[-1] + shap_values[-1])
        
        # Create waterfall effect
        for i in range(len(features)):
            color = '#667eea' if shap_values[i] > 0 else '#ef5350'
            
            fig.add_trace(go.Scatter(
                x=[i, i+1],
                y=[cumulative[i], cumulative[i]],
                mode='lines',
                line=dict(color=color, width=20),
                name=features[i],
                hovertemplate=f'<b>{features[i]}</b><br>SHAP: {shap_values[i]:.3f}<br>Value: {shap_data["feature_values"][i]}<extra></extra>'
            ))
        
        fig.update_layout(
            title="SHAP Waterfall Plot - Feature Contributions",
            xaxis_title="Features",
            yaxis_title="Risk Score",
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature importance table
        shap_df = pd.DataFrame({
            'Feature': features,
            'SHAP Value': shap_values,
            'Feature Value': shap_data['feature_values'],
            'Impact': ['Positive' if v > 0 else 'Negative' for v in shap_values]
        })
        
        st.markdown("#### 📊 Feature Importance Details")
        st.dataframe(shap_df, use_container_width=True)
    
    def render_compliance_checklist(self, reasoning_results: Dict) -> None:
        """Render compliance checklist"""
        st.markdown("### ✅ Compliance Checklist")
        
        checklist_items = reasoning_results.get('compliance_checklist', [
            {"item": "Suspicious Transaction Report (STR) criteria met", "status": "✅"},
            {"item": "Reporting threshold exceeded", "status": "✅"},
            {"item": "Pattern of structuring identified", "status": "✅"},
            {"item": "Evidence of layering activity", "status": "⚠️"},
            {"item": "Customer due diligence completed", "status": "✅"},
            {"item": "Source of funds verified", "status": "❌"}
        ])
        
        for item in checklist_items:
            status_icon = item.get('status', '❓')
            st.markdown(f"{status_icon} {item['item']}")
    
    def export_reasoning_report(self, reasoning_results: Dict) -> str:
        """Export reasoning report as formatted text"""
        report = f"""
PROOFSAR AI - REASONING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Case ID: {reasoning_results.get('case_id', 'N/A')}

EXECUTIVE SUMMARY
{reasoning_results.get('executive_summary', 'No summary available')}

KEY FINDINGS
"""
        
        findings = reasoning_results.get('key_findings', [])
        for i, finding in enumerate(findings, 1):
            report += f"{i}. {finding}\n"
        
        report += "\nLEGAL FRAMEWORK\n"
        citations = reasoning_results.get('legal_citations', [])
        for citation in citations:
            report += f"- {citation.get('act', 'N/A')} - {citation.get('section', 'N/A')}\n"
        
        return report
