#!/bin/bash
# Script to automatically get ngrok URL and update config.yaml

set -e

CONFIG_FILE="gpu-server-qwen/configs/config.yaml"

echo "=============================================================="
echo "Updating ngrok URL in config.yaml"
echo "=============================================================="

# Check if ngrok is running
if ! curl -s http://localhost:4040/api/tunnels &> /dev/null; then
    echo "❌ Ngrok is not running or not accessible"
    echo "Please start ngrok first: ngrok http 8001"
    exit 1
fi

# Get ngrok URL
echo "Getting ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | \
    python3 -c "import sys, json; d=json.load(sys.stdin); urls=[t['public_url'] for t in d.get('tunnels',[]) if 'https' in t.get('public_url','')]; print(urls[0] if urls else '')" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    echo "Make sure ngrok is running: ngrok http 8001"
    exit 1
fi

CALLBACK_URL="${NGROK_URL}/v1/vton/result"

echo "✓ Ngrok URL found: $NGROK_URL"
echo "✓ Callback URL: $CALLBACK_URL"

# Backup config
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✓ Config backed up"
fi

# Update config using Python for better YAML handling
python3 << EOF
import yaml
import sys

config_file = "$CONFIG_FILE"

try:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    config['asset_service']['callback_url'] = "$CALLBACK_URL"
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ Config updated successfully!")
    print(f"   Callback URL: $CALLBACK_URL")
    
except Exception as e:
    print(f"❌ Error updating config: {e}")
    sys.exit(1)
EOF

echo ""
echo "=============================================================="
echo "✅ Done! Config file updated."
echo "=============================================================="
echo "Next steps:"
echo "1. Pull this updated config on your Vast AI server"
echo "2. Restart the GPU server"
echo "3. Run test_client.py to verify callbacks"
echo "=============================================================="

