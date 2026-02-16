"""
Enterprise Dashboard Components for ProofSAR AI
Production-grade AML compliance dashboard components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class EnterpriseDashboard:
    """Enterprise-grade dashboard component for AML compliance"""
    
    def __init__(self):
        self.risk_colors = {
            "CRITICAL": ("#dc3545", "🔴"),
            "HIGH": ("#fd7e14", "🟠"),
            "MEDIUM": ("#ffc107", "🟡"),
            "LOW": ("#28a745", "🟢")
        }
    
    def render_kpi_metrics(self, metrics_data: Dict) -> None:
        """Render executive KPI cards with professional styling"""
        col1, col2, col3, col4 = st.columns(4)
        
        kpi_configs = [
            {
                "col": col1,
                "title": "📁 Total Cases",
                "value": metrics_data.get("total_cases", 12),
                "delta": "+3 this week",
                "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            },
            {
                "col": col2,
                "title": "🚨 High Risk",
                "value": metrics_data.get("high_risk", 5),
                "delta": "Needs attention",
                "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            },
            {
                "col": col3,
                "title": "✅ SARs Filed",
                "value": metrics_data.get("sars_filed", 8),
                "delta": "Avg: 2 per week",
                "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            },
            {
                "col": col4,
                "title": "🎯 Accuracy",
                "value": f"{metrics_data.get('accuracy', 94)}%",
                "delta": "Above benchmark",
                "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
            }
        ]
        
        for i, config in enumerate(kpi_configs):
            with config["col"]:
                st.markdown(f"""
                <div class="metric-card" style="background: {config['gradient']}; animation-delay: {0.1 * (i + 1)}s;">
                    <h4 style="margin:0; font-size:1rem; opacity:0.9;">{config['title']}</h4>
                    <h1 style="margin:0.5rem 0; font-size:3rem;">{config['value']}</h1>
                    <p style="margin:0; font-size:0.9rem; opacity:0.8;">{config['delta']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    def render_risk_distribution(self, risk_data: Optional[pd.DataFrame] = None) -> None:
        """Render risk distribution pie chart"""
        if risk_data is None:
            risk_data = pd.DataFrame({
                'Risk Level': ['Critical', 'High', 'Medium', 'Low'],
                'Count': [2, 3, 4, 3],
                'Color': ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
            })
        
        fig = go.Figure(data=[go.Pie(
            labels=risk_data['Risk Level'],
            values=risk_data['Count'],
            hole=.4,
            marker=dict(colors=risk_data['Color']),
            textinfo='label+percent',
            textfont_size=14,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=True,
            height=350,
            margin=dict(t=30, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True, key="risk_pie")
    
    def render_detection_trends(self, trend_data: Optional[pd.DataFrame] = None) -> None:
        """Render detection trends line chart"""
        if trend_data is None:
            trend_data = pd.DataFrame({
                'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'Structuring': [3, 5, 4, 6],
                'Layering': [1, 2, 1, 3],
                'Smurfing': [2, 1, 3, 2]
            })
        
        fig = go.Figure()
        
        line_configs = [
            ('Structuring', '#667eea'),
            ('Layering', '#f093fb'),
            ('Smurfing', '#4facfe')
        ]
        
        for pattern, color in line_configs:
            fig.add_trace(go.Scatter(
                x=trend_data['Week'], 
                y=trend_data[pattern],
                mode='lines+markers',
                name=pattern,
                line=dict(color=color, width=3),
                marker=dict(size=10),
                hovertemplate=f'<b>{pattern}</b><br>%{{x}}<br>Cases: %{{y}}<extra></extra>'
            ))
        
        fig.update_layout(
            height=350,
            margin=dict(t=30, b=50, l=50, r=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            hovermode='x unified',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True, key="trend_line")
    
    def render_recent_cases(self, cases_data: Optional[pd.DataFrame] = None) -> None:
        """Render recent high-risk cases table"""
        if cases_data is None:
            cases_data = pd.DataFrame({
                'Case ID': ['SAR-1042', 'SAR-1041', 'SAR-1040', 'SAR-1039', 'SAR-1038'],
                'Customer': ['Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sunita Mehta', 'Vikram Singh'],
                'Risk Score': ['94%', '87%', '92%', '78%', '96%'],
                'Pattern': ['Structuring', 'Layering', 'Structuring', 'Smurfing', 'Structuring'],
                'Status': ['Under Review', 'Filed', 'Under Review', 'Filed', 'Approved'],
                'Date': ['2024-02-15', '2024-02-14', '2024-02-13', '2024-02-12', '2024-02-11']
            })
        
        def highlight_risk(val):
            if isinstance(val, str):
                if val.startswith('9'):
                    return 'background-color: #ffebee; font-weight: bold;'
                elif val.startswith('8'):
                    return 'background-color: #fff3e0; font-weight: bold;'
            return ''
        
        styled_df = cases_data.style.applymap(highlight_risk, subset=['Risk Score'])
        st.dataframe(styled_df, use_container_width=True, height=250)
    
    def render_activity_heatmap(self) -> None:
        """Render 7-day activity heatmap"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = list(range(24))
        
        # Generate sample heatmap data
        np.random.seed(42)
        activity_data = np.random.randint(0, 10, size=(len(hours), len(days)))
        
        fig = go.Figure(data=go.Heatmap(
            z=activity_data,
            x=days,
            y=hours,
            colorscale='RdYlGn_r',
            hoverongaps=False,
            hovertemplate='Day: %{x}<br>Hour: %{y}:00<br>Cases: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            height=400,
            xaxis_title="Day of Week",
            yaxis_title="Hour of Day",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True, key="heatmap")
    
    def render_performance_gauges(self) -> None:
        """Render ML performance gauge charts"""
        col1, col2, col3 = st.columns(3)
        
        gauge_configs = [
            {
                "col": col1,
                "value": 94,
                "title": "Detection Accuracy",
                "color": "#667eea",
                "reference": 90
            },
            {
                "col": col2,
                "value": 87,
                "title": "Processing Speed",
                "color": "#f093fb",
                "reference": None
            },
            {
                "col": col3,
                "value": 92,
                "title": "User Satisfaction",
                "color": "#4facfe",
                "reference": None
            }
        ]
        
        for config in gauge_configs:
            with config["col"]:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta" if config["reference"] else "gauge+number",
                    value=config["value"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': config["title"]},
                    delta={'reference': config["reference"]} if config["reference"] else None,
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': config["color"]},
                        'steps': [
                            {'range': [0, 70], 'color': "#ffebee"},
                            {'range': [70, 90], 'color': "#fff3e0"},
                            {'range': [90, 100], 'color': "#e8f5e9"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 95
                        } if config["reference"] else None
                    }
                ))
                
                fig.update_layout(height=300, margin=dict(t=50, b=0, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
    
    def render_monthly_trends(self) -> None:
        """Render monthly case volume trends"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        cases_2023 = [45, 52, 48, 61, 58, 67, 72, 69, 75, 81, 78, 85]
        cases_2024 = [88, 92] + [None] * 10
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=months,
            y=cases_2023,
            name='2023',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        fig.add_trace(go.Scatter(
            x=months[:2],
            y=cases_2024[:2],
            name='2024',
            line=dict(color='#f093fb', width=3, dash='dash'),
            fill='tozeroy',
            fillcolor='rgba(240, 147, 251, 0.3)'
        ))
        
        fig.update_layout(
            height=400,
            hovermode='x unified',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_ml_performance(self) -> None:
        """Render ML model performance metrics"""
        metrics = pd.DataFrame({
            'Metric': ['Precision', 'Recall', 'F1-Score', 'Accuracy'],
            'Structuring': [0.92, 0.89, 0.90, 0.94],
            'Layering': [0.88, 0.85, 0.86, 0.90],
            'Smurfing': [0.91, 0.87, 0.89, 0.93]
        })
        
        fig = go.Figure()
        
        for column in ['Structuring', 'Layering', 'Smurfing']:
            fig.add_trace(go.Bar(
                name=column,
                x=metrics['Metric'],
                y=metrics[column],
                text=metrics[column],
                textposition='auto',
                texttemplate='%{text:.2%}'
            ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', tickformat='.0%'),
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
