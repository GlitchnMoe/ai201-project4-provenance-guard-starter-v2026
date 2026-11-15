#!/usr/bin/env python3
"""Unit 9 Provenance Guard acceptance evaluation.

Runs the five previously committed criteria, three independent trials each.
Does not alter application code or the criteria. Requires the local Flask
server to be running with debug/reloader disabled.

Usage: python run_capstone_eval.py --label before
       python run_capstone_eval.py --label after
"""

import argparse
import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "logs" / "operations.jsonl"
RESULTS_DIR = ROOT / "results"
BASE_URL = "http://127.0.0.1:5000"
SAMPLE_TEXT = (
    "Artificial intelligence is transforming the way people work, learn, "
    "and communicate. These systems can automate repetitive tasks, generate "
    "written content, and assist with decision making."
)
assert len(SAMPLE_TEXT) == 188

NAMES = [
    "Structured logging completeness",
    "Failure logging and error visibility",
    "Input privacy in operational logs",
    "Warm-model processing latency",
    "Existing application regression protection",
]
TARGETS = ["10/10", "3/3", "5/5", "at least 9/10 <=60 ms", "5/5"]


def ident(trial, kind):
    """Unique creator IDs avoid the existing per-creator rate limits."""
    return f"capstone_{kind}_t{trial}_{uuid.uuid4().hex[:10]}"


def log_offset():
    return LOG_PATH.stat().st_size if LOG_PATH.exists() else 0


def added_log_lines(previous_offset):
    """Read records appended by one request, without touching older logs."""
    if not LOG_PATH.exists():
        return []
    with LOG_PATH.open("rb") as f:
        f.seek(previous_offset)
        data = f.read()
    return [s for s in data.decode("utf-8", errors="replace").splitlines() if s]


def send(method, path, payload=None):
    """Capture actual HTTP response and the appended operational log entry."""
    before = log_offset()
    try:
        response = requests.request(
            method, BASE_URL + path, json=payload, timeout=180
        )
        try:
            body = response.json()
        except ValueError:
            body = {"non_json_body": response.text[:400]}
        status = response.status_code
        transport_error = None
    except requests.RequestException as exc:
        body = {"transport_error": str(exc)}
        status = None
        transport_error = str(exc)

    raw = added_log_lines(before)
    parsed = []
    for line in raw:
        try:
            parsed.append(json.loads(line))
        except ValueError:
            parsed.append(None)

    return {
        "method": method,
        "path": path,
        "status": status,
        "body": body,
        "log_lines": raw,
        "entries": parsed,
        "transport_error": transport_error,
    }


def exactly_one_log(item):
    return len(item["log_lines"]) == 1 and len(item["entries"]) == 1 and isinstance(item["entries"][0], dict)


def matching_basic_log(item):
    if not exactly_one_log(item):
        return False
    e = item["entries"][0]
    return (
        e.get("method") == item["method"]
        and e.get("path") == item["path"]
        and e.get("status_code") == item["status"]
    )


def valid_utc(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.tzinfo is not None and dt.utcoffset() == timedelta(0)
    except (ValueError, AttributeError, TypeError):
        return False


def valid_duration(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def c1(trial):
    events, passed = [], 0
    for i in range(5):
        message = f"capstone-c1-trial-{trial}-ping-{i}-{uuid.uuid4().hex[:8]}"
        event = send("POST", "/ping", {"message": message})
        events.append(event)
        ok = full_log_check(event)
        if ok:
            entry = event["entries"][0]
            ok = (
                event["status"] == 200
                and event["body"].get("ok") is True
                and entry["input"].get("message_sha256") == hashlib.sha256(message.encode()).hexdigest()[:16]
                and entry["output"].get("ok") is True
            )
        passed += bool(ok)

    for i in range(5):
        event = send("POST", "/submit", {"creator_id": ident(trial, f"c1_{i}"), "text": SAMPLE_TEXT})
        events.append(event)
        ok = full_log_check(event)
        if ok:
            entry = event["entries"][0]
            ok = (
                event["status"] == 200
                and bool(event["body"].get("content_id"))
                and entry["output"].get("content_id") == event["body"].get("content_id")
                and entry["output"].get("guess") == event["body"].get("guess")
            )
        passed += bool(ok)
    return {"passed": passed, "total": 10, "events": events}


def full_log_check(event):
    if not matching_basic_log(event):
        return False
    e = event["entries"][0]
    required = {"timestamp", "method", "path", "input", "output", "status_code", "duration_ms", "error"}
    return (
        required.issubset(e)
        and valid_utc(e["timestamp"])
        and isinstance(e["input"], dict)
        and isinstance(e["output"], dict)
        and valid_duration(e["duration_ms"])
    )


def c2(trial):
    cases = [
        {"creator_id": ident(trial, "missing")},
        {"creator_id": ident(trial, "empty"), "text": ""},
        {"creator_id": ident(trial, "numeric"), "text": 123},
    ]
    events, passed = [], 0
    for payload in cases:
        event = send("POST", "/submit", payload)
        events.append(event)
        ok = matching_basic_log(event) and event["status"] == 400
        if ok:
            e = event["entries"][0]
            ok = (
                isinstance(e.get("input"), dict)
                and bool(e["input"].get("fields"))
                and isinstance(e.get("error"), str)
                and bool(e["error"].strip())
                and valid_duration(e.get("duration_ms"))
                and e.get("output", {}).get("error") == event["body"].get("error")
            )
        passed += bool(ok)
    return {"passed": passed, "total": 3, "events": events}


def c3(trial):
    events, passed = [], 0
    for i in range(5):
        marker = f"PRIVATE_MARKER_T{trial}_S{i}_{uuid.uuid4().hex[:10]}"
        text = SAMPLE_TEXT + f" This synthetic privacy check uses {marker} as its unique marker."
        event = send("POST", "/submit", {"creator_id": ident(trial, f"privacy_{i}"), "text": text})
        events.append(event)
        ok = matching_basic_log(event) and event["status"] == 200
        if ok:
            entry = event["entries"][0]
            summary = entry.get("input", {})
            fingerprint = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            raw_text = "\n".join(event["log_lines"])
            ok = (
                summary.get("text_length") == len(text)
                and summary.get("text_sha256") == fingerprint
                and len(str(summary.get("text_sha256", ""))) == 16
                and marker not in raw_text
                and text not in raw_text
            )
        passed += bool(ok)
    return {"passed": passed, "total": 5, "events": events}


def c4(trial):
    # Warm-up is deliberately excluded from the 10 measured requests.
    warmup = send("POST", "/submit", {"creator_id": ident(trial, "warmup"), "text": SAMPLE_TEXT})
    events, passed, durations = [], 0, []
    for i in range(10):
        event = send("POST", "/submit", {"creator_id": ident(trial, f"timing_{i}"), "text": SAMPLE_TEXT})
        events.append(event)
        d = event["entries"][0].get("duration_ms") if matching_basic_log(event) else None
        durations.append(d)
        ok = event["status"] == 200 and valid_duration(d) and d <= 60
        passed += bool(ok)
    return {"passed": passed, "total": 10, "events": events, "warmup": warmup, "durations_ms": durations}


def c5(trial):
    events = [
        send("POST", "/ping", {"message": f"regression-trial-{trial}"}),
        send("GET", "/health"),
        send("POST", "/submit", {"creator_id": ident(trial, "regression"), "text": SAMPLE_TEXT}),
        send("POST", "/appeal", {}),
        send("GET", "/content/" + str(uuid.uuid4())),
    ]
    checks = [
        events[0]["status"] == 200 and events[0]["body"].get("ok") is True,
        events[1]["status"] == 200 and events[1]["body"].get("ok") is True,
        events[2]["status"] == 200 and all(k in events[2]["body"] for k in ("content_id", "guess", "confidence")),
        events[3]["status"] == 400 and bool(events[3]["body"].get("error")),
        events[4]["status"] == 404 and bool(events[4]["body"].get("error")),
    ]
    return {"passed": sum(checks), "total": 5, "events": events}


RUNNERS = [c1, c2, c3, c4, c5]


def score_label(data, index):
    return f"{data['passed']}/{data['total']}" + (" <=60 ms" if index == 3 else "")


def met(data, index):
    return data["passed"] >= (9 if index == 3 else data["total"])


def output_examples(result):
    chunks = []
    for index, name in enumerate(NAMES):
        trial_one = result["trials"][0]["criteria"][index]
        fn = RUNNERS[index].__name__
        # For failure criterion, show both an invalid missing-text and an empty-text example.
        sample = trial_one["events"][0]
        chunks.extend([
            f"### Criterion {index + 1}: {name}",
            f"Source: `run_capstone_eval.py::{fn}`; Flask route in `app.py`; "
            "log writer: `operational_logging.py::write_request_log`.",
            "",
            "**Actual HTTP response from trial 1:**",
            "```json",
            json.dumps({"method": sample["method"], "path": sample["path"], "status_code": sample["status"], "body": sample["body"]}, indent=2),
            "```",
            "**Actual operational log line from the same request:**",
            "```json",
            sample["log_lines"][0] if sample["log_lines"] else "(NO LOG RECORD — failure evidence)",
            "```",
        ])
        if index == 3:
            chunks.extend(["**All 10 measured durations from trial 1 (milliseconds):**", "```json", json.dumps(trial_one["durations_ms"]), "```"])
        chunks.append("")
    return "\n".join(chunks)


def save_results(result):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.fromisoformat(result["started_utc"]).strftime("%Y%m%d_%H%M%S_%fZ")
    base = RESULTS_DIR / f"capstone_{result['label']}_{stamp}"
    json_path = Path(str(base) + ".json")
    md_path = Path(str(base) + ".md")
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    parts = [
        f"# Unit 9 Capstone — {result['label'].title()} formal evaluation",
        "",
        f"Run timestamp (UTC): `{result['started_utc']}`",
        "",
        "Evaluation: `run_capstone_eval.py::main` (real localhost HTTP requests).",
        "Three complete trials were executed without application or criteria changes.",
        "",
        "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |",
        "|---|---|---|---|---|---|",
    ]
    for i, name in enumerate(NAMES):
        cases = [t["criteria"][i] for t in result["trials"]]
        verdict = "MET" if all(met(c, i) for c in cases) else "MISSED"
        parts.append(f"| {i + 1}. {name} | {TARGETS[i]} | " + " | ".join(score_label(c, i) for c in cases) + f" | {verdict} |")
    parts.extend([
        "", "## Real outputs from trial 1", "",
        "The responses and operational log lines below were captured by the evaluator, "
        "not fabricated. Complete evidence for all requests and all three trials is "
        f"in `{json_path.name}`.", "", output_examples(result),
    ])
    md_path.write_text("\n".join(parts), encoding="utf-8")
    return md_path, json_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", choices=["before", "after"], required=True)
    args = parser.parse_args()

    if not LOG_PATH.parent.is_dir():
        raise SystemExit("Missing logs/ directory. Run this script in the original repo.")
    try:
        probe = requests.get(BASE_URL + "/health", timeout=15)
    except requests.RequestException as exc:
        raise SystemExit(f"Server is not reachable at {BASE_URL}: {exc}")
    if probe.status_code != 200:
        raise SystemExit(f"/health returned {probe.status_code}; start the server before testing.")

    result = {"label": args.label, "started_utc": datetime.now(timezone.utc).isoformat(), "trials": []}
    print(f"Capstone {args.label.upper()} evaluation — 5 criteria x 3 trials")
    for trial in (1, 2, 3):
        trial_result = {"trial": trial, "criteria": []}
        print(f"\nTrial {trial}")
        for index, fn in enumerate(RUNNERS):
            data = fn(trial)
            trial_result["criteria"].append(data)
            print(f"  C{index + 1} {score_label(data, index)}: {'MET' if met(data, index) else 'MISSED'}")
        result["trials"].append(trial_result)

    md_path, json_path = save_results(result)
    print("\nFormal evaluation saved:")
    print("  ", md_path)
    print("  ", json_path)
    print("Criteria that missed in any trial:", [i + 1 for i in range(5) if not all(met(t['criteria'][i], i) for t in result['trials'])])


if __name__ == "__main__":
    main()
