
import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

# Keep operational records separate from the existing audit log.
LOG_PATH = Path(__file__).resolve().parent / "logs" / "operations.jsonl"
_lock = threading.Lock()


def summarize_input(payload):
    """Describe an incoming JSON body without storing private text."""
    if not isinstance(payload, dict):
        return {"body_type": type(payload).__name__}

    summary = {
        "fields": sorted(str(key) for key in payload.keys())
    }

    for field in ("text", "reasoning", "message"):
        if field in payload:
            value = payload[field]
            summary[f"{field}_type"] = type(value).__name__

            if isinstance(value, str):
                summary[f"{field}_length"] = len(value)
                summary[f"{field}_sha256"] = hashlib.sha256(
                    value.encode("utf-8")
                ).hexdigest()[:16]

    if "creator_id" in payload:
        creator = payload["creator_id"]
        summary["has_creator_id"] = (
            isinstance(creator, str) and bool(creator.strip())
        )

    if "content_id" in payload:
        summary["content_id"] = str(payload["content_id"])[:100]

    return summary


def summarize_output(payload):
    """Capture useful response fields without copying full response bodies."""
    if not isinstance(payload, dict):
        return {"body_type": type(payload).__name__}

    allowed_fields = (
        "content_id",
        "guess",
        "confidence",
        "status",
        "error",
        "ok",
        "count",
        "service",
    )

    return {
        key: payload[key]
        for key in allowed_fields
        if key in payload
    }


def write_request_log(
    method,
    path,
    input_summary,
    output_summary,
    status_code,
    duration_ms,
):
    """Append one structured record for an HTTP request."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "input": input_summary,
        "output": output_summary,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 3),
        "error": (
            output_summary.get("error", "http_error")
            if status_code >= 400
            else None
        ),
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _lock:
        with LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry
