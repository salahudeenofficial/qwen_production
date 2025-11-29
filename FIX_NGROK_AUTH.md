# Fix Ngrok Authentication

## The Issue
Your ngrok config file has a placeholder token. You need to replace it with your actual authtoken.

## Solution

### Step 1: Get Your Real Authtoken
1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Sign in to your ngrok account
3. Copy your authtoken (it looks like: `2abc123def456ghi789jkl012mno345pq_6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f`)

### Step 2: Update Ngrok Config
```bash
ngrok config add-authtoken YOUR_REAL_AUTHTOKEN_HERE
```

Replace `YOUR_REAL_AUTHTOKEN_HERE` with the actual token from step 1.

### Step 3: Verify
```bash
ngrok config check
```

Should show: "Valid configuration file"

### Step 4: Start Ngrok
```bash
ngrok http 8001
```

You should see:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8001
```

### Step 5: Get the URL
In another terminal:
```bash
./get_ngrok_url.sh
```

Or manually copy the URL from ngrok output.

### Step 6: Update Config
Edit `gpu-server-qwen/configs/config.yaml`:
```yaml
asset_service:
  callback_url: "https://YOUR_ACTUAL_NGROK_URL.ngrok-free.app/v1/vton/result"
```

### Step 7: Push and Deploy
```bash
git add gpu-server-qwen/configs/config.yaml
git commit -m "Update callback URL with ngrok"
git push origin qwen_api
git push production qwen_api:main
```

