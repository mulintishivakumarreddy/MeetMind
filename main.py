"""
MeetMind – FastAPI Backend
Provides clean REST API endpoints for:
- POST /meetings           : Store meeting interaction in Hindsight Retain
- GET /prepare/{contact}   : Retrieve Hindsight memories and generate 14-part briefing
- GET /followups/{contact} : Retrieve structured commitments and follow-ups with explicit status
- POST /preferences/user   : Store user meeting preparation style in Hindsight
- GET /preferences/user    : Retrieve learned user meeting style from Hindsight
- GET /health              : Backend & Hindsight connection health check
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

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
    HINDSIGHT_BASE_URL,
    HINDSIGHT_BANK_ID,
    HINDSIGHT_API_KEY,
    HindsightHelper,
)
from retain import remember_meeting, remember_user_preference, parse_and_validate_date
from recall import recall_contact, recall_user_preferences
from reflect import prepare_meeting

logger = logging.getLogger("meetmind.backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Initialize FastAPI application
app = FastAPI(
    title="MeetMind – AI Meeting Preparation Agent",
    description="Backend API powered by Hindsight persistent memory.",
    version="2.0.0",
)

# Optional template engine for UI
templates_dir = _current_dir / "templates"
templates = Jinja2Templates(directory=str(templates_dir)) if templates_dir.exists() else None


# Request Models
class MeetingCreateRequest(BaseModel):
    contact: str = Field(..., min_length=1, description="Contact name, e.g. 'Shiva', 'Rahul'")
    date: Optional[str] = Field(None, description="Meeting date (YYYY-MM-DD or readable date)")
    notes: str = Field(..., min_length=1, description="Meeting discussion, commitments, deadlines, and preferences")


class UserPreferenceRequest(BaseModel):
    preference_type: Optional[str] = Field(default="meeting_style", description="Category: summary_length, priority_order, or communication_style")
    preference_value: Optional[str] = Field(default=None, description="e.g. 'Short / Concise', 'Blockers first', 'Direct'")
    summary_length: Optional[str] = None
    first_priority: Optional[str] = None
    communication_style: Optional[str] = None


# -------------------------------------------------------------
# 1. POST /meetings
# -------------------------------------------------------------
@app.post("/meetings", status_code=status.HTTP_201_CREATED)
def create_meeting(payload: MeetingCreateRequest):
    """
    Accept contact, date, and meeting notes, then store into Hindsight Retain.
    """
    contact = (payload.contact or "").strip()
    notes = (payload.notes or "").strip()
    raw_date = (payload.date or "").strip()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact name cannot be empty.",
        )
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting notes cannot be empty.",
        )

    # Validate date if provided
    is_valid_date, formatted_date, _ = parse_and_validate_date(raw_date)
    if not is_valid_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: '{payload.date}'. Please provide a valid date string (e.g. YYYY-MM-DD).",
        )

    result = remember_meeting(
        contact=contact,
        date=formatted_date,
        notes=notes,
    )

    if not result.get("success"):
        if result.get("error") == "ValidationError":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Validation error occurred."),
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result.get("message", "Hindsight memory service is currently unavailable."),
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "success",
            "message": result.get("message"),
            "contact": result.get("contact"),
            "date": result.get("date"),
            "bank_id": result.get("bank_id"),
            "items_count": result.get("items_count", 1),
            "dimensions": result.get("dimensions"),
        },
    )


# -------------------------------------------------------------
# 2. GET /prepare & GET /prepare/{contact}
# -------------------------------------------------------------
@app.get("/prepare", status_code=status.HTTP_400_BAD_REQUEST)
@app.get("/prepare/", status_code=status.HTTP_400_BAD_REQUEST)
def prepare_empty_contact():
    """Handle missing contact path parameter."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Contact name parameter is required. Usage: /prepare/{contact}",
    )


@app.get("/prepare/{contact}", status_code=status.HTTP_200_OK)
def get_meeting_briefing(contact: str):
    """
    Retrieve relevant Hindsight memories and generate a personalized 14-part meeting briefing.
    Includes memory timeline, commitment tracking, and 'What MeetMind Learned' longitudinal intelligence.
    """
    contact_clean = contact.strip()
    if not contact_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact name parameter cannot be empty.",
        )

    result = prepare_meeting(contact=contact_clean)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result.get("message") or result.get("error", "Failed to generate meeting briefing."),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "contact": result.get("contact"),
            "has_memories": result.get("has_memories", False),
            "memory_count": result.get("memory_count", 0),
            "source": result.get("source"),
            "briefing": result.get("briefing"),
            "timeline": result.get("timeline", []),
            "commitments": result.get("commitments", {}),
            "learned_summary": result.get("learned_summary", {}),
            "user_style": result.get("user_style", {}),
            "memories": result.get("memories", []),
        },
    )


# -------------------------------------------------------------
# 3. GET /followups/{contact}
# -------------------------------------------------------------
@app.get("/followups/{contact}", status_code=status.HTTP_200_OK)
def get_contact_followups(contact: str):
    """
    Retrieve longitudinal commitment & follow-up tracking for a specific contact.
    Categorizes items into Completed, Pending, and Missed / Overdue.
    """
    contact_clean = contact.strip()
    if not contact_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact name parameter cannot be empty.",
        )

    recall_res = recall_contact(contact=contact_clean)
    if not recall_res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=recall_res.get("message", "Failed to retrieve follow-ups from Hindsight."),
        )

    commitments = recall_res.get("commitments", {})
    summary = {
        "total": len(commitments.get("all_commitments", [])),
        "pending": len(commitments.get("pending", [])),
        "completed": len(commitments.get("completed", [])),
        "missed": len(commitments.get("missed", [])),
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "contact": contact_clean,
            "has_commitments": len(commitments.get("all_commitments", [])) > 0,
            "commitments": commitments,
            "summary": summary,
        },
    )


# -------------------------------------------------------------
# 4. POST /preferences/user & GET /preferences/user
# -------------------------------------------------------------
@app.post("/preferences/user", status_code=status.HTTP_201_CREATED)
def set_user_preference(payload: UserPreferenceRequest):
    """
    Store user meeting preparation and interaction style into Hindsight memory.
    """
    pref_val = payload.preference_value
    if not pref_val:
        parts = []
        if payload.summary_length:
            parts.append(f"Summary length: {payload.summary_length}")
        if payload.first_priority:
            parts.append(f"Priority order: {payload.first_priority}")
        if payload.communication_style:
            parts.append(f"Communication tone: {payload.communication_style}")
        pref_val = ". ".join(parts) if parts else "Short / Concise. Blockers First."

    res = remember_user_preference(
        preference_type=payload.preference_type or "meeting_style",
        preference_value=pref_val,
        source="My Meeting Preferences UI",
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=res.get("message", "Failed to store user preference in Hindsight."),
        )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"status": "success", **res})


@app.get("/preferences/user", status_code=status.HTTP_200_OK)
def get_user_preferences():
    """
    Retrieve current learned user meeting preparation style from Hindsight.
    """
    res = recall_user_preferences()
    return JSONResponse(status_code=status.HTTP_200_OK, content=res)


# -------------------------------------------------------------
# 5. GET /health
# -------------------------------------------------------------
@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint reporting backend and Hindsight connection status.
    No API keys are exposed.
    """
    reachability = HindsightHelper.check_reachability()
    is_healthy = bool(reachability.get("reachable"))
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_healthy else "degraded",
            "service": "MeetMind Backend",
            "hindsight_bank": HINDSIGHT_BANK_ID,
            "hindsight_connected": is_healthy,
            "hindsight_api_version": reachability.get("api_version"),
            "error": reachability.get("error") if not is_healthy else None,
        },
    )


# -------------------------------------------------------------
# Optional UI Route (GET /)
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def root_dashboard(request: Request):
    """Render dashboard UI if template exists."""
    if templates:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "bank_id": HINDSIGHT_BANK_ID,
                "hindsight_base_url": HINDSIGHT_BASE_URL,
                "has_hindsight_key": bool(HINDSIGHT_API_KEY),
            },
        )
    return HTMLResponse("<h1>MeetMind Backend API Online</h1><p>Visit /docs for API documentation.</p>")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    print(f"Starting MeetMind FastAPI backend on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
