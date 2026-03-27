"""
Deep observability and debugging tracer for external API integrations.
Writes structured telemetry to `d:/Crypto/debug.txt`.
"""
import time
import json
from pathlib import Path
from typing import Any

DEBUG_FILE = Path("d:/Crypto/debug.txt")

def init_debug_file() -> None:
    """Clear the file to start a fresh debug session."""
    with open(DEBUG_FILE, "w", encoding="utf-8") as f:
        f.write("=== API DEBUG STRATEGY INITIALISED ===\n")
        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")


def log_debug(
    exchange: str,
    endpoint: str,
    latency_ms: float,
    status_code: int | str,
    raw_response: Any,
    parsed_count: int = 0,
    missing_fields: list[str] | None = None,
    errors: str | None = None
) -> None:
    """Append deep observability data for a single API call."""
    try:
        with open(DEBUG_FILE, "a", encoding="utf-8") as f:
            f.write("-" * 80 + "\n")
            f.write(f"TIMESTAMP  : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"EXCHANGE   : {exchange}\n")
            f.write(f"ENDPOINT   : {endpoint}\n")
            f.write(f"LATENCY    : {latency_ms:.2f} ms\n")
            f.write(f"STATUS     : {status_code}\n")
            
            # Truncate raw response safely to avoid MBs of text per request
            if isinstance(raw_response, (dict, list)):
                res_str = json.dumps(raw_response)
            else:
                res_str = str(raw_response)
            
            if len(res_str) > 500:
                res_str = res_str[:500] + f"... [truncated {len(res_str)-500} bytes]"
            
            f.write(f"RAW RES    : {res_str}\n")
            f.write(f"PARSED     : {parsed_count} valid items extracted\n")
            
            if missing_fields:
                f.write(f"MISSING    : {', '.join(missing_fields)}\n")
            if errors:
                f.write(f"ERRORS     : {errors}\n")
            
            f.write("-" * 80 + "\n\n")
    except Exception as e:
        print(f"Failed to write to debug.txt: {e}")
