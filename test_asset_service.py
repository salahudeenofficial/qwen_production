"""
Mock Asset Service for testing GPU server callbacks.
Receives callbacks from GPU server and displays results.
"""
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException, status
from fastapi.responses import JSONResponse
import uvicorn
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
ASSET_SERVICE_PORT = 8001
ASSET_AUTH_TOKEN = "TEST_GPU_TO_ASSET_SECRET"  # Must match config.yaml

# Create output directory for received images
OUTPUT_DIR = Path("asset_service_output")
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Mock Asset Service",
    version="1.0.0",
    description="Mock Asset Service for testing GPU server callbacks"
)

# Store received callbacks for inspection
received_callbacks = []


def verify_auth(request: Request) -> bool:
    """Verify X-Internal-Auth header."""
    auth_header = request.headers.get("X-Internal-Auth")
    return auth_header == ASSET_AUTH_TOKEN


@app.post("/v1/vton/result")
async def receive_result(
    request: Request,
    job_id: str = Form(...),
    user_id: str = Form(...),
    session_id: str = Form(...),
    provider: str = Form(...),
    node_id: str = Form(...),
    model_version: str = Form(...),
    inference_time_ms: str = Form(...),
    output_image: Optional[UploadFile] = File(None),
    error: Optional[str] = Form(None),
    meta: Optional[str] = Form(None),
):
    """
    Receive callback from GPU server.
    
    This endpoint matches the specification:
    POST /v1/vton/result
    X-Internal-Auth: <GPU_TO_ASSET_SECRET>
    Content-Type: multipart/form-data
    """
    # Verify authentication
    if not verify_auth(request):
        logger.warning(f"Unauthorized callback attempt for job {job_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-Internal-Auth header"
        )
    
    # Parse metadata if provided
    metadata = None
    if meta:
        try:
            metadata = json.loads(meta)
        except:
            metadata = {"raw": meta}
    
    # Save output image if provided
    image_path = None
    if output_image:
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{job_id}_{timestamp}.png"
            image_path = OUTPUT_DIR / filename
            
            # Save image
            with open(image_path, "wb") as f:
                content = await output_image.read()
                f.write(content)
            
            logger.info(f"Saved output image: {image_path} ({len(content)} bytes)")
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
    
    # Store callback data
    callback_data = {
        "timestamp": datetime.now().isoformat(),
        "job_id": job_id,
        "user_id": user_id,
        "session_id": session_id,
        "provider": provider,
        "node_id": node_id,
        "model_version": model_version,
        "inference_time_ms": float(inference_time_ms),
        "error": error,
        "meta": metadata,
        "image_path": str(image_path) if image_path else None,
        "image_size": os.path.getsize(image_path) if image_path and image_path.exists() else None,
    }
    
    received_callbacks.append(callback_data)
    
    # Log callback
    print("\n" + "="*60)
    print("📥 CALLBACK RECEIVED FROM GPU SERVER")
    print("="*60)
    print(json.dumps(callback_data, indent=2, default=str))
    print("="*60)
    
    if error:
        logger.error(f"❌ Error callback for job {job_id}: {error}")
    else:
        logger.info(f"✅ Success callback for job {job_id}")
        logger.info(f"   Inference time: {inference_time_ms}ms")
        if image_path:
            logger.info(f"   Image saved: {image_path}")
    
    return {
        "status": "received",
        "job_id": job_id,
        "timestamp": callback_data["timestamp"]
    }


@app.get("/callbacks")
async def list_callbacks():
    """List all received callbacks (for testing)."""
    return {
        "total": len(received_callbacks),
        "callbacks": received_callbacks
    }


@app.get("/callbacks/{job_id}")
async def get_callback(job_id: str):
    """Get callback for specific job ID."""
    for callback in received_callbacks:
        if callback["job_id"] == job_id:
            return callback
    raise HTTPException(status_code=404, detail="Callback not found")


@app.delete("/callbacks")
async def clear_callbacks():
    """Clear all callbacks (for testing)."""
    global received_callbacks
    count = len(received_callbacks)
    received_callbacks = []
    return {"message": f"Cleared {count} callbacks"}


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "service": "mock_asset_service",
        "port": ASSET_SERVICE_PORT,
        "callbacks_received": len(received_callbacks)
    }


@app.get("/")
async def root():
    """Root endpoint with instructions."""
    return {
        "service": "Mock Asset Service",
        "description": "Receives callbacks from GPU server",
        "endpoints": {
            "POST /v1/vton/result": "Receive callback from GPU server",
            "GET /callbacks": "List all received callbacks",
            "GET /callbacks/{job_id}": "Get specific callback",
            "DELETE /callbacks": "Clear all callbacks",
            "GET /health": "Health check"
        },
        "configuration": {
            "port": ASSET_SERVICE_PORT,
            "auth_token": ASSET_AUTH_TOKEN[:20] + "...",
            "output_dir": str(OUTPUT_DIR)
        },
        "received_callbacks": len(received_callbacks)
    }


if __name__ == "__main__":
    print("="*60)
    print("Mock Asset Service Starting...")
    print("="*60)
    print(f"Port: {ASSET_SERVICE_PORT}")
    print(f"Auth Token: {ASSET_AUTH_TOKEN[:20]}...")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("="*60)
    print("\nWaiting for callbacks from GPU server...")
    print("Callbacks will be displayed here and saved to:", OUTPUT_DIR)
    print("\nPress CTRL+C to stop")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=ASSET_SERVICE_PORT,
        log_level="info"
    )

