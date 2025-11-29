# Next Steps for Testing

## Current Status
- ✅ GPU Server running on: http://108.231.141.46:17857
- ✅ Asset Service running on: localhost:8001
- ⚠️  Ngrok needs authentication and setup

## What You Need to Do

### 1. Authenticate Ngrok
```bash
# Get authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### 2. Start Ngrok Tunnel
```bash
ngrok http 8001
```

### 3. Update Config with Ngrok URL

**Option A: Automatic (Recommended)**
```bash
./update_ngrok_url.sh
```

**Option B: Manual**
1. Get URL from ngrok output: `https://abc123.ngrok-free.app`
2. Edit `gpu-server-qwen/configs/config.yaml`:
   ```yaml
   asset_service:
     callback_url: "https://abc123.ngrok-free.app/v1/vton/result"
   ```

### 4. Push Updated Config
```bash
git add gpu-server-qwen/configs/config.yaml
git commit -m "Update callback URL with ngrok"
git push origin qwen_api
git push production qwen_api:main
```

### 5. On Vast AI Server
```bash
# Pull latest code
cd /workspace/qwen_production
git pull origin main  # or git pull production main

# Edit config.yaml with the ngrok URL
nano gpu-server-qwen/configs/config.yaml
# Update callback_url with your ngrok URL

# Restart server
cd gpu-server-qwen
python run_server.py
```

### 6. Test End-to-End
```bash
# On your local machine
python test_client.py http://108.231.141.46:17857
```

## Expected Flow

1. Test client sends request → GPU server (108.231.141.46:17857)
2. GPU server accepts (202) → Test client
3. GPU server processes inference → Background
4. GPU server sends callback → Ngrok → Asset Service (localhost:8001)
5. Asset Service receives and displays → Console + saves image

## Troubleshooting

- **No callbacks received**: Check ngrok URL is correct in config
- **Ngrok not working**: Verify authentication and tunnel is running
- **Config not updated**: Make sure you pulled latest code on Vast AI
- **Server not starting**: Check config.yaml syntax is valid YAML

