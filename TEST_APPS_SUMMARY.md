# Test Applications Summary

## Created Files

### 1. `test_client.py`
**Purpose**: Sends requests to GPU server and tests all endpoints

**Features**:
- Tests `/health`, `/version`, `/metrics`, `/gpu/status`
- Tests `/tryon` endpoint with images
- Tests authentication (401 on missing auth)
- Tests GPU busy state (429 response)
- Uses images from `input/masked_person.png` and `input/cloth.png`
- Configurable server URL (command line argument)

**Usage**:
```bash
python test_client.py http://YOUR_VAST_AI_IP:8000
```

### 2. `test_asset_service.py`
**Purpose**: Mock Asset Service to receive callbacks from GPU server

**Features**:
- Receives callbacks at `/v1/vton/result`
- Validates `X-Internal-Auth` header
- Saves received images to `asset_service_output/`
- Displays callback data in console
- Stores all callbacks for inspection
- Additional endpoints: `/callbacks`, `/health`

**Usage**:
```bash
python test_asset_service.py
```

Runs on port 8001 by default.

### 3. Updated `gpu-server-qwen/configs/config.yaml`
- Set test auth tokens:
  - `TEST_BRIDGE_TO_GPU_SECRET` (for CPU Bridge → GPU Server)
  - `TEST_GPU_TO_ASSET_SECRET` (for GPU Server → Asset Service)
- Set callback URL to `http://localhost:8001/v1/vton/result` (update for Vast AI)

## Test Authentication Tokens

**Current test tokens** (configured in all three places):
- GPU Server accepts: `TEST_BRIDGE_TO_GPU_SECRET`
- Asset Service accepts: `TEST_GPU_TO_ASSET_SECRET`

**⚠️ Important**: These are for testing only. Change for production!

## Key Points to Handle Outside Test Apps

### 1. **Network Configuration** ⚠️ CRITICAL

**If GPU server and Asset Service on different machines:**
- Update `gpu-server-qwen/configs/config.yaml`:
  ```yaml
  asset_service:
    callback_url: "http://YOUR_ASSET_SERVICE_IP:8001/v1/vton/result"
  ```
- GPU server must be able to reach Asset Service
- Check firewall rules
- Use public IP or domain if services are remote

**If both on same Vast AI instance:**
- Use `localhost` or internal IP
- Both services can share same network

### 2. **Port Access** ⚠️ IMPORTANT

- **GPU Server**: Port 8000
- **Asset Service**: Port 8001

**On Vast AI:**
- Ensure ports are exposed/forwarded
- Check Vast AI port configuration
- May need to configure firewall rules

### 3. **Model Files** ⚠️ REQUIRED

GPU server needs models in these directories:
- `gpu-server-qwen/models/checkpoints/` - UNET model
- `gpu-server-qwen/models/clip/` - CLIP model  
- `gpu-server-qwen/models/vae/` - VAE model
- `gpu-server-qwen/models/loras/` - LoRA model

**Server will reject traffic until models are loaded!**

### 4. **Image Files** ✅ READY

Test images are already in place:
- `input/masked_person.png` ✅
- `input/cloth.png` ✅

### 5. **GPU Availability** ⚠️ REQUIRED

- Server needs GPU access (CUDA)
- Check with: `nvidia-smi` on Vast AI instance
- Server will work on CPU but very slow (not recommended)

### 6. **Callback URL Configuration** ⚠️ CRITICAL

**Before testing, update callback URL:**

If Asset Service on same machine as GPU server:
```yaml
asset_service:
  callback_url: "http://localhost:8001/v1/vton/result"
```

If Asset Service on different machine:
```yaml
asset_service:
  callback_url: "http://ASSET_SERVICE_IP:8001/v1/vton/result"
```

If Asset Service on your local machine (GPU server on Vast AI):
- Use ngrok or similar tunnel
- Or use Vast AI's public IP if accessible
- Update callback URL accordingly

### 7. **Service Startup Order**

1. **First**: Start Asset Service (test_asset_service.py)
2. **Second**: Start GPU Server (app.main:app)
3. **Third**: Run Test Client (test_client.py)

### 8. **Logging and Monitoring**

**GPU Server:**
- Logs in JSON format to stdout
- All events include `node_id`
- Check logs for: request_received, inference_started, callback_sent_asset, etc.

**Asset Service:**
- Logs callback receipts
- Saves images to `asset_service_output/`
- Stores callback history

### 9. **Error Scenarios to Test**

1. **Invalid Auth**: Remove `X-Internal-Auth` header → Should get 401
2. **GPU Busy**: Send 2 requests quickly → Second should get 429
3. **Invalid Images**: Send corrupted files → Should send error callback
4. **Network Failure**: Stop Asset Service → GPU server should retry
5. **Missing Fields**: Send incomplete request → Should get 400

### 10. **Production Considerations**

Before production deployment:
- [ ] Change auth tokens to secure random values
- [ ] Configure TLS/SSL for all endpoints
- [ ] Set up proper logging aggregation
- [ ] Configure monitoring and alerting
- [ ] Test all error scenarios
- [ ] Load testing
- [ ] Security review
- [ ] Update callback URL to production Asset Service

## Testing Workflow

1. **Start Asset Service**:
   ```bash
   python test_asset_service.py
   ```

2. **Update GPU Server Config** (if needed):
   ```bash
   # Edit gpu-server-qwen/configs/config.yaml
   # Update callback_url if Asset Service on different machine
   ```

3. **Start GPU Server**:
   ```bash
   cd gpu-server-qwen
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Wait for Models to Load**:
   - Check server logs
   - Server will reject traffic until ready
   - Look for "✓ Server ready to accept requests!"

5. **Run Test Client**:
   ```bash
   python test_client.py http://YOUR_VAST_AI_IP:8000
   ```

6. **Verify Results**:
   - Test client shows 202 Accepted
   - Asset Service receives callback
   - Image saved to `asset_service_output/`

## Quick Verification Checklist

- [ ] Test images exist (`input/masked_person.png`, `input/cloth.png`)
- [ ] GPU server config updated with correct callback URL
- [ ] Auth tokens match in all three places
- [ ] Ports 8000 and 8001 accessible
- [ ] Models loaded in GPU server
- [ ] Asset Service running and accessible
- [ ] Network connectivity verified

## Troubleshooting

See `TESTING_GUIDE.md` for detailed troubleshooting steps.

## Next Steps

1. Clone repo to Vast AI instance
2. Set up GPU server
3. Update callback URL in config
4. Start Asset Service (on your machine or Vast AI)
5. Run test client
6. Verify end-to-end flow

