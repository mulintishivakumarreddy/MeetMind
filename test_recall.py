"""
MeetMind – Test Recall Module
Tests Hindsight memory recall for:
1. Known contact ('Rahul') -> verifies previous meeting memories are retrieved
2. Unknown contact ('UnknownPerson') -> verifies empty result, zero hallucination
"""

import sys
import logging
from pathlib import Path

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

from recall import recall_contact
from hindsight_config import HINDSIGHT_BANK_ID, HINDSIGHT_BASE_URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("meetmind.test_recall")


def run_recall_tests():
    print("=" * 70)
    print(">>> MeetMind -- Testing Memory Retrieval (Recall)")
    print("=" * 70)
    print(f"Target Hindsight URL: {HINDSIGHT_BASE_URL}")
    print(f"Target Memory Bank:   {HINDSIGHT_BANK_ID}")
    print("-" * 70)

    all_passed = True

    # -------------------------------------------------------------
    # TEST 1: Recall Known Contact ("Rahul")
    # -------------------------------------------------------------
    print("\n[TEST 1/2] Recalling memories for known contact: 'Rahul'...")
    res_rahul = recall_contact("Rahul")

    print(f"  Status:       {'[PASS]' if res_rahul['success'] else '[FAIL]'}")
    print(f"  Count:        {res_rahul['count']} memories retrieved")
    print(f"  Has Memories: {res_rahul['has_memories']}")
    print(f"  Message:      {res_rahul['message']}")

    if res_rahul["count"] > 0:
        print("\n  Retrieved Facts from Hindsight:")
        for idx, mem in enumerate(res_rahul["memories"][:5], start=1):
            print(f"    [{idx}] ({mem.get('type')}): {mem.get('text')}")

        # Check for core facts
        all_texts = " ".join(m.get("text", "") for m in res_rahul["memories"]).lower()
        has_dashboard = "dashboard" in all_texts
        has_prototype = "prototype" in all_texts or "friday" in all_texts or "october" in all_texts
        has_updates = "short" in all_texts or "updates" in all_texts

        print("\n  Verifying Content Extraction:")
        print(f"    - Dashboard Request Found:     {'YES' if has_dashboard else 'NO'}")
        print(f"    - Prototype/Deadline Found:    {'YES' if has_prototype else 'NO'}")
        print(f"    - Short Updates Preference:    {'YES' if has_updates else 'NO'}")

        if not (has_dashboard and has_prototype and has_updates):
            print("  [WARN] Some specific details might be missing from the top results.")
    else:
        print("  [FAIL] Expected memories for 'Rahul', but found 0.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 2: Recall Unknown Contact ("UnknownPerson")
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[TEST 2/2] Recalling memories for unknown contact: 'UnknownPerson'...")
    res_unknown = recall_contact("UnknownPerson")

    print(f"  Status:       {'[PASS]' if res_unknown['success'] else '[FAIL]'}")
    print(f"  Count:        {res_unknown['count']} memories retrieved")
    print(f"  Has Memories: {res_unknown['has_memories']}")
    print(f"  Message:      {res_unknown['message']}")

    if res_unknown["count"] == 0 and not res_unknown["has_memories"]:
        print("  Verification: [PASS] Zero memories returned. No false facts invented.")
    else:
        print("  Verification: [FAIL] Expected 0 memories for unknown contact, but got results.")
        all_passed = False

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("RECALL TEST SUMMARY:")
    print("=" * 70)
    if all_passed:
        print("[ALL PASS] Hindsight Recall layer functions accurately for both known and unknown contacts!")
        return 0
    else:
        print("[FAIL] One or more recall test cases failed.")
        return 1


if __name__ == "__main__":
    exit_code = run_recall_tests()
    sys.exit(exit_code)
