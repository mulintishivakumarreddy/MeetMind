"""
MeetMind – Test Retain Module
Performs real storage tests by retaining at least 2 sample meetings in Hindsight.
"""

import sys
import logging

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pathlib import Path

# Ensure project root is in sys.path regardless of current working directory
_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
if (_current_dir.parent / "hindsight_config.py").exists() and str(_current_dir.parent) not in sys.path:
    sys.path.insert(0, str(_current_dir.parent))

from retain import remember_meeting
from hindsight_config import HINDSIGHT_BANK_ID, HINDSIGHT_BASE_URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("meetmind.test_retain")


def run_retain_tests():
    print("=" * 70)
    print(">>> MeetMind -- Testing Meeting Memory Storage (Retain)")
    print("=" * 70)
    print(f"Target Hindsight URL: {HINDSIGHT_BASE_URL}")
    print(f"Target Memory Bank:   {HINDSIGHT_BANK_ID}")
    print("-" * 70)

    # Sample Meeting 1: Rahul
    meeting_1 = {
        "contact": "Rahul",
        "date": "2026-09-28",
        "notes": (
            "Rahul requested a dashboard.\n"
            "We promised a prototype by Friday.\n"
            "Rahul prefers short progress updates."
        ),
    }

    # Sample Meeting 2: Sarah Jenkins
    meeting_2 = {
        "contact": "Sarah Jenkins",
        "date": "2026-09-25",
        "notes": (
            "Sarah reviewed the Q3 marketing budget and strategic goals.\n"
            "We committed to sending the revised vendor proposal by Wednesday at 3 PM.\n"
            "Sarah explicitly prefers email summaries rather than Slack messages and values punctuality."
        ),
    }

    test_meetings = [meeting_1, meeting_2]
    all_success = True

    for idx, meeting in enumerate(test_meetings, start=1):
        print(f"\n[Test Case {idx}] Storing meeting for '{meeting['contact']}' on {meeting['date']}...")
        print(f"  Notes Preview:\n  " + meeting["notes"].replace("\n", "\n  "))

        result = remember_meeting(
            contact=meeting["contact"],
            date=meeting["date"],
            notes=meeting["notes"],
        )

        status = "[PASS]" if result.get("success") else "[FAIL]"
        print(f"\n  Result: {status}")
        print(f"  Message: {result.get('message')}")
        print(f"  Items Ingested: {result.get('items_count', 'N/A')}")
        if result.get("error"):
            print(f"  Error Details: {result.get('error')}")
            all_success = False

    print("\n" + "=" * 70)
    print("RETAIN TEST SUMMARY:")
    print("=" * 70)
    if all_success:
        print("[ALL PASS] All sample meetings successfully stored in Hindsight memory!")
        return 0
    else:
        print("[FAIL] One or more retain operations failed.")
        return 1


if __name__ == "__main__":
    exit_code = run_retain_tests()
    sys.exit(exit_code)
