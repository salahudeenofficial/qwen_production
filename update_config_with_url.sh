#!/bin/bash
# Script to update config.yaml with ngrok URL
# Usage: ./update_config_with_url.sh https://your-ngrok-url.ngrok-free.app

if [ -z "$1" ]; then
    echo "Usage: ./update_config_with_url.sh https://your-ngrok-url.ngrok-free.app"
    exit 1
fi

NGROK_URL="$1"
CALLBACK_URL="${NGROK_URL}/v1/vton/result"
CONFIG_FILE="gpu-server-qwen/configs/config.yaml"

echo "=============================================================="
echo "Updating config.yaml with ngrok URL"
echo "=============================================================="
echo "Ngrok URL: $NGROK_URL"
echo "Callback URL: $CALLBACK_URL"
echo ""

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

# Backup
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✓ Config backed up"

# Update using Python
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
echo "Next steps:"
echo "1. Review the updated config: cat $CONFIG_FILE"
echo "2. Commit and push:"
echo "   git add $CONFIG_FILE"
echo "   git commit -m 'Update callback URL with ngrok'"
echo "   git push origin qwen_api"
echo "   git push production qwen_api:main"
echo "3. On Vast AI: git pull && restart server"
echo "=============================================================="

