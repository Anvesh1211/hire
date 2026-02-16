@echo off
echo ========================================
echo 🛡️  ProofSAR AI - Starting Application
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ⚠️ Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created!
)

REM Activate venv
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check Python in venv
python --version
echo.

REM Install/Update requirements
echo 📦 Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ⚠️ Some packages may have failed to install
) else (
    echo ✅ Dependencies installed!
)
echo.

echo 🚀 Launching ProofSAR AI...
echo.
echo 📊 Dashboard will open at: http://localhost:8501
echo 🔐 Use Ctrl+C to stop the server
echo.
echo ========================================

REM Run Streamlit
cd frontend
streamlit run app.py

REM Keep window open on error
if errorlevel 1 pause