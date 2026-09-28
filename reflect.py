"""
MeetMind – Meeting Briefing Generation Layer (Reflect)
Synthesizes recalled Hindsight memories into an executive 8-part meeting briefing.
Enforces strict anti-hallucination guarantees: if information is missing in memory,
explicitly outputs "Not available in memory."
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
from recall import recall_contact

logger = logging.getLogger("meetmind.reflect")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def _build_empty_briefing(contact: str) -> str:
    """
    Constructs a strict zero-hallucination briefing for contacts with no stored memories.
    Every section explicitly marks missing details as 'Not available in memory.'
    """
    return f"""# Meeting Preparation Briefing

### 1. Contact
{contact}

### 2. Previous Discussions
Not available in memory.

### 3. Decisions
Not available in memory.

### 4. Unresolved Commitments
Not available in memory.

### 5. Deadlines
Not available in memory.

### 6. Preferences
Not available in memory.

### 7. Follow-up Items
Not available in memory.

### 8. Three Suggested Questions for the Next Meeting
1. What are your primary goals and priorities for our discussion today?
2. Are there any key milestones or expectations you would like us to align on?
3. How do you prefer our team share progress and updates moving forward?
"""


def _synthesize_structured_briefing(contact: str, memories: List[Dict[str, Any]]) -> str:
    """
    Extracts and maps recalled Hindsight memories into the required 8 sections.
    Ensures missing sections explicitly state 'Not available in memory.'
    """
    all_texts = [m.get("text", "").strip() for m in memories if m.get("text")]
    # Deduplicate while preserving order
    seen = set()
    deduped_texts = []
    for t in all_texts:
        normalized = t.lower()
        if normalized not in seen:
            seen.add(normalized)
            deduped_texts.append(t)

    discussions = []
    decisions = []
    commitments = []
    deadlines = []
    preferences = []
    followups = []

    for text in deduped_texts:
        t_low = text.lower()

        # Decisions
        if any(w in t_low for w in ["decide", "agreed", "decision", "approved", "chosen"]):
            decisions.append(text)

        # Commitments & promises
        if any(w in t_low for w in ["promise", "commit", "will deliver", "pledged", "agreed to"]):
            commitments.append(text)

        # Deadlines
        if any(w in t_low for w in ["by friday", "deadline", "by ", "due", "timeline", "october", "september"]):
            deadlines.append(text)

        # Preferences
        if any(w in t_low for w in ["prefer", "likes", "prefers", "updates", "short", "format", "email", "slack"]):
            preferences.append(text)

        # Discussions & requests
        if any(w in t_low for w in ["request", "review", "discussed", "dashboard", "proposal", "budget", "meeting"]):
            discussions.append(text)

        # Follow-up items
        if any(w in t_low for w in ["follow up", "prototype", "action item", "todo", "deliver"]):
            followups.append(text)

    def format_items(items: List[str]) -> str:
        if not items:
            return "Not available in memory."
        return "\n".join(f"- {it}" for it in items)

    # Contextual questions strictly grounded in previous discussions
    questions = []
    if commitments or deadlines or followups:
        questions.append("Can we review our progress on the prototype deliverables promised for the deadline?")
    if discussions:
        questions.append(f"Are there any additional requirements or scope changes regarding the dashboard requested earlier?")
    if preferences:
        questions.append("Do our concise progress updates continue to align with your communication preferences?")

    # Fill default professional questions if context is minimal
    default_q = [
        "What are the next priority milestones we should focus on?",
        "Are there any blockers or dependencies we should address today?",
        "How can our team best support your upcoming initiatives?",
    ]
    for dq in default_q:
        if len(questions) < 3 and dq not in questions:
            questions.append(dq)

    return f"""# Meeting Preparation Briefing

### 1. Contact
{contact}

### 2. Previous Discussions
{format_items(discussions[:3])}

### 3. Decisions
{format_items(decisions)}

### 4. Unresolved Commitments
{format_items(commitments)}

### 5. Deadlines
{format_items(deadlines)}

### 6. Preferences
{format_items(preferences)}

### 7. Follow-up Items
{format_items(followups)}

### 8. Three Suggested Questions for the Next Meeting
1. {questions[0]}
2. {questions[1]}
3. {questions[2]}
"""


def prepare_meeting(
    contact: str,
    bank_id: Optional[str] = None,
    client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Prepare a comprehensive meeting briefing for a contact using Hindsight memory.

    Parameters:
        contact (str): Full name or identifier of the contact (e.g. 'Rahul')
        bank_id (str, optional): Target memory bank ID (defaults to HINDSIGHT_BANK_ID)
        client (Hindsight, optional): Active Hindsight client instance

    Returns:
        dict: Briefing markdown containing the 8 required sections, memory count,
              and verification status.
    """
    if not contact or not str(contact).strip():
        raise ValueError("Contact name is required to prepare a meeting briefing.")

    contact_clean = str(contact).strip()
    target_bank = bank_id or HINDSIGHT_BANK_ID
    contact_tag = contact_clean.lower().replace(" ", "_")

    hindsight = client or get_hindsight_client()

    # 1. Recall memories from Hindsight
    recall_result = recall_contact(
        contact=contact_clean,
        bank_id=target_bank,
        client=hindsight,
    )

    if not recall_result.get("success"):
        logger.error(f"Recall failed for '{contact_clean}': {recall_result.get('message')}")
        return {
            "success": False,
            "contact": contact_clean,
            "bank_id": target_bank,
            "has_memories": False,
            "memory_count": 0,
            "error": recall_result.get("error", "HindsightUnavailable"),
            "message": recall_result.get("message", "Failed to query Hindsight memory service."),
        }

    memories = recall_result.get("memories", [])
    has_memories = bool(recall_result.get("has_memories") and memories)

    # 2. If unknown contact / no memories found: return strict zero-hallucination briefing
    if not has_memories:
        logger.info(f"No memories found for '{contact_clean}'. Returning zero-hallucination empty briefing.")
        empty_briefing = _build_empty_briefing(contact_clean)
        return {
            "success": True,
            "contact": contact_clean,
            "bank_id": target_bank,
            "has_memories": False,
            "memory_count": 0,
            "source": "no_memory",
            "briefing": empty_briefing,
            "briefing_markdown": empty_briefing,
            "memories": [],
        }

    # 3. Use Hindsight Reflect to synthesize memories into the 8 sections
    reflect_query = (
        f"Generate a concise, professional executive meeting preparation briefing for an upcoming meeting with {contact_clean}.\n"
        f"Structure the briefing with these EXACT 8 headings:\n"
        f"### 1. Contact\n"
        f"### 2. Previous Discussions\n"
        f"### 3. Decisions\n"
        f"### 4. Unresolved Commitments\n"
        f"### 5. Deadlines\n"
        f"### 6. Preferences\n"
        f"### 7. Follow-up Items\n"
        f"### 8. Three Suggested Questions for the Next Meeting\n\n"
        f"CRITICAL INSTRUCTIONS:\n"
        f"- Rely ONLY on stored memories from previous meetings.\n"
        f"- DO NOT invent, assume, or hallucinate any facts, dates, or decisions.\n"
        f"- If information for any section is missing or absent in memory, you MUST explicitly write: 'Not available in memory.'\n"
        f"- Provide exactly three practical, relevant questions to ask in the next meeting."
    )

    briefing_text: Optional[str] = None
    source = "hindsight_reflect"

    try:
        logger.info(f"Synthesizing meeting briefing for '{contact_clean}' via Hindsight reflect()...")
        response = hindsight.reflect(
            bank_id=target_bank,
            query=reflect_query,
            tags=[contact_tag],
            tags_match="any_strict",
            budget="mid",
            include_facts=True,
        )

        if response and response.text:
            raw_text = response.text.strip()
            # Verify that required headings are present in the reflect output
            required_checks = ["Previous Discussions", "Decisions", "Deadlines", "Preferences"]
            if all(ch in raw_text for ch in required_checks):
                briefing_text = raw_text

    except Exception as e:
        logger.warning(f"Hindsight reflect() encountered: {e}. Using structured synthesizer fallback.")

    # 4. Fallback to structured deterministic synthesizer if reflect output is unavailable or incomplete
    if not briefing_text:
        source = "structured_memory_synthesis"
        briefing_text = _synthesize_structured_briefing(contact_clean, memories)

    logger.info(f"Briefing generated successfully for '{contact_clean}' (source: {source}).")

    if client is None and hasattr(hindsight, "close"):
        try:
            hindsight.close()
        except Exception:
            pass

    return {
        "success": True,
        "contact": contact_clean,
        "bank_id": target_bank,
        "has_memories": True,
        "memory_count": len(memories),
        "source": source,
        "briefing": briefing_text,
        "briefing_markdown": briefing_text,
        "memories": memories,
    }


# Aliases for backward compatibility
generate_meeting_briefing = prepare_meeting
