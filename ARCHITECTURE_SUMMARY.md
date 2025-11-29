# Qwen Production Architecture Summary

## Overview
This repository is a production-ready ComfyUI workflow execution system that runs Qwen Image Edit workflows without the frontend. It provides a FastAPI-based API server that loads models once at startup and executes workflows on-demand.

## Key Components

### 1. **FastAPI Server (`api_server.py`)**
- **Purpose**: Main API server for handling virtual try-on requests
- **Key Features**:
  - Model caching at startup (loads once, reuses for all requests)
  - Single endpoint: `POST /tryon` for virtual try-on requests
  - Health check endpoint: `GET /health`
  - CORS enabled for cross-origin requests
  - Automatic model loading on startup via lifespan context manager

**Workflow**:
1. Receives `masked_person_image`, `cloth_image`, and `prompt` via POST request
2. Saves uploaded images temporarily
3. Executes the Qwen Image Edit workflow
4. Returns the generated image

### 2. **Model Caching (`model_cache.py`)**
- **Purpose**: Loads and caches all AI models at startup
- **Models Loaded**:
  - UNET: `qwen_image_edit_2509_fp8_e4m3fn.safetensors`
  - CLIP: `qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - VAE: `qwen_image_vae.safetensors`
  - LoRA: `Qwen-Image-Lightning-4steps-V2.0.safetensors`

**Key Functions**:
- `load_models_once()`: Loads all models at startup
- `get_cached_model(model_type)`: Retrieves cached models
- `is_models_loaded()`: Checks if models are loaded
- Models are kept in CPU memory and moved to GPU automatically when needed

### 3. **Workflow Execution (`workflow_script_serial.py`)**
- **Purpose**: Serial execution of the Qwen Image Edit workflow
- **Key Functions**:
  - `add_comfyui_directory_to_sys_path()`: Adds ComfyUI to Python path
  - `add_extra_model_paths()`: Loads extra model paths from config
  - `import_custom_nodes_minimal()`: Loads custom nodes with minimal async setup
  - `get_value_at_index()`: Helper to extract values from node outputs

**Workflow Steps**:
1. Load and scale masked person image
2. Encode image to latent space using VAE
3. Load cloth image
4. Apply LoRA model to UNET
5. Apply ModelSamplingAuraFlow and CFGNorm transformations
6. Encode text prompts with images (positive and negative)
7. Run KSampler for diffusion sampling (4 steps, Euler sampler)
8. Decode latent to image using VAE
9. Save output image

### 4. **ComfyUI Core Components**

#### **Node System (`nodes.py`)**
- Core ComfyUI nodes: UNETLoader, CLIPLoader, VAELoader, KSampler, etc.
- Custom nodes loaded from `custom_nodes/` directory
- Node class mappings for dynamic node instantiation

#### **Model Management (`comfy/model_management.py`)**
- Handles GPU/CPU memory management
- Automatic model offloading
- Smart memory allocation

#### **Execution System (`execution.py`)**
- Graph execution engine
- Caching system for efficient re-execution
- Progress tracking and status updates

### 5. **API Server Structure (`api_server/`)**

#### **Internal Routes (`api_server/routes/internal/`)**
- Internal endpoints for ComfyUI frontend (if needed)
- Logs, folder paths, file management
- Terminal service integration

#### **Services (`api_server/services/`)**
- Terminal service for log streaming
- File operations utilities

### 6. **App Management (`app/`)**

#### **Model Manager (`app/model_manager.py`)**
- Model file discovery and caching
- Model preview generation
- File metadata management

#### **User Manager (`app/user_manager.py`)**
- Multi-user support
- User data directory management
- File operations (upload, download, delete, move)

#### **App Settings (`app/app_settings.py`)**
- User settings management
- JSON-based configuration storage

## Architecture Flow

```
Client Request
    ↓
FastAPI Server (api_server.py)
    ↓
Model Cache (model_cache.py) - Models already loaded
    ↓
Workflow Execution (workflow_script_serial.py)
    ↓
ComfyUI Nodes (nodes.py)
    ↓
Model Management (comfy/model_management.py)
    ↓
GPU/CPU Execution
    ↓
Result Image
    ↓
FastAPI Response
```

## Important Modules

### **Core (Must Keep)**
- `api_server.py` - Main FastAPI server
- `model_cache.py` - Model caching system
- `workflow_script_serial.py` - Workflow execution
- `main.py` - ComfyUI entry point
- `nodes.py` - Node definitions
- `execution.py` - Execution engine
- `comfy/` - Core ComfyUI library
- `app/` - Application management modules

### **Supporting (Important)**
- `folder_paths.py` - Model path management
- `comfy_execution/` - Execution utilities
- `comfy_api/` - API definitions
- `custom_nodes/` - Custom node implementations
- `api_server/` - API server structure

### **Optional (Can Remove for Production)**
- `microservices/` - Microservices architecture docs (not implemented)
- `tests/` - Test files
- `tests-unit/` - Unit tests
- `script_examples/` - Example scripts
- `alembic_db/` - Database migrations (if not using DB)

## Model Files Required

Models should be placed in the appropriate directories:
- `models/checkpoints/` - UNET models
- `models/clip/` - CLIP models
- `models/vae/` - VAE models
- `models/loras/` - LoRA models

## Configuration

### **Environment Variables**
- Model paths can be configured via `extra_model_paths.yaml`
- Input/output directories can be set via CLI args or config

### **Startup Process**
1. FastAPI server starts
2. Lifespan context manager loads models via `load_models_once()`
3. Custom nodes are loaded
4. All models are cached in CPU memory
5. Server ready to accept requests

## API Usage

### **POST /tryon**
```bash
curl -X POST "http://localhost:8000/tryon" \
  -F "masked_person_image=@masked_person.png" \
  -F "cloth_image=@cloth.png" \
  -F "prompt=by using the green masked area from Picture 3 as a reference for position place the garment from Picture 2 on the person from Picture 1." \
  -F "seed=12345" \
  --output result.png
```

### **GET /health**
```bash
curl http://localhost:8000/health
```

## Production Considerations

1. **Model Loading**: Models are loaded once at startup, reducing per-request overhead
2. **Memory Management**: ComfyUI automatically manages GPU/CPU memory
3. **Error Handling**: Comprehensive error handling and logging
4. **CORS**: Configured for cross-origin requests (adjust for production)
5. **Security**: Add authentication/authorization for production
6. **Scaling**: Consider using multiple workers or container orchestration

## Key Differences from Standard ComfyUI

1. **No Frontend**: This is a headless execution system
2. **Model Caching**: Models loaded once and reused
3. **FastAPI Integration**: REST API instead of WebSocket
4. **Serial Execution**: Workflow runs serially without queue system
5. **Simplified Setup**: Minimal async setup for custom nodes

## Branch Information

- **Current Branch**: `qwen_api`
- **Pushed to**: `qwen_production` repository (main branch)
- **Other branches pruned**: Only `qwen_api` branch kept

