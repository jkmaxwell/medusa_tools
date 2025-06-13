#!/bin/bash

echo "🌐 Starting Medusa Wavetable Utility Web Interface..."
echo ""

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask not found. Installing web dependencies..."
    pip install -r requirements_web.txt
fi

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg not found. Audio conversion may not work."
    echo "   Install FFmpeg with: brew install ffmpeg"
    echo ""
fi

echo "🚀 Starting development server..."
echo "📱 Open your browser to: http://localhost:5001"
echo "🛑 Press Ctrl+C to stop the server"
echo ""
echo "💡 Note: Using port 5001 to avoid macOS AirPlay conflict"
echo ""

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run the web app
python web_app.py 