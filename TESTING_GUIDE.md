# Testing Guide for Qwen GPU Server

## Overview

This guide explains how to test the GPU server using the two test applications:
1. **test_client.py** - Sends requests to GPU server
2. **test_asset_service.py** - Receives callbacks from GPU server

## Prerequisites

1. GPU server running on Vast AI instance
2. Test images in `input/` folder:
   - `masked_person.png`
   - `cloth.png`
3. Both test applications configured with correct URLs

## Setup Instructions

### 1. Configure GPU Server

Edit `gpu-server-qwen/configs/config.yaml`:

```yaml
asset_service:
  # Update with your Vast AI instance URL where Asset Service is running
  callback_url: "http://YOUR_VAST_AI_IP:8001/v1/vton/result"
  internal_auth_token: "TEST_GPU_TO_ASSET_SECRET"
```

### 2. Start Asset Service (Mock)

On your local machine or Vast AI instance:

```bash
python test_asset_service.py
```

The Asset Service will run on port 8001 and wait for callbacks.

**Important**: If running on Vast AI, make sure port 8001 is exposed/accessible.

### 3. Update Test Client

Edit `test_client.py`:

```python
GPU_SERVER_URL = "http://YOUR_VAST_AI_IP:8000"  # Your GPU server URL
```

Or pass URL as command line argument:

```bash
python test_client.py http://YOUR_VAST_AI_IP:8000
```

### 4. Run Test Client

```bash
python test_client.py
```

## Test Scenarios

### ✅ Basic Endpoints

The test client automatically tests:
- `/health` - Health check
- `/version` - Version information
- `/metrics` - Prometheus metrics
- `/gpu/status` - GPU status (requires auth)

### ✅ Tryon Endpoint

Tests the main `/tryon` endpoint:
- Sends multipart form-data with images
- Includes `X-Internal-Auth` header
- Expects 202 Accepted response
- Verifies job is accepted

### ✅ GPU Busy State

Tests 429 response when GPU is busy:
- Sends two requests quickly
- Second request should get 429 if GPU is processing first

### ✅ Authentication

Tests unauthorized access:
- Request without `X-Internal-Auth` header
- Should return 401 Unauthorized

### ✅ Callback Flow

1. Test client sends request → GPU server
2. GPU server accepts (202) → Test client
3. GPU server processes inference → Background
4. GPU server sends callback → Asset Service
5. Asset Service receives and displays → Console + saves image

## Expected Behavior

### Test Client Output

```
============================================================
Testing /tryon endpoint (Job ID: test_job_abc123)
============================================================
Sending request to http://YOUR_VAST_AI_IP:8000/tryon
Job ID: test_job_abc123
Headers: X-Internal-Auth: TEST_BRIDGE_TO_GPU_...

Status: 202
Response Headers:
  X-Node-Id: qwen-gpu-1
Response: {
  "job_id": "test_job_abc123",
  "status": "ACCEPTED",
  "node_id": "qwen-gpu-1"
}
✅ Job accepted! Processing asynchronously...
⚠️  Note: Result will be sent to Asset Service via callback.
   Check the Asset Service logs to see the result.
```

### Asset Service Output

```
============================================================
📥 CALLBACK RECEIVED FROM GPU SERVER
============================================================
{
  "timestamp": "2024-11-29T23:30:00.123456",
  "job_id": "test_job_abc123",
  "user_id": "test_user_123",
  "session_id": "test_session_456",
  "provider": "qwen",
  "node_id": "qwen-gpu-1",
  "model_version": "1.0.0",
  "inference_time_ms": 1234.56,
  "error": null,
  "meta": null,
  "image_path": "asset_service_output/test_job_abc123_20241129_233000.png",
  "image_size": 1234567
}
============================================================
✅ Success callback for job test_job_abc123
   Inference time: 1234.56ms
   Image saved: asset_service_output/test_job_abc123_20241129_233000.png
```

## Key Points to Verify

### ✅ Specification Compliance

1. **Immediate Response (202)**
   - GPU server responds immediately with 202
   - Never waits for inference to complete

2. **Busy State (429)**
   - When GPU is processing, returns 429
   - Includes `Retry-After` header
   - Includes `X-Node-Id` header

3. **Authentication**
   - All requests require `X-Internal-Auth` header
   - Missing/invalid auth returns 401

4. **No Images in HTTP Response**
   - `/tryon` never returns images
   - Images only sent via callback to Asset Service

5. **Callback to Asset Service**
   - Callback sent after inference completes
   - Includes all required fields
   - Retries on failure (check logs)

6. **Structured JSON Logging**
   - GPU server logs in JSON format
   - All log events include `node_id`
   - Check GPU server logs for events

## Troubleshooting

### GPU Server Not Responding

1. Check if server is running:
   ```bash
   curl http://YOUR_VAST_AI_IP:8000/health
   ```

2. Check if models are loaded:
   - Server rejects traffic until models loaded
   - Check server logs for model loading status

3. Check firewall/port access:
   - Ensure port 8000 is accessible from your machine

### Callbacks Not Received

1. Check Asset Service is running:
   ```bash
   curl http://YOUR_VAST_AI_IP:8001/health
   ```

2. Verify callback URL in config:
   - Must be accessible from GPU server
   - If GPU server is on Vast AI, use internal IP or public IP

3. Check GPU server logs:
   - Look for "callback_sent_asset" or "callback_failed" events
   - Check for network errors

4. Verify auth tokens match:
   - `config.yaml` `asset_service.internal_auth_token` must match
   - `test_asset_service.py` `ASSET_AUTH_TOKEN`

### Authentication Failures

1. Verify auth tokens match:
   - `config.yaml` `security.internal_auth_token` must match
   - `test_client.py` `INTERNAL_AUTH_TOKEN`

2. Check headers are sent correctly:
   - Use browser dev tools or curl to verify

### GPU Busy Issues

1. If always getting 429:
   - Check if previous job is stuck
   - Restart GPU server to reset state

2. If never getting 429:
   - May indicate jobs complete too quickly
   - Try sending multiple requests simultaneously

## Advanced Testing

### Load Testing

Send multiple requests:

```python
import concurrent.futures
import requests

def send_request(job_id):
    # ... request code ...

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(send_request, f"job_{i}") for i in range(10)]
    results = [f.result() for f in futures]
```

### Error Scenarios

1. **Invalid Images**: Send corrupted image files
2. **Missing Fields**: Send request without required fields
3. **Network Issues**: Simulate callback failures
4. **Large Images**: Test with very large image files

## Important Notes

### ⚠️ Vast AI Specific

1. **Port Forwarding**: Ensure ports 8000 and 8001 are accessible
2. **Internal vs External IP**: 
   - Use internal IP for callbacks if both services on same instance
   - Use external IP for external access
3. **Firewall**: Check Vast AI firewall settings

### ⚠️ Network Configuration

If GPU server and Asset Service are on different machines:
- Update `callback_url` in `config.yaml` with correct IP/domain
- Ensure network connectivity between services
- Check firewall rules

### ⚠️ Testing on Localhost

For local testing:
- GPU server: `http://localhost:8000`
- Asset Service: `http://localhost:8001`
- Callback URL: `http://localhost:8001/v1/vton/result`

## Next Steps

After successful testing:
1. Update auth tokens for production
2. Configure proper callback URL for production Asset Service
3. Set up monitoring and alerting
4. Configure TLS/SSL for production
5. Set up proper logging aggregation

