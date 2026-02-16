"""
Audit View Components for ProofSAR AI
Enterprise-grade audit trail and cryptographic verification components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
import logging
import hashlib
import json
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class AuditViewComponent:
    """Enterprise-grade audit trail visualization component"""
    
    def __init__(self):
        self.audit_colors = {
            "CREATED": ("#28a745", "✅"),
            "ANALYZED": ("#007bff", "🔍"),
            "ALERT_SENT": ("#fd7e14", "📧"),
            "APPROVED": ("#28a745", "✅"),
            "REJECTED": ("#dc3545", "❌"),
            "MODIFIED": ("#ffc107", "📝")
        }
    
    def render_audit_dashboard(self, audit_data: Optional[Dict] = None) -> None:
        """Render comprehensive audit dashboard"""
        st.markdown("## 🔐 Audit Trail Dashboard")
        
        if audit_data is None:
            # Generate sample audit data
            audit_data = self._generate_sample_audit_data()
        
        # Key metrics
        self._render_audit_metrics(audit_data)
        
        # Timeline visualization
        self._render_audit_timeline(audit_data)
        
        # Detailed audit log
        self._render_audit_log(audit_data)
        
        # Cryptographic verification
        self._render_crypto_verification(audit_data)
    
    def _render_audit_metrics(self, audit_data: Dict) -> None:
        """Render audit metrics cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_events = len(audit_data.get('events', []))
            st.metric("📊 Total Events", total_events)
        
        with col2:
            cases_created = len([e for e in audit_data.get('events', []) if e['event_type'] == 'CREATED'])
            st.metric("📁 Cases Created", cases_created)
        
        with col3:
            alerts_sent = len([e for e in audit_data.get('events', []) if e['event_type'] == 'ALERT_SENT'])
            st.metric("📧 Alerts Sent", alerts_sent)
        
        with col4:
            last_event = audit_data.get('events', [{}])[-1].get('timestamp', '')
            if last_event:
                st.metric("🕐 Last Activity", self._format_timestamp(last_event))
    
    def _render_audit_timeline(self, audit_data: Dict) -> None:
        """Render audit timeline visualization"""
        st.markdown("### 📅 Audit Timeline")
        
        events = audit_data.get('events', [])
        if not events:
            st.info("No audit events found.")
            return
        
        # Prepare timeline data
        timeline_data = []
        for event in events:
            timeline_data.append({
                'timestamp': pd.to_datetime(event['timestamp']),
                'event_type': event['event_type'],
                'case_id': event.get('case_id', 'N/A'),
                'user': event.get('user', 'system'),
                'description': event.get('description', '')
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create timeline visualization
        fig = go.Figure()
        
        event_types = timeline_df['event_type'].unique()
        colors = ['#28a745', '#007bff', '#fd7e14', '#dc3545', '#ffc107']
        
        for i, event_type in enumerate(event_types):
            event_data = timeline_df[timeline_df['event_type'] == event_type]
            
            fig.add_trace(go.Scatter(
                x=event_data['timestamp'],
                y=[i] * len(event_data),
                mode='markers+lines',
                name=event_type,
                marker=dict(
                    size=12,
                    color=colors[i % len(colors)]
                ),
                line=dict(width=2),
                hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Case: %{customdata}<extra></extra>',
                customdata=event_data['case_id']
            ))
        
        fig.update_layout(
            title="Audit Event Timeline",
            xaxis_title="Timestamp",
            yaxis_title="Event Type",
            height=400,
            margin=dict(t=50, b=50, l=100, r=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_audit_log(self, audit_data: Dict) -> None:
        """Render detailed audit log table"""
        st.markdown("### 📋 Detailed Audit Log")
        
        events = audit_data.get('events', [])
        if not events:
            st.info("No audit events found.")
            return
        
        # Prepare audit log data
        log_data = []
        for event in events:
            log_data.append({
                'Timestamp': self._format_timestamp(event['timestamp']),
                'Event Type': event['event_type'],
                'Case ID': event.get('case_id', 'N/A'),
                'User': event.get('user', 'system'),
                'Description': event.get('description', ''),
                'Hash': event.get('hash', '')[:16] + '...' if event.get('hash') else ''
            })
        
        log_df = pd.DataFrame(log_data)
        
        # Style the dataframe
        def style_event_type(val):
            color, _ = self.audit_colors.get(val, ("#6c757d", "⚪"))
            return f'background-color: {color}22; color: {color}; font-weight: bold;'
        
        styled_df = log_df.style.applymap(style_event_type, subset=['Event Type'])
        st.dataframe(styled_df, use_container_width=True, height=400)
    
    def _render_crypto_verification(self, audit_data: Dict) -> None:
        """Render cryptographic verification section"""
        st.markdown("### 🔒 Cryptographic Verification")
        
        # Hash chain verification
        st.markdown("#### 🔗 Hash Chain Integrity")
        
        events = audit_data.get('events', [])
        if not events:
            st.info("No events to verify.")
            return
        
        # Verify hash chain
        is_valid, verification_details = self._verify_hash_chain(events)
        
        if is_valid:
            st.success("✅ Hash chain integrity verified")
        else:
            st.error("❌ Hash chain integrity compromised")
        
        # Show verification details
        with st.expander("🔍 Verification Details", expanded=False):
            for detail in verification_details:
                st.markdown(f"• {detail}")
        
        # Merkle tree visualization
        st.markdown("#### 🌳 Merkle Tree Verification")
        
        merkle_root = self._calculate_merkle_root(events)
        if merkle_root:
            st.code(f"Merkle Root: {merkle_root}", language='text')
            
            # Verify specific event
            col1, col2 = st.columns(2)
            with col1:
                event_index = st.number_input(
                    "Verify Event Index",
                    min_value=0,
                    max_value=len(events) - 1,
                    value=0,
                    step=1
                )
            
            with col2:
                if st.button("🔍 Verify Event"):
                    if event_index < len(events):
                        event = events[event_index]
                        is_valid = self._verify_event_hash(event)
                        
                        if is_valid:
                            st.success(f"✅ Event {event_index} hash verified")
                        else:
                            st.error(f"❌ Event {event_index} hash verification failed")
    
    def _verify_hash_chain(self, events: List[Dict]) -> tuple[bool, List[str]]:
        """Verify the integrity of the hash chain"""
        details = []
        
        if len(events) < 2:
            details.append("Insufficient events for chain verification")
            return True, details
        
        for i in range(1, len(events)):
            prev_hash = events[i-1].get('hash', '')
            curr_prev_hash = events[i].get('previous_hash', '')
            
            if prev_hash != curr_prev_hash:
                details.append(f"Hash mismatch at event {i}")
                details.append(f"Expected: {prev_hash}")
                details.append(f"Found: {curr_prev_hash}")
                return False, details
        
        details.append("All hash chain links verified successfully")
        return True, details
    
    def _calculate_merkle_root(self, events: List[Dict]) -> Optional[str]:
        """Calculate Merkle root for all events"""
        if not events:
            return None
        
        # Create hashes for all events
        hashes = []
        for event in events:
            event_str = json.dumps(event, sort_keys=True)
            hash_obj = hashlib.sha256(event_str.encode())
            hashes.append(hash_obj.hexdigest())
        
        # Build Merkle tree
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i + 1]
                else:
                    combined = hashes[i] + hashes[i]  # Duplicate last hash
                
                hash_obj = hashlib.sha256(combined.encode())
                new_hashes.append(hash_obj.hexdigest())
            
            hashes = new_hashes
        
        return hashes[0] if hashes else None
    
    def _verify_event_hash(self, event: Dict) -> bool:
        """Verify individual event hash"""
        event_data = event.copy()
        stored_hash = event_data.pop('hash', '')
        
        event_str = json.dumps(event_data, sort_keys=True)
        calculated_hash = hashlib.sha256(event_str.encode()).hexdigest()
        
        return stored_hash == calculated_hash
    
    def _generate_sample_audit_data(self) -> Dict:
        """Generate sample audit data for demonstration"""
        events = []
        base_time = datetime.now().timestamp()
        
        sample_events = [
            {
                "event_type": "CREATED",
                "case_id": "SAR-1042",
                "user": "analyst_1",
                "description": "Case created from transaction analysis"
            },
            {
                "event_type": "ANALYZED",
                "case_id": "SAR-1042", 
                "user": "system",
                "description": "AI analysis completed"
            },
            {
                "event_type": "ALERT_SENT",
                "case_id": "SAR-1042",
                "user": "system",
                "description": "High-risk alert sent to compliance team"
            },
            {
                "event_type": "MODIFIED",
                "case_id": "SAR-1042",
                "user": "supervisor_1",
                "description": "Case notes updated"
            }
        ]
        
        for i, event_data in enumerate(sample_events):
            timestamp = base_time + (i * 3600)  # 1 hour intervals
            event_data['timestamp'] = datetime.fromtimestamp(timestamp).isoformat()
            
            # Generate hash
            event_str = json.dumps(event_data, sort_keys=True)
            event_hash = hashlib.sha256(event_str.encode()).hexdigest()
            event_data['hash'] = event_hash
            
            if i > 0:
                event_data['previous_hash'] = events[-1]['hash']
            else:
                event_data['previous_hash'] = '0' * 64  # Genesis hash
            
            events.append(event_data)
        
        return {"events": events}
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp
    
    def export_audit_report(self, audit_data: Dict) -> str:
        """Export audit report as formatted text"""
        report = f"""
PROOFSAR AI - AUDIT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
Total Events: {len(audit_data.get('events', []))}
Hash Chain Valid: {self._verify_hash_chain(audit_data.get('events', []))[0]}
Merkle Root: {self._calculate_merkle_root(audit_data.get('events', []))}

DETAILED LOG
"""
        
        events = audit_data.get('events', [])
        for event in events:
            report += f"""
Timestamp: {self._format_timestamp(event['timestamp'])}
Event Type: {event['event_type']}
Case ID: {event.get('case_id', 'N/A')}
User: {event.get('user', 'system')}
Description: {event.get('description', '')}
Hash: {event.get('hash', '')}
{'-' * 50}
"""
        
        return report
