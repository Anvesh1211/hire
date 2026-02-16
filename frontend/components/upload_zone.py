"""
Enterprise Upload Component for ProofSAR AI
Production-safe CSV upload with validation and error handling
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import logging
from typing import Optional, Tuple, Dict, Any
import io
from datetime import datetime

logger = logging.getLogger(__name__)

class EnterpriseUploadZone:
    """Enterprise-grade file upload component with validation"""
    
    def __init__(self):
        self.required_columns = {
            'transaction_id': 'str',
            'account_id': 'str', 
            'amount': 'float64',
            'timestamp': 'datetime64[ns]'
        }
        
        self.optional_columns = {
            'transaction_type': 'str',
            'source': 'str',
            'destination': 'str',
            'description': 'str'
        }
    
    def render_upload_interface(self) -> Optional[pd.DataFrame]:
        """Render the complete upload interface with validation"""
        st.markdown("### 📤 Upload Transaction Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Drop CSV file here or click to browse",
                type=['csv'],
                help="Upload a CSV file containing transaction data",
                key="csv_uploader"
            )
            
            # Action buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📁 Use Demo Data", use_container_width=True, type="secondary"):
                    demo_df = self._load_demo_data()
                    if demo_df is not None:
                        st.session_state.uploaded_df = demo_df
                        st.success("✅ Demo data loaded successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Demo data not available")
            
            with col_b:
                if st.button("🔄 Clear Data", use_container_width=True):
                    st.session_state.uploaded_df = None
                    st.session_state.upload_validation = None
                    st.rerun()
        
        with col2:
            self._render_requirements_info()
        
        # Handle uploaded file
        if uploaded_file is not None:
            return self._process_uploaded_file(uploaded_file)
        
        # Check for existing data in session state
        if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
            return st.session_state.uploaded_df
        
        return None
    
    def _process_uploaded_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """Process and validate uploaded file"""
        with st.spinner("🔍 Validating file..."):
            try:
                # Read CSV with error handling
                df = pd.read_csv(uploaded_file)
                
                # Validate file structure
                validation_result = self._validate_csv_structure(df)
                
                if validation_result['is_valid']:
                    # Store in session state
                    st.session_state.uploaded_df = df
                    st.session_state.upload_validation = validation_result
                    
                    st.success(f"✅ File validated successfully! Found {len(df)} transactions.")
                    return df
                else:
                    # Display validation errors
                    st.error("❌ File validation failed:")
                    for error in validation_result['errors']:
                        st.error(f"• {error}")
                    return None
                    
            except pd.errors.EmptyDataError:
                st.error("❌ The uploaded file is empty.")
                return None
            except pd.errors.ParserError:
                st.error("❌ Invalid CSV format. Please check the file structure.")
                return None
            except Exception as e:
                logger.error(f"Error processing uploaded file: {str(e)}")
                st.error(f"❌ Error processing file: {str(e)}")
                return None
    
    def _validate_csv_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate CSV structure and content"""
        errors = []
        warnings = []
        
        # Check if dataframe is empty
        if df.empty:
            errors.append("File contains no data")
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check required columns
        missing_columns = set(self.required_columns.keys()) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate data types and content
        for col, expected_type in self.required_columns.items():
            if col in df.columns:
                try:
                    if expected_type == 'datetime64[ns]':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        if df[col].isna().any():
                            errors.append(f"Column '{col}' contains invalid date values")
                    elif expected_type == 'float64':
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        if df[col].isna().any():
                            warnings.append(f"Column '{col}' contains non-numeric values")
                    elif expected_type == 'str':
                        df[col] = df[col].astype(str)
                        if df[col].isna().any():
                            warnings.append(f"Column '{col}' contains missing values")
                except Exception as e:
                    errors.append(f"Column '{col}' validation failed: {str(e)}")
        
        # Check for duplicate transaction IDs
        if 'transaction_id' in df.columns:
            duplicates = df['transaction_id'].duplicated().sum()
            if duplicates > 0:
                warnings.append(f"Found {duplicates} duplicate transaction IDs")
        
        # Check for negative amounts
        if 'amount' in df.columns:
            negative_amounts = (df['amount'] < 0).sum()
            if negative_amounts > 0:
                warnings.append(f"Found {negative_amounts} transactions with negative amounts")
        
        # Validate date ranges
        if 'timestamp' in df.columns:
            min_date = df['timestamp'].min()
            max_date = df['timestamp'].max()
            if min_date > datetime.now():
                warnings.append("Some transactions have future dates")
            if (max_date - min_date).days > 365:
                warnings.append("Transaction data spans more than 1 year")
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'row_count': len(df),
            'column_count': len(df.columns),
            'date_range': (min_date, max_date) if 'timestamp' in df.columns else None
        }
    
    def _render_requirements_info(self) -> None:
        """Render file requirements information"""
        st.markdown("""
        <div class="info-box">
            <strong>📋 Required Columns:</strong><br>
            • transaction_id (unique identifier)<br>
            • account_id (account number)<br>
            • amount (transaction amount)<br>
            • timestamp (date and time)<br><br>
            
            <strong>📝 Optional Columns:</strong><br>
            • transaction_type<br>
            • source<br>
            • destination<br>
            • description<br><br>
            
            <strong>📏 File Format:</strong><br>
            • CSV format only<br>
            • Max 10MB file size<br>
            • UTF-8 encoding
        </div>
        """, unsafe_allow_html=True)
    
    def _load_demo_data(self) -> Optional[pd.DataFrame]:
        """Load demo data safely using pathlib"""
        try:
            # Use pathlib for safe file path handling
            demo_path = Path(__file__).parent.parent.parent / "demo_data" / "transactions.csv"
            
            if demo_path.exists():
                df = pd.read_csv(demo_path)
                # Ensure required columns exist
                if all(col in df.columns for col in self.required_columns.keys()):
                    return df
                else:
                    logger.warning(f"Demo data missing required columns: {demo_path}")
                    return None
            else:
                logger.warning(f"Demo data file not found: {demo_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading demo data: {str(e)}")
            return None
    
    def render_data_overview(self, df: pd.DataFrame) -> None:
        """Render data overview and statistics"""
        if df is None:
            return
        
        st.markdown("### 📋 Transaction Overview")
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Transactions", len(df))
        
        with col2:
            if 'amount' in df.columns:
                total_amount = df['amount'].sum()
                st.metric("💰 Total Amount", f"₹{total_amount:,.0f}")
        
        with col3:
            if 'timestamp' in df.columns:
                date_range = (pd.to_datetime(df['timestamp'].max()) - pd.to_datetime(df['timestamp'].min())).days
                st.metric("📅 Date Range", f"{date_range} days")
        
        with col4:
            if 'account_id' in df.columns:
                unique_accounts = df['account_id'].nunique()
                st.metric("🏦 Accounts", unique_accounts)
    
    def render_data_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Render interactive data filters"""
        if df is None:
            return df
        
        st.markdown("#### 🔍 Filter Transactions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'amount' in df.columns:
                min_amount = st.number_input(
                    "Min Amount", 
                    value=float(df['amount'].min()), 
                    min_value=float(df['amount'].min()),
                    max_value=float(df['amount'].max()),
                    step=1000.0
                )
            else:
                min_amount = 0
        
        with col2:
            if 'amount' in df.columns:
                max_amount = st.number_input(
                    "Max Amount", 
                    value=float(df['amount'].max()), 
                    min_value=float(df['amount'].min()),
                    max_value=float(df['amount'].max()),
                    step=1000.0
                )
            else:
                max_amount = float('inf')
        
        with col3:
            if 'transaction_type' in df.columns:
                txn_types = df['transaction_type'].unique()
                selected_types = st.multiselect(
                    "Transaction Type", 
                    txn_types, 
                    default=list(txn_types)
                )
            else:
                selected_types = None
        
        # Apply filters
        filtered_df = df.copy()
        
        if 'amount' in df.columns:
            filtered_df = filtered_df[
                (filtered_df['amount'] >= min_amount) & 
                (filtered_df['amount'] <= max_amount)
            ]
        
        if selected_types and 'transaction_type' in df.columns:
            filtered_df = filtered_df[filtered_df['transaction_type'].isin(selected_types)]
        
        return filtered_df
    
    def get_validation_summary(self) -> Optional[Dict[str, Any]]:
        """Get validation summary from session state"""
        return st.session_state.get('upload_validation', None)
