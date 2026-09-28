"""
MeetMind – Test Meeting Briefing Generation (Reflect)
Tests:
1. prepare_meeting("Rahul") -> verifies stored memories (dashboard, prototype, preferences) appear in the briefing
2. prepare_meeting("UnknownPerson") -> verifies zero hallucination and "Not available in memory." messages
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

from reflect import prepare_meeting
from hindsight_config import HINDSIGHT_BANK_ID, HINDSIGHT_BASE_URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("meetmind.test_reflect")


def run_reflect_tests():
    print("=" * 70)
    print(">>> MeetMind -- Testing Meeting Briefing Generation (Reflect)")
    print("=" * 70)
    print(f"Target Hindsight URL: {HINDSIGHT_BASE_URL}")
    print(f"Target Memory Bank:   {HINDSIGHT_BANK_ID}")
    print("-" * 70)

    all_passed = True

    # -------------------------------------------------------------
    # TEST 1: Known Contact ("Rahul")
    # -------------------------------------------------------------
    print("\n[TEST 1/2] Generating Meeting Briefing for known contact: 'Rahul'...")
    res_rahul = prepare_meeting("Rahul")
    briefing_rahul = res_rahul.get("briefing", "")

    print(f"  Status:       {'[PASS]' if res_rahul['success'] else '[FAIL]'}")
    print(f"  Source:       {res_rahul.get('source')}")
    print(f"  Memory Count: {res_rahul.get('memory_count')}")
    print("\n--- GENERATED BRIEFING FOR RAHUL ---")
    print(briefing_rahul)
    print("-------------------------------------")

    # Verify key details for Rahul
    rahul_text_lower = briefing_rahul.lower()
    has_dashboard = "dashboard" in rahul_text_lower
    has_prototype = "prototype" in rahul_text_lower or "friday" in rahul_text_lower or "october" in rahul_text_lower
    has_preferences = "short" in rahul_text_lower or "update" in rahul_text_lower

    print("\n  Verifying Content from Stored Memories:")
    print(f"    - Mentions Dashboard Request:    {'[PASS] YES' if has_dashboard else '[FAIL] NO'}")
    print(f"    - Mentions Prototype/Deadline:   {'[PASS] YES' if has_prototype else '[FAIL] NO'}")
    print(f"    - Mentions Short Updates Pref:   {'[PASS] YES' if has_preferences else '[FAIL] NO'}")

    if not (has_dashboard and has_prototype and has_preferences):
        print("  [FAIL] Missing expected facts in Rahul's briefing.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 2: Unknown Contact ("UnknownPerson")
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[TEST 2/2] Generating Meeting Briefing for unknown contact: 'UnknownPerson'...")
    res_unknown = prepare_meeting("UnknownPerson")
    briefing_unknown = res_unknown.get("briefing", "")

    print(f"  Status:       {'[PASS]' if res_unknown['success'] else '[FAIL]'}")
    print(f"  Source:       {res_unknown.get('source')}")
    print(f"  Has Memories: {res_unknown.get('has_memories')}")
    print("\n--- GENERATED BRIEFING FOR UNKNOWN PERSON ---")
    print(briefing_unknown)
    print("---------------------------------------------")

    unknown_lower = briefing_unknown.lower()
    has_not_available = "not available in memory" in unknown_lower

    print("  Verifying Anti-Hallucination Guardrails:")
    print(f"    - Zero Memories Stored:          {'[PASS] YES' if not res_unknown.get('has_memories') else '[FAIL] NO'}")
    print(f"    - States 'Not available in memory': {'[PASS] YES' if has_not_available else '[FAIL] NO'}")

    # Ensure no fabricated dashboard or prototype is attributed to UnknownPerson
    no_fabricated_facts = "dashboard" not in unknown_lower and "prototype" not in unknown_lower
    print(f"    - No Fabricated Past Facts:      {'[PASS] YES' if no_fabricated_facts else '[FAIL] NO'}")

    if not (has_not_available and no_fabricated_facts):
        print("  [FAIL] UnknownPerson briefing failed anti-hallucination checks.")
        all_passed = False

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("REFLECT TEST SUMMARY:")
    print("=" * 70)
    if all_passed:
        print("[ALL PASS] Meeting Briefing generation is working with full Hindsight memory fidelity and zero hallucination!")
        return 0
    else:
        print("[FAIL] One or more reflect test checks failed.")
        return 1


if __name__ == "__main__":
    exit_code = run_reflect_tests()
    sys.exit(exit_code)
