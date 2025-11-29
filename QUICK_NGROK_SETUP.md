# Quick Ngrok Setup Guide

## Step 1: Authenticate Ngrok (One-time)

```bash
# Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## Step 2: Start Asset Service

```bash
python test_asset_service.py
```

Keep this running in one terminal.

## Step 3: Start Ngrok

In another terminal:
```bash
ngrok http 8001
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8001
```

## Step 4: Update Config Automatically

Once ngrok is running, use the helper script:
```bash
./update_ngrok_url.sh
```

This will:
- Get the ngrok URL automatically
- Update `gpu-server-qwen/configs/config.yaml` with the correct callback URL
- Create a backup of your config

## Step 5: Push and Deploy

```bash
git add gpu-server-qwen/configs/config.yaml
git commit -m "Update callback URL with ngrok"
git push origin qwen_api
git push production qwen_api:main
```

## Step 6: On Vast AI Server

```bash
# Pull the latest code
git pull origin qwen_api  # or git pull production main

# Edit config if needed (ngrok URL might have changed)
# Or use: ./update_ngrok_url.sh if running ngrok on Vast AI

# Restart server
python run_server.py
```

## Manual Update (Alternative)

If you prefer to update manually:

1. Get ngrok URL from ngrok output or:
   ```bash
   curl http://localhost:4040/api/tunnels | python3 -m json.tool
   ```

2. Edit `gpu-server-qwen/configs/config.yaml`:
   ```yaml
   asset_service:
     callback_url: "https://YOUR_NGROK_URL.ngrok-free.app/v1/vton/result"
   ```

## Testing

After updating and restarting:
```bash
python test_client.py http://108.231.141.46:17857
```

Check Asset Service terminal for callbacks!

