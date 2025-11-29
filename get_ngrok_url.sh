#!/bin/bash
# Simple script to get ngrok URL and display it

echo "Getting ngrok URL..."
sleep 2

NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | \
    python3 -c "import sys, json; d=json.load(sys.stdin); urls=[t['public_url'] for t in d.get('tunnels',[]) if 'https' in t.get('public_url','')]; print(urls[0] if urls else '')" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Ngrok is not running or not accessible"
    echo "Please start ngrok first: ngrok http 8001"
    exit 1
fi

CALLBACK_URL="${NGROK_URL}/v1/vton/result"

echo "=============================================================="
echo "✅ Ngrok URL found!"
echo "=============================================================="
echo "Ngrok URL: $NGROK_URL"
echo "Callback URL: $CALLBACK_URL"
echo ""
echo "Update gpu-server-qwen/configs/config.yaml with:"
echo "  callback_url: \"$CALLBACK_URL\""
echo "=============================================================="

