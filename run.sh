#!/bin/bash

echo "🛡️  ProofSAR AI - Starting Application..."
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Install requirements if needed
if [ ! -d "venv" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt --quiet
    echo "✅ Dependencies installed!"
    echo ""
fi

echo "🚀 Launching ProofSAR AI..."
echo ""
echo "📊 Dashboard will open at: http://localhost:8501"
echo "🔐 Use Ctrl+C to stop the server"
echo ""
echo "========================================"

# Run Streamlit
cd frontend
streamlit run app.py