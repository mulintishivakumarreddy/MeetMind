"""
MeetMind – Meeting Memory Storage Layer (Retain)
Stores structured meeting interactions, decisions, commitments, deadlines,
and contact preferences in Hindsight persistent memory.
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dateutil import parser as date_parser

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path regardless of current working directory
_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
if (_current_dir.parent / "hindsight_config.py").exists() and str(_current_dir.parent) not in sys.path:
    sys.path.insert(0, str(_current_dir.parent))

from hindsight_config import (
    get_hindsight_client,
    HINDSIGHT_BANK_ID,
    ensure_bank_exists,
)

logger = logging.getLogger("meetmind.retain")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def parse_and_validate_date(date_str: Optional[str]) -> tuple[bool, Optional[str], Optional[datetime]]:
    """
    Validates and parses a meeting date string.
    Returns: (is_valid, formatted_date_str, datetime_obj)
    """
    if not date_str or not str(date_str).strip():
        now = datetime.now()
        return True, now.strftime("%Y-%m-%d"), now

    clean_str = str(date_str).strip()
    try:
        dt = date_parser.parse(clean_str)
        if dt.year < 1900 or dt.year > 2100:
            return False, None, None
        return True, dt.strftime("%Y-%m-%d"), dt
    except Exception:
        return False, None, None


def remember_meeting(
    contact: str,
    date: str,
    notes: str,
    bank_id: Optional[str] = None,
    client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Store meeting information in Hindsight persistent memory.

    Parameters:
        contact (str): Full name or identifier of the contact (e.g. 'Rahul')
        date (str): Date of the meeting (YYYY-MM-DD or readable date string)
        notes (str): Raw notes covering discussions, commitments, deadlines, and preferences
        bank_id (str, optional): Target memory bank ID (defaults to HINDSIGHT_BANK_ID)
        client (Hindsight, optional): Active Hindsight client instance

    Returns:
        dict: Result with 'success' boolean, bank_id, contact, date, and confirmation message.
    """
    # 1. Input Validation
    if not contact or not str(contact).strip():
        return {
            "success": False,
            "error": "ValidationError",
            "message": "Contact name is required and cannot be empty.",
        }

    if not notes or not str(notes).strip():
        return {
            "success": False,
            "error": "ValidationError",
            "message": "Meeting notes are required and cannot be empty.",
        }

    # 2. Validate and Parse Event Date
    is_valid_date, date_clean, event_timestamp = parse_and_validate_date(date)
    if not is_valid_date:
        return {
            "success": False,
            "error": "ValidationError",
            "message": f"Invalid date format: '{date}'. Please provide a valid date string (e.g. YYYY-MM-DD).",
        }

    contact_clean = str(contact).strip()
    notes_clean = str(notes).strip()
    target_bank = bank_id or HINDSIGHT_BANK_ID

    # 3. Format Structured Memory Content
    # Ensures contact, date, discussion, commitments, deadlines, and preferences are explicitly captured
    memory_content = (
        f"Meeting Record with {contact_clean}\n"
        f"Date: {date_clean}\n"
        f"Participant: {contact_clean}\n\n"
        f"Meeting Notes & Discussion:\n"
        f"{notes_clean}\n"
    )

    contact_tag = contact_clean.lower().replace(" ", "_")

    # 4. Ingest into Hindsight
    hindsight = client or get_hindsight_client()

    try:
        # Ensure bank exists before retaining
        ensure_bank_exists(hindsight, target_bank)

        logger.info(f"Retaining meeting memory for '{contact_clean}' in bank '{target_bank}'...")

        response = hindsight.retain(
            bank_id=target_bank,
            content=memory_content,
            timestamp=event_timestamp,
            context=f"Executive meeting record with {contact_clean} on {date_clean}",
            tags=[contact_tag, "meeting", "meeting_record"],
            metadata={
                "contact": contact_clean,
                "date": date_clean,
                "source": "MeetMind",
            },
            entities=[
                {"text": contact_clean, "type": "person"}
            ],
            resolve_entities=True,
        )

        success = getattr(response, "success", True)
        items_count = getattr(response, "items_count", 1)

        logger.info(f"Successfully stored memory for '{contact_clean}' (items: {items_count}).")
        return {
            "success": success,
            "contact": contact_clean,
            "date": date_clean,
            "bank_id": target_bank,
            "items_count": items_count,
            "message": f"Successfully stored meeting memories for {contact_clean} in Hindsight bank '{target_bank}'.",
        }

    except Exception as e:
        logger.error(f"Error storing meeting memory in Hindsight: {e}")
        return {
            "success": False,
            "contact": contact_clean,
            "date": date_clean,
            "bank_id": target_bank,
            "error": str(e),
            "message": f"Failed to store meeting memory in Hindsight: {e}",
        }
    finally:
        # Close client connection if created locally
        if client is None and hasattr(hindsight, "close"):
            try:
                hindsight.close()
            except Exception:
                pass


# Alias for backward compatibility
retain_meeting = remember_meeting
