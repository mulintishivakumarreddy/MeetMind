"""
MeetMind – Test Backend Endpoints
Tests every required FastAPI endpoint:
- GET  /health
- POST /meetings (with validation & real storage)
- GET  /prepare/{contact} (with known & unknown contacts)
"""

import sys
import logging
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
if (_current_dir.parent / "hindsight_config.py").exists() and str(_current_dir.parent) not in sys.path:
    sys.path.insert(0, str(_current_dir.parent))

from main import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("meetmind.test_backend")


def run_backend_tests():
    print("=" * 70)
    print(">>> MeetMind -- Testing FastAPI Backend Endpoints")
    print("=" * 70)

    client = TestClient(app)
    all_passed = True

    # -------------------------------------------------------------
    # 1. TEST GET /health
    # -------------------------------------------------------------
    print("\n[TEST 1/3] GET /health ...")
    resp_health = client.get("/health")
    print(f"  Status Code: {resp_health.status_code}")
    print(f"  Response:    {resp_health.json()}")

    assert resp_health.status_code == 200, "Health check must return 200"
    data_health = resp_health.json()
    assert "status" in data_health
    assert "hindsight_bank" in data_health
    assert "api_key" not in str(data_health).lower(), "Security check failed: API key leaked in health!"
    print("  -> GET /health: [PASS]")

    # -------------------------------------------------------------
    # 2. TEST POST /meetings
    # -------------------------------------------------------------
    print("\n[TEST 2/3] POST /meetings ...")

    # 2a. Valid meeting payload
    payload_valid = {
        "contact": "Alice Walker",
        "date": "2026-09-29",
        "notes": (
            "Alice discussed migrating the database to PostgreSQL.\n"
            "We promised to deliver the initial schema migration draft by next Tuesday.\n"
            "Alice specifically prefers asynchronous Slack updates and concise tables."
        ),
    }

    print("  Submitting valid meeting for 'Alice Walker'...")
    resp_create = client.post("/meetings", json=payload_valid)
    print(f"  Status Code: {resp_create.status_code}")
    print(f"  Response:    {resp_create.json()}")

    assert resp_create.status_code == 201, f"Expected 201, got {resp_create.status_code}"
    data_create = resp_create.json()
    assert data_create.get("status") == "success"
    assert data_create.get("contact") == "Alice Walker"
    assert "api_key" not in str(data_create).lower(), "Security check failed: API key leaked!"
    print("  -> Valid POST /meetings: [PASS]")

    # 2b. Input validation: missing contact
    print("  Testing input validation: missing contact...")
    resp_bad_contact = client.post("/meetings", json={"contact": "", "notes": "Some notes"})
    assert resp_bad_contact.status_code in [400, 422], f"Expected 400/422, got {resp_bad_contact.status_code}"
    print(f"  -> Empty contact validation (HTTP {resp_bad_contact.status_code}): [PASS]")

    # 2c. Input validation: missing notes
    print("  Testing input validation: missing notes...")
    resp_bad_notes = client.post("/meetings", json={"contact": "Bob", "notes": ""})
    assert resp_bad_notes.status_code in [400, 422], f"Expected 400/422, got {resp_bad_notes.status_code}"
    print(f"  -> Empty notes validation (HTTP {resp_bad_notes.status_code}): [PASS]")

    # -------------------------------------------------------------
    # 3. TEST GET /prepare/{contact}
    # -------------------------------------------------------------
    print("\n[TEST 3/3] GET /prepare/{contact} ...")

    # 3a. Known contact ("Rahul")
    print("  Requesting briefing for known contact 'Rahul'...")
    resp_prep_rahul = client.get("/prepare/Rahul")
    print(f"  Status Code: {resp_prep_rahul.status_code}")
    assert resp_prep_rahul.status_code == 200, f"Expected 200, got {resp_prep_rahul.status_code}"
    data_rahul = resp_prep_rahul.json()
    print(f"  Contact:      {data_rahul.get('contact')}")
    print(f"  Has Memories: {data_rahul.get('has_memories')}")
    print(f"  Memory Count: {data_rahul.get('memory_count')}")
    print(f"  Source:       {data_rahul.get('source')}")

    briefing_text = data_rahul.get("briefing", "").lower()
    assert "dashboard" in briefing_text, "Rahul briefing must mention dashboard"
    assert "prototype" in briefing_text or "october" in briefing_text or "friday" in briefing_text, "Rahul briefing must mention prototype/deadline"
    assert "short" in briefing_text or "update" in briefing_text, "Rahul briefing must mention preference"
    assert "api_key" not in str(data_rahul).lower(), "Security check failed: API key leaked!"
    print("  -> GET /prepare/Rahul: [PASS]")

    # 3b. Unknown contact ("UnknownPerson")
    print("\n  Requesting briefing for unknown contact 'UnknownPerson'...")
    resp_prep_unknown = client.get("/prepare/UnknownPerson")
    print(f"  Status Code: {resp_prep_unknown.status_code}")
    assert resp_prep_unknown.status_code == 200, f"Expected 200, got {resp_prep_unknown.status_code}"
    data_unknown = resp_prep_unknown.json()
    print(f"  Has Memories: {data_unknown.get('has_memories')}")
    print(f"  Memory Count: {data_unknown.get('memory_count')}")

    assert data_unknown.get("has_memories") is False
    assert data_unknown.get("memory_count") == 0
    assert "not available in memory" in data_unknown.get("briefing", "").lower(), "Must state 'Not available in memory.'"
    assert "dashboard" not in data_unknown.get("briefing", "").lower(), "Must not invent dashboard for unknown contact"
    print("  -> GET /prepare/UnknownPerson (Zero Hallucination): [PASS]")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("BACKEND TEST SUMMARY:")
    print("=" * 70)
    print("[ALL PASS] All FastAPI endpoints passed verification with complete Hindsight memory fidelity and zero errors!")
    return 0


if __name__ == "__main__":
    exit_code = run_backend_tests()
    sys.exit(exit_code)
