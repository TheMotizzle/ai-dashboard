#!/usr/bin/env python3
"""ComfyUI server status checking module."""
import json
from typing import Dict, List
import urllib.request

HTTP_TIMEOUT = 2


def get_comfyui_server_status(port: int) -> Dict:
    """Check ComfyUI server status on given port."""
    result = {
        "port": port,
        "status": "OFFLINE",
        "error": None
    }
    
    try:
        url = f"http://localhost:{port}/object_info"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            response.read()
            result["status"] = "ONLINE"
    except urllib.error.URLError:
        pass
    except Exception:
        pass
    
    return result


def get_all_comfyui_servers(ports: List[int]) -> List[Dict]:
    """Get status for all ComfyUI servers on specified ports."""
    return [get_comfyui_server_status(port) for port in ports]
