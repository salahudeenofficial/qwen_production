# Simple Workflow - Just Follow These Steps

## Current Situation
- ✅ GPU Server running on: http://108.231.141.46:17857
- ✅ Asset Service running on: localhost:8001
- ⚠️  Ngrok needs proper authentication

## Step-by-Step Instructions

### 1. Fix Ngrok Authentication

Your ngrok config has a placeholder. Fix it:

```bash
# Get your real authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_REAL_AUTHTOKEN
```

**Important**: Replace `YOUR_REAL_AUTHTOKEN` with the actual token from ngrok dashboard.

### 2. Start Ngrok

```bash
ngrok http 8001
```

**Keep this terminal open!** You'll see:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8001
```

### 3. Get the Ngrok URL

**Option A: From ngrok output**
- Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

**Option B: Use helper script** (in another terminal)
```bash
./get_ngrok_url.sh
```

### 4. Update Config

**Option A: Automatic** (recommended)
```bash
./update_config_with_url.sh https://your-ngrok-url.ngrok-free.app
```

**Option B: Manual**
Edit `gpu-server-qwen/configs/config.yaml`:
```yaml
asset_service:
  callback_url: "https://your-ngrok-url.ngrok-free.app/v1/vton/result"
```

### 5. Push to GitHub

```bash
git add gpu-server-qwen/configs/config.yaml
git commit -m "Update callback URL with ngrok"
git push origin qwen_api
git push production qwen_api:main
```

### 6. On Vast AI Server

```bash
cd /workspace/qwen_production
git pull origin main
cd gpu-server-qwen
python run_server.py
```

### 7. Test

```bash
python test_client.py http://108.231.141.46:17857
```

Check Asset Service terminal for callbacks!

## Quick Reference

- **Get ngrok URL**: `./get_ngrok_url.sh`
- **Update config**: `./update_config_with_url.sh https://your-url.ngrok-free.app`
- **Test server**: `python test_client.py http://108.231.141.46:17857`

