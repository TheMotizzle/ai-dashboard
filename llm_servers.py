#!/usr/bin/env python3
import json
from typing import Dict, List
import urllib.request

HTTP_TIMEOUT = 2


def get_llm_server_status(port: int) -> Dict:
    """Check LLM server status on given port."""
    result = {
        "port": port,
        "status": "OFFLINE",
        "model_id": None
    }
    
    try:
        url = f"http://localhost:{port}/v1/models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            data = json.loads(response.read().decode())
            result["status"] = "ONLINE"
            if isinstance(data.get("data"), list) and len(data["data"]) > 0:
                result["model_id"] = data["data"][0].get("id", "unknown")
    except Exception:
        pass
    
    return result


def get_all_llm_server_status(ports: List[int]) -> List[Dict]:
    """Get status for all LLM servers on specified ports."""
    return [get_llm_server_status(port) for port in ports]
