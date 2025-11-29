# Manual Ngrok Setup (Quick Guide)

Since ngrok requires manual authentication and startup, follow these steps:

## Step 1: Start Ngrok Manually

Open a terminal and run:
```bash
ngrok http 8001
```

You'll see output like:
```
Session Status                online
Account                       Your Name (Plan: Free)
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8001
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

## Step 2: Update Config

**Option A: Use the helper script**
```bash
./get_ngrok_url.sh
```
This will display the ngrok URL and callback URL to use.

**Option B: Manual update**

Edit `gpu-server-qwen/configs/config.yaml`:
```yaml
asset_service:
  callback_url: "https://YOUR_NGROK_URL.ngrok-free.app/v1/vton/result"
```

Replace `YOUR_NGROK_URL` with the actual ngrok URL from step 1.

## Step 3: Push Changes

```bash
git add gpu-server-qwen/configs/config.yaml
git commit -m "Update callback URL with ngrok"
git push origin qwen_api
git push production qwen_api:main
```

## Step 4: On Vast AI Server

```bash
# Pull latest code
cd /workspace/qwen_production
git pull origin main

# Verify config has correct ngrok URL
cat gpu-server-qwen/configs/config.yaml | grep callback_url

# Start server
cd gpu-server-qwen
python run_server.py
```

## Step 5: Test

```bash
python test_client.py http://108.231.141.46:17857
```

Check Asset Service terminal for callbacks!

