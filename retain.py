"""
MeetMind – Meeting Memory Storage Layer (Retain)
Stores structured meeting interactions, decisions, commitments, deadlines,
follow-up statuses, and preferences in Hindsight persistent memory.
"""

import sys
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dateutil import parser as date_parser

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


def extract_meeting_dimensions(notes: str, contact: str) -> Dict[str, Any]:
    """
    Parses unstructured meeting notes into longitudinal meeting dimensions.
    Extracts discussions, decisions, commitments, deadlines, follow-up statuses,
    contact preferences, and user preferences.
    """
    sentences = [s.strip() for s in re.split(r'[.\n;]+', notes) if s.strip()]

    discussions: List[str] = []
    decisions: List[str] = []
    commitments: List[Dict[str, Any]] = []
    deadlines: List[str] = []
    followups: List[Dict[str, Any]] = []
    contact_preferences: List[str] = []
    user_preferences: List[str] = []
    unresolved_topics: List[str] = []

    contact_lower = contact.lower()

    for sentence in sentences:
        s_low = sentence.lower()

        # 1. Contact Preferences
        if any(k in s_low for k in ["prefers", "prefer", "likes", "slack over", "async", "update frequency", "communication style"]):
            if "i prefer" in s_low or "user prefer" in s_low:
                user_preferences.append(sentence)
            else:
                contact_preferences.append(sentence)

        # 2. User Meeting Style / Preparation Preferences
        if any(k in s_low for k in ["i prefer", "blockers first", "action items at", "concise summaries", "show me", "briefing style"]):
            if sentence not in user_preferences:
                user_preferences.append(sentence)

        # 3. Decisions
        if any(k in s_low for k in ["decided", "agreed to", "approved", "chosen", "consensus", "agreed that"]):
            decisions.append(sentence)

        # 4. Deadlines
        if any(k in s_low for k in ["by friday", "by monday", "deadline", "due date", "by october", "by september", "by november", "by december"]):
            deadlines.append(sentence)

        # 5. Commitments & Follow-up Tracking
        is_commitment = any(k in s_low for k in [
            "promised", "will deliver", "committed", "pledged", "agreed to deliver",
            "sent the", "delivered the", "not delivered", "still not ready", "still pending"
        ])

        if is_commitment or "prototype" in s_low or "export" in s_low or "dashboard" in s_low:
            responsible = "Me / Our Team"
            if contact_lower in s_low and any(w in s_low for w in ["promised", "will", "deliver"]):
                responsible = contact
            elif "i promised" in s_low or "we promised" in s_low or "committed" in s_low:
                responsible = "Our Team"

            status = "Pending"
            if any(k in s_low for k in ["was delivered", "sent yesterday", "completed", "already delivered", "delivered the prototype", "has been delivered"]):
                status = "Completed"
            elif any(k in s_low for k in ["not delivered", "still not ready", "missed", "overdue", "still pending", "delayed", "not ready"]):
                if any(k in s_low for k in ["not delivered", "missed", "still not ready"]):
                    status = "Missed / Overdue"
                else:
                    status = "Pending"

            item_info = {
                "item": sentence,
                "responsible": responsible,
                "status": status,
            }
            commitments.append(item_info)
            followups.append(item_info)

        # 6. General Discussions
        if any(k in s_low for k in ["requested", "reviewed", "discussed", "asked for", "demo", "feature", "requirements"]):
            discussions.append(sentence)

        # 7. Unresolved topics
        if any(k in s_low for k in ["still pending", "blocker", "unresolved", "open question", "waiting on", "needs clarification"]):
            unresolved_topics.append(sentence)

    return {
        "discussions": discussions,
        "decisions": decisions,
        "commitments": commitments,
        "deadlines": deadlines,
        "followups": followups,
        "contact_preferences": contact_preferences,
        "user_preferences": user_preferences,
        "unresolved_topics": unresolved_topics,
    }


def remember_meeting(
    contact: str,
    date: str,
    notes: str,
    bank_id: Optional[str] = None,
    client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Store meeting information in Hindsight persistent memory with longitudinal structure.
    """
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

    dims = extract_meeting_dimensions(notes_clean, contact_clean)

    content_lines = [
        f"MEETING RECORD: {contact_clean} on {date_clean}",
        f"Participant: {contact_clean}",
        f"Date: {date_clean}",
        "",
        "RAW MEETING NOTES:",
        notes_clean,
        "",
        "STRUCTURED DIMENSIONS:",
    ]

    if dims["discussions"]:
        content_lines.append(f"Discussions: {'; '.join(dims['discussions'])}")
    if dims["decisions"]:
        content_lines.append(f"Decisions: {'; '.join(dims['decisions'])}")
    if dims["commitments"]:
        commit_strs = [f"{c['item']} (Responsible: {c['responsible']}, Status: {c['status']})" for c in dims["commitments"]]
        content_lines.append(f"Commitments & Promises: {'; '.join(commit_strs)}")
    if dims["deadlines"]:
        content_lines.append(f"Deadlines: {'; '.join(dims['deadlines'])}")
    if dims["followups"]:
        f_strs = [f"{f['item']} [Status: {f['status']}]" for f in dims["followups"]]
        content_lines.append(f"Follow-ups: {'; '.join(f_strs)}")
    if dims["contact_preferences"]:
        content_lines.append(f"Contact Preferences: {'; '.join(dims['contact_preferences'])}")
    if dims["user_preferences"]:
        content_lines.append(f"User Meeting Preferences: {'; '.join(dims['user_preferences'])}")
    if dims["unresolved_topics"]:
        content_lines.append(f"Unresolved Topics & Blockers: {'; '.join(dims['unresolved_topics'])}")

    memory_content = "\n".join(content_lines)

    contact_tag = contact_clean.lower().replace(" ", "_")
    tags = [contact_tag, "meeting", "meeting_record", f"date_{date_clean}"]

    if dims["commitments"] or dims["followups"]:
        tags.append("commitment")
        tags.append("followup")
    if dims["contact_preferences"]:
        tags.append("preference")
    if dims["user_preferences"]:
        tags.append("user_preference")

    hindsight = client or get_hindsight_client()

    try:
        ensure_bank_exists(hindsight, target_bank)

        logger.info(f"Retaining structured meeting memory for '{contact_clean}' in bank '{target_bank}'...")

        response = hindsight.retain(
            bank_id=target_bank,
            content=memory_content,
            timestamp=event_timestamp,
            context=f"Executive meeting record with {contact_clean} on {date_clean}",
            tags=tags,
            metadata={
                "contact": contact_clean,
                "date": date_clean,
                "source": "MeetMind",
                "has_commitments": "true" if dims["commitments"] else "false",
                "has_followups": "true" if dims["followups"] else "false",
            },
            entities=[
                {"text": contact_clean, "type": "person"}
            ],
            resolve_entities=True,
        )

        success = getattr(response, "success", True)
        items_count = getattr(response, "items_count", 1)

        if dims["user_preferences"]:
            for pref in dims["user_preferences"]:
                remember_user_preference(
                    preference_type="meeting_style",
                    preference_value=pref,
                    source=f"Extracted from meeting with {contact_clean} on {date_clean}",
                    bank_id=target_bank,
                    client=hindsight,
                )

        logger.info(f"Successfully stored memory for '{contact_clean}' (items: {items_count}).")
        return {
            "success": success,
            "contact": contact_clean,
            "date": date_clean,
            "bank_id": target_bank,
            "items_count": items_count,
            "dimensions": dims,
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
        if client is None and hasattr(hindsight, "close"):
            try:
                hindsight.close()
            except Exception:
                pass


def remember_user_preference(
    preference_type: str,
    preference_value: str,
    source: str = "User Settings",
    bank_id: Optional[str] = None,
    client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retains user meeting preparation and interaction style into Hindsight.
    This enables MeetMind to learn how the user prefers briefings structured.
    """
    if not preference_value or not str(preference_value).strip():
        return {
            "success": False,
            "error": "ValidationError",
            "message": "Preference value cannot be empty.",
        }

    val_clean = str(preference_value).strip()
    type_clean = str(preference_type).strip() or "general"
    target_bank = bank_id or HINDSIGHT_BANK_ID

    content = (
        f"USER MEETING PREPARATION PREFERENCE:\n"
        f"Category: {type_clean}\n"
        f"Preference: {val_clean}\n"
        f"Source: {source}\n"
        f"Instruction: When generating pre-meeting briefings for this user, always apply this preference."
    )

    hindsight = client or get_hindsight_client()

    try:
        ensure_bank_exists(hindsight, target_bank)

        response = hindsight.retain(
            bank_id=target_bank,
            content=content,
            context="User meeting preparation style and briefing preference",
            tags=["user_preference", "user_style", "meetmind_user", f"pref_{type_clean}"],
            metadata={
                "type": type_clean,
                "preference": val_clean,
                "source": source,
                "is_user_preference": "true",
            },
            entities=[
                {"text": "User", "type": "person"}
            ],
            resolve_entities=True,
        )

        return {
            "success": getattr(response, "success", True),
            "type": type_clean,
            "preference": val_clean,
            "bank_id": target_bank,
            "message": "User meeting preference successfully stored in Hindsight.",
        }
    except Exception as e:
        logger.error(f"Error storing user preference in Hindsight: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to store user preference in Hindsight: {e}",
        }
    finally:
        if client is None and hasattr(hindsight, "close"):
            try:
                hindsight.close()
            except Exception:
                pass


# Aliases for backward compatibility
retain_meeting = remember_meeting
