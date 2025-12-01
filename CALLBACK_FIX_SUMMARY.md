# Callback Connection Fix Summary

## Issue
The GPU server was getting HTTP 502 errors when trying to send callbacks via ngrok. The error indicated:
- Ngrok was receiving the request
- But ngrok couldn't connect to `localhost:8001` (ERR_NGROK_8012)

## Root Cause
The Asset Service was not running or not accessible when ngrok tried to forward requests.

## Solution
1. ✅ **Asset Service** - Now running on port 8001, listening on `0.0.0.0:8001`
2. ✅ **Ngrok** - Restarted and configured to forward to `localhost:8001`
3. ✅ **Connection Test** - Verified Asset Service is accessible locally

## Current Status

### Asset Service
- **Status**: Running
- **Port**: 8001
- **Host**: 0.0.0.0 (accessible from localhost)
- **Health Check**: `http://localhost:8001/health`

### Ngrok
- **Status**: Running
- **Forwarding**: `https://[ngrok-url].ngrok-free.dev` → `localhost:8001`
- **API**: `http://localhost:4040/api/tunnels`

### GPU Server Config
- **Callback URL**: `https://[ngrok-url].ngrok-free.dev/v1/vton/result`
- **Auth Token**: `TEST_GPU_TO_ASSET_SECRET`

## Testing

To test the callback connection:

```bash
# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; d=json.load(sys.stdin); urls=[t['public_url'] for t in d.get('tunnels',[]) if 'https' in t.get('public_url','')]; print(urls[0] if urls else '')")

# Test callback
curl -X POST "$NGROK_URL/v1/vton/result" \
  -H "X-Internal-Auth: TEST_GPU_TO_ASSET_SECRET" \
  -F "job_id=test_123" \
  -F "user_id=test" \
  -F "session_id=test" \
  -F "status=SUCCESS"
```

## Next Steps

1. **Verify ngrok URL** - Make sure the GPU server's `config.yaml` has the correct callback URL
2. **Send test request** - Use `test_client.py` to send a request to the GPU server
3. **Monitor callbacks** - Check Asset Service logs and `asset_service_output/` directory

## Important Notes

- **Ngrok free URLs change** when you restart ngrok
- If you restart ngrok, update the callback URL in the GPU server config
- Keep both Asset Service and ngrok running while testing
- Asset Service must be accessible on `localhost:8001` for ngrok to work

