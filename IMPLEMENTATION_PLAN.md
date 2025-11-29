# GPU Server Implementation Plan

## Overview
Transform current `api_server.py` into production GPU microservice per specification.

## Implementation Steps

### Phase 1: Core Infrastructure (Foundation)
1. **Create folder structure** (`gpu-server-qwen/`)
   - `app/main.py` - FastAPI app with lifespan
   - `app/routers/` - API endpoints
   - `app/service/` - Business logic
   - `configs/config.yaml` - Configuration
   - `models/request_models.py` - Pydantic models

2. **Configuration System** (`app/service/config.py`)
   - Load `config.yaml` at startup
   - Validate required fields (node_id, auth tokens, callback URL)
   - Expose config via singleton

3. **Authentication Middleware** (`app/service/auth.py`)
   - Check `X-Internal-Auth` header on protected routes
   - Return 401 if missing/invalid
   - Protect `/tryon` and `/gpu/status`

4. **Structured JSON Logging** (`app/service/logger.py`)
   - Replace basic logging with JSON formatter
   - Log all required events (request_received, validation_passed, etc.)
   - Always include `node_id` in logs

### Phase 2: GPU State Management
5. **Scheduler Service** (`app/service/scheduler.py`)
   - Track GPU busy state (boolean flag)
   - Track current job_id
   - Track queue length (simple counter)
   - Thread-safe operations

6. **Status Endpoint** (`app/routers/gpu_status.py`)
   - `GET /gpu/status` - Return busy state, current_job_id, queue_length
   - Protected by auth middleware

### Phase 3: Async Inference Pipeline
7. **Inference Service** (`app/service/inference.py`)
   - Extract workflow logic from `api_server.py` → `run_workflow()`
   - Wrap in async function
   - Add timing measurement
   - Handle errors gracefully

8. **Background Task Manager**
   - Use FastAPI `BackgroundTasks` or `asyncio.create_task()`
   - Process: validate → preprocess → inference → postprocess → callback → cleanup
   - Never block HTTP response

### Phase 4: API Endpoints
9. **Tryon Endpoint** (`app/routers/tryon.py`)
   - `POST /tryon` - Accept multipart/form-data
   - Validate: job_id, user_id, session_id, provider="qwen", images, config
   - Check GPU busy → return 429 or 202 immediately
   - Queue background task
   - Return 202 with node_id (never wait for inference)

10. **Health/Version/Metrics** (`app/routers/health.py`, `metrics.py`)
    - `GET /health` - Model loaded, GPU available, node_id
    - `GET /version` - Model version, backend, git commit, node_id
    - `GET /metrics` - Prometheus-style metrics (count, latency, errors, GPU stats)

### Phase 5: Asset Service Callback
11. **Callback Service** (`app/service/asset_callback.py`)
    - POST to Asset Service with multipart/form-data
    - Include: job_id, user_id, session_id, provider, node_id, model_version, inference_time_ms, output_image
    - Retry logic (3 retries with 10s timeout)
    - Handle success/failure cases
    - Log callback events

12. **Image Utilities** (`app/service/utils_image.py`)
    - Validate image formats
    - Save temporary files
    - Cleanup temp files after callback

### Phase 6: Integration & Testing
13. **Main App** (`app/main.py`)
    - FastAPI app with lifespan
    - Load config
    - Load models at startup (reuse `model_cache.py`)
    - Reject traffic until models loaded
    - Register routers
    - Add auth middleware
    - Setup JSON logging

14. **Request Models** (`models/request_models.py`)
    - Pydantic models for request validation
    - Response models for API docs

## Key Changes from Current Implementation

| Current | New |
|---------|-----|
| Synchronous response with image | Async 202 + callback |
| No authentication | X-Internal-Auth middleware |
| No busy state | GPU scheduler with busy flag |
| Direct image return | Callback to Asset Service |
| Basic logging | Structured JSON logging |
| Hardcoded config | YAML config file |
| Single endpoint | Multiple endpoints (tryon, status, health, metrics, version) |

## File Mapping

**Reuse:**
- `model_cache.py` → Keep as-is, import in inference service
- `workflow_script_serial.py` → Extract `run_workflow()` logic
- ComfyUI core → No changes needed

**New Files:**
- `gpu-server-qwen/app/main.py`
- `gpu-server-qwen/app/routers/tryon.py`
- `gpu-server-qwen/app/routers/gpu_status.py`
- `gpu-server-qwen/app/routers/health.py`
- `gpu-server-qwen/app/routers/metrics.py`
- `gpu-server-qwen/app/service/inference.py`
- `gpu-server-qwen/app/service/asset_callback.py`
- `gpu-server-qwen/app/service/scheduler.py`
- `gpu-server-qwen/app/service/auth.py`
- `gpu-server-qwen/app/service/config.py`
- `gpu-server-qwen/app/service/utils_image.py`
- `gpu-server-qwen/models/request_models.py`
- `gpu-server-qwen/configs/config.yaml`

## Implementation Order

1. ✅ Create folder structure
2. ✅ Config system + YAML
3. ✅ Auth middleware
4. ✅ JSON logging
5. ✅ Scheduler (GPU state)
6. ✅ Status endpoint
7. ✅ Inference service (extract workflow)
8. ✅ Tryon endpoint (202/429 logic)
9. ✅ Background task processing
10. ✅ Asset callback service
11. ✅ Health/Version/Metrics endpoints
12. ✅ Main app integration
13. ✅ Testing

## Dependencies to Add

```python
# requirements.txt additions
pyyaml>=6.0          # Config file parsing
httpx>=0.24.0        # Async HTTP for callbacks
python-multipart     # Already have for FastAPI
prometheus-client   # Metrics (optional, can use simple dict)
```

## Testing Strategy

1. **Unit Tests**: Each service module
2. **Integration Tests**: Full request → callback flow
3. **Load Tests**: Multiple concurrent requests
4. **Error Cases**: Invalid auth, GPU busy, callback failures

