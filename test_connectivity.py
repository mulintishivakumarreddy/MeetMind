"""
MeetMind – Hindsight Connectivity & Diagnostic Test

Verifies:
1. Hindsight credentials configuration (.env)
2. Hindsight service reachability (network & API version)
3. Target memory bank accessibility (get/create bank)

Security: NEVER prints any part of the API key.
"""

import sys
import os
import logging
from dotenv import load_dotenv, find_dotenv

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Locate and load .env file from current or parent directory
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Read environment variables
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io").rstrip("/")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "").strip() or None
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "meetmind-bank").strip()

# Suppress noisy library logs during test
logging.getLogger("hindsight_client").setLevel(logging.ERROR)
logging.getLogger("meetmind").setLevel(logging.ERROR)


def run_connectivity_test():
    print("=" * 70)
    print("MeetMind -- Hindsight Connectivity & Diagnostic Test")
    print("=" * 70)
    print(f"Target Service URL:  {HINDSIGHT_BASE_URL}")
    print(f"Target Memory Bank:  {HINDSIGHT_BANK_ID}")
    print(f"Credentials Status:  {'Configured (Hidden for security)' if HINDSIGHT_API_KEY else 'Not Configured'}")
    print("-" * 70)

    # -------------------------------------------------------------
    # 1. Credentials Check
    # -------------------------------------------------------------
    print("\n[CHECK 1/3] Hindsight Credentials Configuration:")
    if HINDSIGHT_API_KEY and not HINDSIGHT_API_KEY.startswith("your_"):
        print("  -> STATUS: [PASS] HINDSIGHT_API_KEY is configured in .env.")
        credentials_ok = True
    else:
        print("  -> STATUS: [FAIL] HINDSIGHT_API_KEY is missing or empty in .env.")
        print("     Action: Add your API key to .env (from https://ui.hindsight.vectorize.io/connect)")
        credentials_ok = False

    # -------------------------------------------------------------
    # 2. Service Reachability Check
    # -------------------------------------------------------------
    print("\n[CHECK 2/3] Hindsight Service Reachability:")
    from hindsight_client import Hindsight

    client = Hindsight(
        base_url=HINDSIGHT_BASE_URL,
        api_key=HINDSIGHT_API_KEY,
        timeout=15.0,
    )

    service_ok = False
    try:
        version_info = client.get_version()
        api_version = getattr(version_info, "api_version", "unknown")
        print(f"  -> STATUS: [PASS] Hindsight service is REACHABLE at {HINDSIGHT_BASE_URL}")
        print(f"     API Version: {api_version}")
        service_ok = True
    except Exception as e:
        print(f"  -> STATUS: [FAIL] Unable to reach Hindsight service at {HINDSIGHT_BASE_URL}")
        print(f"     Error details: {e}")

    # -------------------------------------------------------------
    # 3. Memory Bank Accessibility Check
    # -------------------------------------------------------------
    print(f"\n[CHECK 3/3] Memory Bank '{HINDSIGHT_BANK_ID}' Accessibility:")
    bank_ok = False
    if not credentials_ok:
        print(f"  -> STATUS: [FAIL] Cannot verify memory bank without a valid HINDSIGHT_API_KEY.")
    else:
        try:
            # Check if bank exists or can be accessed
            try:
                config = client.get_bank_config(HINDSIGHT_BANK_ID)
                print(f"  -> STATUS: [PASS] Memory bank '{HINDSIGHT_BANK_ID}' is ACCESSIBLE (Existing).")
                bank_ok = True
            except Exception as get_err:
                err_text = str(get_err)
                if "401" in err_text or "unauthorized" in err_text.lower():
                    print(f"  -> STATUS: [FAIL] Authentication failed. Your HINDSIGHT_API_KEY was rejected.")
                else:
                    # Attempt to create bank
                    client.create_bank(
                        bank_id=HINDSIGHT_BANK_ID,
                        retain_mission="Extract meeting participants, key decisions, promises, deadlines, follow-up commitments, and contact preferences.",
                        reflect_mission="Synthesize previous meeting discussions, decisions, commitments, deadlines, and preferences to prepare the user for their upcoming meeting.",
                    )
                    print(f"  -> STATUS: [PASS] Memory bank '{HINDSIGHT_BANK_ID}' is ACCESSIBLE (Initialized).")
                    bank_ok = True
        except Exception as e:
            print(f"  -> STATUS: [FAIL] Memory bank '{HINDSIGHT_BANK_ID}' is NOT accessible.")
            print(f"     Error details: {e}")

    # Close client session cleanly
    try:
        client.close()
    except Exception:
        pass

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY:")
    print("=" * 70)
    if credentials_ok and service_ok and bank_ok:
        print("[ALL PASS] Hindsight memory layer is fully configured, reachable, and ready!")
        return 0
    else:
        print("[FAIL] One or more connectivity checks failed. Please check the messages above.")
        return 1


if __name__ == "__main__":
    exit_code = run_connectivity_test()
    sys.exit(exit_code)
