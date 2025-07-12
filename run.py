import uvicorn
import os
import sys
from pathlib import Path

def main():
    # Set project root as working directory
    current_dir = Path(__file__).resolve().parent
    sys.path.append(str(current_dir))

    # Read environment-based settings
    env = os.getenv("ENV", "development").lower()
    port = int(os.getenv("PORT", 8000))
    reload = env == "development"
    workers = int(os.getenv("UVICORN_WORKERS", 1 if reload else 4))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        workers=workers,
        log_level="debug" if reload else "info",
        proxy_headers=True,         # Trust X-Forwarded-For if behind proxy
        forwarded_allow_ips="*",    # Allow all forwarded IPs
        timeout_keep_alive=30       # Optional tuning
    )

if __name__ == "__main__":
    main()
