# Quick Start Testing Guide

## Step-by-Step Testing

### 1. Start Asset Service (Terminal 1)

```bash
cd /home/fashionx/qwen_production/vtryon2
python test_asset_service.py
```

You should see:
```
============================================================
Mock Asset Service Starting...
============================================================
Port: 8001
Waiting for callbacks from GPU server...
```

### 2. Update GPU Server Config

Edit `gpu-server-qwen/configs/config.yaml`:

```yaml
asset_service:
  callback_url: "http://YOUR_VAST_AI_IP:8001/v1/vton/result"
```

**If both services on same machine:**
```yaml
asset_service:
  callback_url: "http://localhost:8001/v1/vton/result"
```

### 3. Start GPU Server (Terminal 2)

```bash
cd /home/fashionx/qwen_production/vtryon2/gpu-server-qwen
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Wait for models to load (check logs).

### 4. Run Test Client (Terminal 3)

```bash
cd /home/fashionx/qwen_production/vtryon2
python test_client.py http://YOUR_VAST_AI_IP:8000
```

Or if testing locally:
```bash
python test_client.py http://localhost:8000
```

### 5. Verify Results

1. **Test Client** should show:
   - ✅ All endpoints responding
   - ✅ Job accepted (202)
   - ✅ GPU status checks

2. **Asset Service** should show:
   - 📥 Callback received
   - ✅ Image saved to `asset_service_output/`
   - ✅ All callback data displayed

3. **GPU Server** logs should show:
   - JSON structured logs
   - All events (request_received, inference_started, etc.)
   - Callback status

## Key Points Outside Test Apps

### 1. Network Configuration

**If GPU server and Asset Service on different machines:**
- GPU server must be able to reach Asset Service callback URL
- Update `callback_url` in `config.yaml` with correct IP/domain
- Check firewall rules

**If on same Vast AI instance:**
- Use `localhost` or internal IP for callback URL
- Both services can use same network interface

### 2. Port Access

- GPU server: Port 8000
- Asset Service: Port 8001
- Ensure ports are accessible (Vast AI port forwarding)

### 3. Model Files

GPU server needs models in:
- `models/checkpoints/` - UNET model
- `models/clip/` - CLIP model
- `models/vae/` - VAE model
- `models/loras/` - LoRA model

Server will reject traffic until models loaded.

### 4. Authentication Tokens

Current test tokens (in `config.yaml` and test apps):
- `TEST_BRIDGE_TO_GPU_SECRET` - For CPU Bridge → GPU Server
- `TEST_GPU_TO_ASSET_SECRET` - For GPU Server → Asset Service

**For production:** Change these to secure random tokens.

### 5. Image Files

Test images must exist:
- `input/masked_person.png`
- `input/cloth.png`

Test client will check and fail if missing.

### 6. GPU Availability

- Server needs GPU access (CUDA)
- Check with: `nvidia-smi`
- Server will work on CPU but very slow

### 7. Logging

GPU server logs in JSON format to stdout.
For production, consider:
- Log aggregation (ELK, Loki, etc.)
- Log rotation
- Structured log parsing

### 8. Error Handling

Test these scenarios:
- Invalid images → Should send error callback
- Network failures → Should retry callback
- GPU OOM → Should send error callback
- Missing fields → Should return 400

### 9. Monitoring

Consider monitoring:
- GPU utilization
- Inference latency
- Callback success rate
- Error rates
- Queue length

### 10. Production Checklist

Before production:
- [ ] Change auth tokens to secure values
- [ ] Configure TLS/SSL
- [ ] Set up proper logging
- [ ] Configure monitoring
- [ ] Test error scenarios
- [ ] Load testing
- [ ] Security review
- [ ] Documentation

## Common Issues

### "Models not loaded"
- Wait for server startup to complete
- Check server logs for model loading errors
- Verify model files exist

### "Connection refused"
- Check if services are running
- Verify port numbers
- Check firewall rules

### "401 Unauthorized"
- Verify auth tokens match in config and test apps
- Check `X-Internal-Auth` header is sent

### "429 Too Many Requests"
- GPU is busy processing another job
- Wait for current job to complete
- Or send to different GPU node

### "Callback not received"
- Check Asset Service is running
- Verify callback URL is correct
- Check network connectivity
- Review GPU server logs for callback errors

