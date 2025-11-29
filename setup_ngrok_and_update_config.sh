#!/bin/bash
# Script to setup ngrok and update config.yaml automatically

set -e

echo "=============================================================="
echo "Ngrok Setup and Config Update Script"
echo "=============================================================="
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed"
    echo "Please install ngrok first:"
    echo "  snap install ngrok"
    echo "  or download from https://ngrok.com/download"
    exit 1
fi

echo "✓ ngrok is installed"

# Check if ngrok is authenticated
if ! ngrok config check &> /dev/null; then
    echo ""
    echo "⚠️  ngrok requires authentication"
    echo "Please run: ngrok config add-authtoken YOUR_AUTHTOKEN"
    echo "Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

echo "✓ ngrok is authenticated"

# Check if Asset Service is running
if ! curl -s http://localhost:8001/health &> /dev/null; then
    echo ""
    echo "⚠️  Asset Service is not running on port 8001"
    echo "Please start it first: python test_asset_service.py"
    exit 1
fi

echo "✓ Asset Service is running"

# Start ngrok in background
echo ""
echo "Starting ngrok tunnel..."
ngrok http 8001 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 5

# Get the ngrok URL
echo "Getting ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | \
    python3 -c "import sys, json; d=json.load(sys.stdin); urls=[t['public_url'] for t in d.get('tunnels',[]) if 'https' in t.get('public_url','')]; print(urls[0] if urls else '')" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    echo "Check ngrok output: cat /tmp/ngrok.log"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

echo "✓ Ngrok URL: $NGROK_URL"

# Update config.yaml
CONFIG_FILE="gpu-server-qwen/configs/config.yaml"
CALLBACK_URL="${NGROK_URL}/v1/vton/result"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

# Backup config
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"

# Update callback URL using sed
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|callback_url:.*|callback_url: \"${CALLBACK_URL}\"|" "$CONFIG_FILE"
else
    # Linux
    sed -i "s|callback_url:.*|callback_url: \"${CALLBACK_URL}\"|" "$CONFIG_FILE"
fi

echo ""
echo "=============================================================="
echo "✅ Config updated successfully!"
echo "=============================================================="
echo "Ngrok URL: $NGROK_URL"
echo "Callback URL: $CALLBACK_URL"
echo "Config file: $CONFIG_FILE"
echo ""
echo "Ngrok is running in background (PID: $NGROK_PID)"
echo "To stop ngrok: kill $NGROK_PID"
echo ""
echo "⚠️  IMPORTANT: Update config.yaml on your Vast AI server with:"
echo "   callback_url: \"${CALLBACK_URL}\""
echo ""
echo "Then restart the GPU server on Vast AI."
echo "=============================================================="

