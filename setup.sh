#!/bin/bash

echo "🚀 Video Transcript App Setup"
echo "=============================="

# Check Python version
echo "✔️ Checking Python version..."
python3 --version

# Create virtual environment
echo "✔️ Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✔️ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✔️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "✔️ Installing Python dependencies..."
pip install -r requirements.txt

# Check if ffmpeg is installed
echo "✔️ Checking ffmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ ffmpeg not found. Installing..."

    # Check OS and install ffmpeg
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ Homebrew not found. Please install ffmpeg manually:"
            echo "   Visit: https://ffmpeg.org/download.html"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y ffmpeg
    else
        echo "❌ Please install ffmpeg manually for your OS"
        echo "   Visit: https://ffmpeg.org/download.html"
    fi
else
    echo "✅ ffmpeg is already installed"
fi

# Create cache directory
echo "✔️ Creating cache directory..."
mkdir -p cache

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 To start the server:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run server: python server.py"
echo ""
echo "🌐 Then open index.html in your browser"