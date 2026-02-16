"""
Enterprise Loading Overlay for ProofSAR AI
Production-grade loading states and progress indicators
"""

import streamlit as st
import time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LoadingOverlay:
    """Enterprise-grade loading overlay component"""
    
    def __init__(self):
        self.loading_states = {}
    
    def show_loading_overlay(self, message: str = "Processing...", show_progress: bool = False) -> None:
        """Show loading overlay with optional progress"""
        overlay_html = f"""
        <div class="loading-overlay" id="loading-overlay">
            <div style="text-align: center;">
                <div class="loading-spinner"></div>
                <p style="margin-top: 20px; font-size: 18px; color: #333;">{message}</p>
            </div>
        </div>
        <script>
            // Show loading overlay
            document.getElementById('loading-overlay').style.display = 'flex';
        </script>
        """
        st.markdown(overlay_html, unsafe_allow_html=True)
    
    def hide_loading_overlay(self) -> None:
        """Hide loading overlay"""
        hide_script = """
        <script>
            var overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        </script>
        """
        st.markdown(hide_script, unsafe_allow_html=True)
    
    def show_progress_with_steps(self, steps: list, current_step: int = 0) -> None:
        """Show progress with step indicators"""
        progress_html = """
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        """
        
        for i, step in enumerate(steps):
            is_completed = i < current_step
            is_current = i == current_step
            
            status_color = "#28a745" if is_completed else "#007bff" if is_current else "#6c757d"
            status_icon = "✅" if is_completed else "🔄" if is_current else "⭕"
            
            progress_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="width: 30px; height: 30px; border-radius: 50%; background: {status_color}; 
                           display: flex; align-items: center; justify-content: center; 
                           color: white; font-weight: bold; margin-right: 15px;">
                    {status_icon}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: {'bold' if is_current else 'normal'}; color: {status_color};">
                        {step}
                    </div>
                </div>
            </div>
            """
        
        progress_html += "</div>"
        st.markdown(progress_html, unsafe_allow_html=True)
    
    def show_animated_progress(self, progress_value: int, message: str = "Processing...") -> None:
        """Show animated progress bar"""
        st.progress(progress_value)
        
        if progress_value < 100:
            # Show spinning indicator
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px;">
                <div style="display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; 
                           border-top: 3px solid #667eea; border-radius: 50%; 
                           animation: spin 1s linear infinite;"></div>
                <span style="margin-left: 10px; color: #666;">{message}</span>
            </div>
            """, unsafe_allow_html=True)

class ToastNotification:
    """Enterprise toast notification system"""
    
    def __init__(self):
        self.notifications = []
    
    def show_success(self, message: str, duration: int = 3000) -> None:
        """Show success toast"""
        self._show_toast(message, "success", duration)
    
    def show_error(self, message: str, duration: int = 5000) -> None:
        """Show error toast"""
        self._show_toast(message, "error", duration)
    
    def show_warning(self, message: str, duration: int = 4000) -> None:
        """Show warning toast"""
        self._show_toast(message, "warning", duration)
    
    def show_info(self, message: str, duration: int = 3000) -> None:
        """Show info toast"""
        self._show_toast(message, "info", duration)
    
    def _show_toast(self, message: str, toast_type: str, duration: int) -> None:
        """Show toast notification"""
        colors = {
            "success": "#28a745",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#007bff"
        }
        
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        color = colors.get(toast_type, "#007bff")
        icon = icons.get(toast_type, "ℹ️")
        
        toast_html = f"""
        <div id="toast-notification" style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border-left: 5px solid {color};
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            z-index: 10000;
            min-width: 300px;
            max-width: 400px;
            animation: slideInRight 0.3s ease-out;
        ">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 20px; margin-right: 10px;">{icon}</span>
                <span style="flex: 1; color: #333;">{message}</span>
            </div>
        </div>
        
        <script>
            // Auto-hide toast after duration
            setTimeout(function() {{
                var toast = document.getElementById('toast-notification');
                if (toast) {{
                    toast.style.animation = 'slideOutRight 0.3s ease-out';
                    setTimeout(function() {{
                        toast.remove();
                    }}, 300);
                }}
            }}, {duration});
        </script>
        
        <style>
            @keyframes slideInRight {{
                from {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}
            
            @keyframes slideOutRight {{
                from {{
                    transform: translateX(0);
                    opacity: 1;
                }}
                to {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
            }}
        </style>
        """
        
        st.markdown(toast_html, unsafe_allow_html=True)

# Global instances
loading_overlay = LoadingOverlay()
toast_notification = ToastNotification()

def get_loading_overlay() -> LoadingOverlay:
    """Get global loading overlay instance"""
    return loading_overlay

def get_toast_notification() -> ToastNotification:
    """Get global toast notification instance"""
    return toast_notification
