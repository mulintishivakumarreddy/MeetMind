"""
MeetMind – Hindsight Recall Layer
Retrieves previous discussions, decisions, commitments, deadlines,
and contact preferences from Hindsight persistent memory.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

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
)

logger = logging.getLogger("meetmind.recall")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def _categorize_memory(text: str) -> str:
    """Classify memory text into primary briefing dimension."""
    t = text.lower()
    if any(k in t for k in ["prefer", "likes", "update", "email", "slack", "style", "communication"]):
        return "preferences"
    if any(k in t for k in ["by friday", "deadline", "by ", "due", "timeline", "october", "september"]):
        return "deadlines"
    if any(k in t for k in ["promise", "commit", "will deliver", "pledged", "agreed to"]):
        return "commitments"
    return "discussions"


def recall_contact(
    contact: str,
    bank_id: Optional[str] = None,
    client: Optional[Any] = None,
    max_tokens: int = 4096,
) -> Dict[str, Any]:
    """
    Query Hindsight for relevant memories about a specific contact.

    Parameters:
        contact (str): Full name or identifier of the contact (e.g. 'Rahul')
        bank_id (str, optional): Target memory bank ID (defaults to HINDSIGHT_BANK_ID)
        client (Hindsight, optional): Active Hindsight client instance
        max_tokens (int): Maximum token budget for recalled results

    Returns:
        dict: Clean structured information with memories, categorized elements,
              and count. If unknown or not found, returns clean empty result.
    """
    # 1. Validation
    if not contact or not str(contact).strip():
        return {
            "success": False,
            "contact": "",
            "bank_id": bank_id or HINDSIGHT_BANK_ID,
            "count": 0,
            "has_memories": False,
            "memories": [],
            "categorized": {
                "discussions": [],
                "commitments": [],
                "deadlines": [],
                "preferences": [],
            },
            "message": "Contact name is required.",
        }

    contact_clean = str(contact).strip()
    target_bank = bank_id or HINDSIGHT_BANK_ID
    contact_tag = contact_clean.lower().replace(" ", "_")

    # 2. Query focused on key executive meeting dimensions
    query = (
        f"What are the previous discussions, key decisions, promises, "
        f"commitments, deadlines, and preferences for {contact_clean}?"
    )

    hindsight = client or get_hindsight_client()

    logger.info(f"Querying Hindsight memories for contact '{contact_clean}' in bank '{target_bank}'...")

    try:
        # 3. Call official Hindsight recall API
        # Using any_strict ensures we ONLY retrieve memories tagged with this contact
        response = hindsight.recall(
            bank_id=target_bank,
            query=query,
            tags=[contact_tag],
            tags_match="any_strict",
            max_tokens=max_tokens,
            include_entities=True,
        )

        formatted_memories: List[Dict[str, Any]] = []
        categorized: Dict[str, List[str]] = {
            "discussions": [],
            "commitments": [],
            "deadlines": [],
            "preferences": [],
        }

        if response and response.results:
            for item in response.results:
                text = getattr(item, "text", "") or ""
                if not text.strip():
                    continue

                mem_type = getattr(item, "type", "memory")
                mem_id = getattr(item, "id", None)
                date_val = getattr(item, "mentioned_at", None) or getattr(item, "occurred_start", None)
                scores = getattr(item, "scores", None)
                score_val = getattr(scores, "final", None) if scores else None

                formatted_memories.append({
                    "id": mem_id,
                    "text": text,
                    "type": mem_type,
                    "date": str(date_val) if date_val else None,
                    "score": score_val,
                    "tags": getattr(item, "tags", []) or [],
                })

                # Categorize for the briefing generator
                category = _categorize_memory(text)
                categorized[category].append(text)

        count = len(formatted_memories)
        has_memories = count > 0

        logger.info(f"Recall finished for '{contact_clean}': found {count} memories.")

        return {
            "success": True,
            "contact": contact_clean,
            "bank_id": target_bank,
            "count": count,
            "has_memories": has_memories,
            "memories": formatted_memories,
            "categorized": categorized,
            "message": (
                f"Successfully retrieved {count} memories for {contact_clean}."
                if has_memories
                else f"No previous memories found for contact '{contact_clean}'."
            ),
        }

    except Exception as e:
        logger.error(f"Error recalling memories from Hindsight: {e}")
        return {
            "success": False,
            "contact": contact_clean,
            "bank_id": target_bank,
            "count": 0,
            "has_memories": False,
            "memories": [],
            "categorized": {
                "discussions": [],
                "commitments": [],
                "deadlines": [],
                "preferences": [],
            },
            "error": str(e),
            "message": f"Failed to recall memories from Hindsight: {e}",
        }
    finally:
        if client is None and hasattr(hindsight, "close"):
            try:
                hindsight.close()
            except Exception:
                pass


# Alias for backward compatibility
recall_memories = recall_contact
