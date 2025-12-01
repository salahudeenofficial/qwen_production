"""
Test client for Qwen GPU Server.
Sends requests to the GPU server and displays responses.
"""
import requests
import json
import sys
from pathlib import Path
from typing import Optional

# Configuration
GPU_SERVER_URL = "http://108.231.141.46:17857"  # Vast AI instance URL
INTERNAL_AUTH_TOKEN = "TEST_BRIDGE_TO_GPU_SECRET"  # Must match config.yaml

# Test images
INPUT_DIR = Path("input")
MASKED_PERSON_IMAGE = INPUT_DIR / "masked_person.png"
GARMENT_IMAGE = INPUT_DIR / "cloth.png"


def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("Testing /health endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{GPU_SERVER_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_version():
    """Test version endpoint."""
    print("\n" + "="*60)
    print("Testing /version endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{GPU_SERVER_URL}/version", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_metrics():
    """Test metrics endpoint."""
    print("\n" + "="*60)
    print("Testing /metrics endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{GPU_SERVER_URL}/metrics", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_gpu_status():
    """Test GPU status endpoint."""
    print("\n" + "="*60)
    print("Testing /gpu/status endpoint")
    print("="*60)
    
    try:
        headers = {
            "X-Internal-Auth": INTERNAL_AUTH_TOKEN
        }
        response = requests.get(
            f"{GPU_SERVER_URL}/gpu/status",
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_tryon(job_id: str, prompt: Optional[str] = None):
    """
    Test /tryon endpoint.
    
    Args:
        job_id: Unique job identifier
        prompt: Optional custom prompt
    """
    print("\n" + "="*60)
    print(f"Testing /tryon endpoint (Job ID: {job_id})")
    print("="*60)
    
    # Check if images exist
    if not MASKED_PERSON_IMAGE.exists():
        print(f"Error: {MASKED_PERSON_IMAGE} not found")
        return False
    
    if not GARMENT_IMAGE.exists():
        print(f"Error: {GARMENT_IMAGE} not found")
        return False
    
    # Prepare form data
    headers = {
        "X-Internal-Auth": INTERNAL_AUTH_TOKEN
    }
    
    data = {
        "job_id": job_id,
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "provider": "qwen",
    }
    
    # Add config if prompt provided
    if prompt:
        config = {
            "prompt": prompt,
            "steps": 4,
            "cfg": 1.0
        }
        data["config"] = json.dumps(config)
    
    files = {
        "masked_user_image": (
            MASKED_PERSON_IMAGE.name,
            open(MASKED_PERSON_IMAGE, "rb"),
            "image/png"
        ),
        "garment_image": (
            GARMENT_IMAGE.name,
            open(GARMENT_IMAGE, "rb"),
            "image/png"
        ),
    }
    
    try:
        print(f"Sending request to {GPU_SERVER_URL}/tryon")
        print(f"Job ID: {job_id}")
        print(f"Headers: X-Internal-Auth: {INTERNAL_AUTH_TOKEN[:20]}...")
        
        response = requests.post(
            f"{GPU_SERVER_URL}/tryon",
            headers=headers,
            data=data,
            files=files,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ["x-node-id", "retry-after"]:
                print(f"  {key}: {value}")
        
        if response.status_code == 202:
            print("✅ Job accepted! Processing asynchronously...")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("\n⚠️  Note: Result will be sent to Asset Service via callback.")
            print("   Check the Asset Service logs to see the result.")
            return True
        elif response.status_code == 429:
            print("⚠️  GPU is busy. Job rejected.")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close file handles
        for file_tuple in files.values():
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()


def test_unauthorized():
    """Test unauthorized access (missing auth header)."""
    print("\n" + "="*60)
    print("Testing unauthorized access (no X-Internal-Auth)")
    print("="*60)
    
    try:
        # Send minimal valid data so FastAPI validation passes
        # Then auth check will run and return 401
        with open(MASKED_PERSON_IMAGE, "rb") as f1, open(GARMENT_IMAGE, "rb") as f2:
            files = {
                "masked_user_image": ("person.png", f1, "image/png"),
                "garment_image": ("cloth.png", f2, "image/png")
            }
            data = {
                "job_id": "test_unauth",
                "user_id": "test_user",
                "session_id": "test_session",
                "provider": "qwen"
            }
            # No X-Internal-Auth header - should get 401
            response = requests.post(
                f"{GPU_SERVER_URL}/tryon",
                data=data,
                files=files,
                timeout=10
            )
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized request")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            if response.status_code == 422:
                print("   (FastAPI validation ran before auth check)")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Qwen GPU Server Test Client")
    print("="*60)
    print(f"Server URL: {GPU_SERVER_URL}")
    print(f"Auth Token: {INTERNAL_AUTH_TOKEN[:20]}...")
    print("="*60)
    
    # Check if images exist
    if not MASKED_PERSON_IMAGE.exists() or not GARMENT_IMAGE.exists():
        print("\n❌ Error: Test images not found!")
        print(f"Expected: {MASKED_PERSON_IMAGE}")
        print(f"Expected: {GARMENT_IMAGE}")
        print("\nPlease ensure images exist in the input/ directory")
        return
    
    results = []
    
    # Test basic endpoints
    results.append(("Health", test_health()))
    results.append(("Version", test_version()))
    results.append(("Metrics", test_metrics()))
    results.append(("GPU Status", test_gpu_status()))
    results.append(("Unauthorized", test_unauthorized()))
    
    # Test tryon endpoint
    import uuid
    job_id = f"test_job_{uuid.uuid4().hex[:8]}"
    results.append(("Tryon (Accepted)", test_tryon(job_id)))
    
    # Test busy state (send multiple requests quickly)
    print("\n" + "="*60)
    print("Testing GPU busy state (sending 2 requests quickly)")
    print("="*60)
    job_id_1 = f"test_job_{uuid.uuid4().hex[:8]}"
    job_id_2 = f"test_job_{uuid.uuid4().hex[:8]}"
    
    # Send first request
    test_tryon(job_id_1)
    
    # Immediately send second request (should get 429 if GPU is busy)
    import time
    time.sleep(0.5)  # Small delay
    results.append(("Tryon (Busy Check)", test_tryon(job_id_2)))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")


if __name__ == "__main__":
    # Allow URL override via command line
    if len(sys.argv) > 1:
        GPU_SERVER_URL = sys.argv[1]
        print(f"Using custom server URL: {GPU_SERVER_URL}")
    
    main()

