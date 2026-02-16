"""
Utility functions for ProofSAR AI frontend
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


def get_demo_data_safe() -> Optional[pd.DataFrame]:
    """
    Safely load demo data using Path-based approach
    Returns DataFrame or None if file not found/invalid
    """
    try:
        # Use Path for safe, cross-platform file handling
        demo_file = Path(__file__).parent.parent.parent / "demo_data" / "transactions.csv"
        
        if not demo_file.exists():
            logger.warning(f"Demo data file not found: {demo_file}")
            return None
            
        df = pd.read_csv(demo_file)
        logger.info(f"Loaded demo data: {len(df)} transactions")
        return df
        
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading demo data: {str(e)}")
        return None


def validate_csv_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, str]:
    """
    Validate that CSV has all required columns
    Returns: (is_valid, error_message)
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        error_msg = f"Missing columns: {', '.join(missing_columns)}"
        return False, error_msg
    
    return True, ""


def validate_csv_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate CSV data integrity
    Returns: (is_valid, error_message)
    """
    if df.empty:
        return False, "CSV file is empty"
    
    # Check for required data types
    try:
        pd.to_numeric(df['amount'], errors='raise')
        pd.to_datetime(df['date'], errors='raise')
    except (ValueError, KeyError) as e:
        return False, f"Data format error: {str(e)}"
    
    # Check for basic data issues
    if df.isnull().any().any():
        null_cols = df.columns[df.isnull().any()].tolist()
        return False, f"Null values found in: {', '.join(null_cols)}"
    
    return True, ""


def load_and_validate_csv(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load and validate uploaded CSV file
    Returns: (dataframe, error_message)
    If error_message is None, dataframe is valid
    """
    try:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        # Validate structure
        from config import REQUIRED_CSV_COLUMNS
        is_valid, error_msg = validate_csv_columns(df, REQUIRED_CSV_COLUMNS)
        if not is_valid:
            return None, error_msg
        
        # Validate data
        is_valid, error_msg = validate_csv_data(df)
        if not is_valid:
            return None, error_msg
        
        return df, None
        
    except pd.errors.ParserError as e:
        return None, f"Invalid CSV format: {str(e)}"
    except Exception as e:
        return None, f"File processing error: {str(e)}"


def format_currency(value: float, currency: str = "₹") -> str:
    """Format value as currency string"""
    return f"{currency}{value:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage string"""
    return f"{value*100:.{decimals}f}%"


def format_timestamp() -> str:
    """Get current timestamp string"""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


def show_loading_spinner(message: str):
    """Context manager for loading spinner"""
    import contextlib
    
    @contextlib.contextmanager
    def _spinner():
        with st.spinner(f"⏳ {message}"):
            yield
    
    return _spinner()


def setup_logging(name: str = "ProofSAR") -> logging.Logger:
    """Setup structured logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)


def safe_metric_display(label: str, value: any, delta: any = None, delta_color: str = "normal") -> None:
    """Safely display metrics with error handling"""
    try:
        st.metric(label, value, delta=delta, delta_color=delta_color)
    except Exception as e:
        logger.error(f"Error displaying metric {label}: {str(e)}")
        st.write(f"**{label}:** {value}")
