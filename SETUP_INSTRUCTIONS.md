# Setup Instructions for Testing

## Current Status
- ✅ GPU Server: http://108.231.141.46:17857 (running on Vast AI)
- ✅ Asset Service: localhost:8001 (running locally)
- ⚠️  Need: Ngrok tunnel to connect them

## Quick Setup Steps

### 1. Start Ngrok (In a Terminal)

```bash
ngrok http 8001
```

**Keep this terminal open!** You'll see:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8001
```

### 2. Get Ngrok URL

**Option A: From ngrok output**
- Copy the HTTPS URL from the "Forwarding" line

**Option B: Use helper script** (in another terminal)
```bash
./get_ngrok_url.sh
```

### 3. Update Config

Edit `gpu-server-qwen/configs/config.yaml`:
```yaml
asset_service:
  callback_url: "https://YOUR_NGROK_URL.ngrok-free.app/v1/vton/result"
```

### 4. Push to GitHub

```bash
git add gpu-server-qwen/configs/config.yaml
git commit -m "Update callback URL with ngrok"
git push origin qwen_api
git push production qwen_api:main
```

### 5. On Vast AI Server

```bash
cd /workspace/qwen_production
git pull origin main
cd gpu-server-qwen
# Edit config.yaml if ngrok URL changed
python run_server.py
```

### 6. Test

```bash
python test_client.py http://108.231.141.46:17857
```

## Important Notes

- **Keep ngrok running** while testing
- **Ngrok free URLs change** each time you restart ngrok
- **Update config on Vast AI** if ngrok URL changes
- **Restart GPU server** after config changes

## Troubleshooting

- **No callbacks**: Check ngrok is running and URL is correct in config
- **Config not updated**: Make sure you pulled latest code on Vast AI
- **Ngrok not working**: Verify authentication: `ngrok config check`

