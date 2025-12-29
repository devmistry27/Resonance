import uvicorn
import os

# Override port for testing
os.environ["PORT"] = "8001"

if __name__ == "__main__":
    print("Starting test server on port 8002...")
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
