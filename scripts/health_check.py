"""
CiteVerify AI - Health Check Probe
Queries the live FastAPI backend GET /api/health endpoint and verifies response schema.
"""
import sys
import os
import urllib.request
import json

DEFAULT_HEALTH_URL = "http://127.0.0.1:8000/api/health"


def probe_health(url: str = DEFAULT_HEALTH_URL) -> bool:
    print(f"Connecting to CiteVerify backend at: {url} ...")
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5.0) as response:
            status_code = response.getcode()
            body_bytes = response.read()
            body_str = body_bytes.decode("utf-8")
            data = json.loads(body_str)

            print(f"\n[HTTP {status_code}] Health Response:")
            print(json.dumps(data, indent=2))

            if status_code == 200 and data.get("status") == "ok":
                print("\nSUCCESS: CiteVerify backend is healthy and responding.")
                return True
            else:
                print(f"\nFAILURE: Unexpected health response: {data}")
                return False

    except urllib.error.URLError as e:
        print(f"\nFAILURE: Could not connect to backend at {url}.")
        print(f"Reason: {e.reason}")
        print("Tip: Ensure the backend is running via `python scripts/dev_start.py` or `uvicorn`.")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error probing health: {e}")
        return False


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HEALTH_URL
    success = probe_health(target_url)
    sys.exit(0 if success else 1)

