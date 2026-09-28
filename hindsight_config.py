"""
MeetMind – Hindsight Configuration & Client Setup
Loads settings from .env and provides a reusable Hindsight client and helper utilities.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv, find_dotenv
from hindsight_client import Hindsight

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables from .env (searches current and parent directories)
_env_path = find_dotenv(usecwd=True)
if _env_path:
    load_dotenv(_env_path)
else:
    load_dotenv()

logger = logging.getLogger("meetmind.hindsight")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Environment variables
HINDSIGHT_BASE_URL: str = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io").rstrip("/")
HINDSIGHT_API_KEY: Optional[str] = os.getenv("HINDSIGHT_API_KEY", "").strip() or None
HINDSIGHT_BANK_ID: str = os.getenv("HINDSIGHT_BANK_ID", "meetmind-demo").strip()

# Tailored missions for MeetMind
RETAIN_MISSION = (
    "Extract meeting participants, key decisions, promises, deadlines, "
    "follow-up commitments, contact preferences, and unresolved topics."
)

REFLECT_MISSION = (
    "You are MeetMind, an executive meeting preparation agent. "
    "Synthesize previous meeting discussions, decisions, commitments, deadlines, "
    "and preferences to prepare the user for their upcoming meeting. "
    "Never hallucinate or invent information not present in the memories."
)


def get_hindsight_client(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: float = 30.0,
) -> Hindsight:
    """
    Creates and returns an official Hindsight client instance.
    Falls back to environment variables HINDSIGHT_BASE_URL and HINDSIGHT_API_KEY.
    """
    target_url = (base_url or HINDSIGHT_BASE_URL).rstrip("/")
    target_key = api_key if api_key is not None else HINDSIGHT_API_KEY

    return Hindsight(
        base_url=target_url,
        api_key=target_key,
        timeout=timeout,
    )


class HindsightHelper:
    """
    Reusable helper providing bank validation and connectivity diagnostic checks.
    """

    @staticmethod
    def is_credentials_configured() -> bool:
        """Check if HINDSIGHT_API_KEY is configured with a non-placeholder value."""
        if not HINDSIGHT_API_KEY:
            return False
        # Guard against common placeholder values
        if "your_" in HINDSIGHT_API_KEY.lower() or "paste_" in HINDSIGHT_API_KEY.lower():
            return False
        return True

    @staticmethod
    def check_reachability(client: Optional[Hindsight] = None) -> Dict[str, Any]:
        """
        Check if the Hindsight service is reachable via get_version().
        """
        hindsight = client or get_hindsight_client()
        try:
            version_info = hindsight.get_version()
            api_ver = getattr(version_info, "api_version", "unknown")
            features = getattr(version_info, "features", None)
            return {
                "reachable": True,
                "api_version": api_ver,
                "features": str(features) if features else None,
                "error": None,
            }
        except Exception as e:
            return {
                "reachable": False,
                "api_version": None,
                "features": None,
                "error": str(e),
            }

    @staticmethod
    def check_bank_accessibility(
        client: Optional[Hindsight] = None,
        bank_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check if the selected memory bank is accessible.
        First attempts get_bank_config(); if not found, attempts create_bank().
        """
        target_bank = bank_id or HINDSIGHT_BANK_ID
        hindsight = client or get_hindsight_client()

        # Try to get existing bank config
        try:
            config = hindsight.get_bank_config(target_bank)
            return {
                "accessible": True,
                "bank_id": target_bank,
                "status": "exists",
                "details": config,
                "error": None,
            }
        except Exception as err:
            err_str = str(err)
            # If 401 Unauthorized, credentials issue
            if "401" in err_str or "unauthorized" in err_str.lower() or "authentication failed" in err_str.lower():
                return {
                    "accessible": False,
                    "bank_id": target_bank,
                    "status": "unauthorized",
                    "details": None,
                    "error": "Authentication failed: HINDSIGHT_API_KEY is missing or invalid.",
                }

            # If 404 or bank not configured yet, attempt creation
            try:
                hindsight.create_bank(
                    bank_id=target_bank,
                    retain_mission=RETAIN_MISSION,
                    reflect_mission=REFLECT_MISSION,
                )
                return {
                    "accessible": True,
                    "bank_id": target_bank,
                    "status": "created",
                    "details": f"Memory bank '{target_bank}' created successfully.",
                    "error": None,
                }
            except Exception as create_err:
                return {
                    "accessible": False,
                    "bank_id": target_bank,
                    "status": "error",
                    "details": None,
                    "error": str(create_err),
                }

    @classmethod
    def run_connectivity_diagnostics(
        cls,
        client: Optional[Hindsight] = None,
        bank_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive diagnostic check of credentials, service reachability, and memory bank access.
        """
        hindsight = client or get_hindsight_client()
        target_bank = bank_id or HINDSIGHT_BANK_ID

        credentials_ok = cls.is_credentials_configured()
        reachability = cls.check_reachability(hindsight)
        bank_status = cls.check_bank_accessibility(hindsight, target_bank)

        # Safely close client connections
        try:
            hindsight.close()
        except Exception:
            pass

        return {
            "base_url": HINDSIGHT_BASE_URL,
            "bank_id": target_bank,
            "credentials_configured": credentials_ok,
            "service_reachable": reachability["reachable"],
            "api_version": reachability.get("api_version"),
            "reachability_error": reachability.get("error"),
            "bank_accessible": bank_status["accessible"],
            "bank_status": bank_status.get("status"),
            "bank_error": bank_status.get("error"),
        }


def ensure_bank_exists(client: Optional[Hindsight] = None, bank_id: Optional[str] = None) -> bool:
    """Convenience helper to ensure memory bank exists."""
    helper = HindsightHelper()
    result = helper.check_bank_accessibility(client, bank_id)
    return result["accessible"]
