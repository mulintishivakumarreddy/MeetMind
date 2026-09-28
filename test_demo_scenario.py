"""
MeetMind – Hackathon End-to-End Demo Scenario Test
Executes the complete multi-interaction demo scenario:
1. Ingests 3 distinct meetings for 'Rahul' via the API.
2. Ingests 1 distinct meeting for 'Priya' via the API.
3. Prepares Rahul's briefing and verifies multi-interaction memory synthesis.
4. Prepares Priya's briefing and verifies strict memory isolation.
5. Prepares UnknownPerson's briefing and verifies zero hallucination.
6. Verifies that the UI serves the exact demo buttons, forms, and cards.
"""

import sys
import logging
from typing import Dict, Any
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("demo_scenario")

from main import app

client = TestClient(app)

# -------------------------------------------------------------
# Test Data
# -------------------------------------------------------------
RAHUL_MEETINGS = [
    {
        "contact": "Rahul",
        "date": "2026-09-10",
        "notes": "Rahul requested a sales dashboard. He wants weekly progress updates.",
    },
    {
        "contact": "Rahul",
        "date": "2026-09-17",
        "notes": "Rahul reviewed the dashboard prototype. He requested export functionality. We promised the updated version by Friday.",
    },
    {
        "contact": "Rahul",
        "date": "2026-09-24",
        "notes": "Rahul said the dashboard should remain simple. He prefers short explanations.",
    },
]

PRIYA_MEETING = {
    "contact": "Priya",
    "date": "2026-09-15",
    "notes": "Priya requested a redesign of the mobile app onboarding flow. We committed to deliver the design mockups by October 5th. Priya prefers async Slack updates and Figma comments over scheduled video calls.",
}


def run_demo():
    print("\n" + "=" * 75)
    print("🧠 MEETMIND – HACKATHON COMPLETE END-TO-END DEMO SCENARIO")
    print("=" * 75)

    # ---------------------------------------------------------
    # Step 0: Verify Health & UI
    # ---------------------------------------------------------
    print("\n--- STEP 0: Verifying Health and UI Dashboard ---")
    health_res = client.get("/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    health_data = health_res.json()
    print(f"✅ Backend Health: {health_data.get('status')} | Bank: {health_data.get('hindsight_bank')}")

    ui_res = client.get("/")
    assert ui_res.status_code == 200, f"UI route failed: {ui_res.text}"
    ui_html = ui_res.text
    # Verify critical UI components
    for keyword in [
        "MeetMind",
        "Save Meeting Memory",
        "Prepare for a Meeting",
        "Meeting Briefing",
        "Hindsight Memory Used",
        "fillRahulM1",
        "fillRahulM2",
        "fillRahulM3",
        "fillPriyaM1",
        "runAutoDemo",
    ]:
        assert keyword in ui_html, f"Missing UI keyword: {keyword}"
    print("✅ Web UI Loaded with all interactive demo presets and controls.")

    # ---------------------------------------------------------
    # Step 1: Ingest 3 Meetings for Rahul
    # ---------------------------------------------------------
    print("\n--- STEP 1: Ingesting 3 Sequential Meetings for 'Rahul' via POST /meetings ---")
    for i, meeting in enumerate(RAHUL_MEETINGS, 1):
        print(f"\n[Meeting {i}] Storing interaction for Rahul ({meeting['date']})...")
        print(f"  Notes: \"{meeting['notes']}\"")
        res = client.post("/meetings", json=meeting)
        assert res.status_code == 201, f"Failed storing meeting {i}: {res.text}"
        data = res.json()
        assert data.get("status") == "success"
        print(f"  ✅ Retained in Hindsight bank '{data.get('bank_id')}'.")

    # ---------------------------------------------------------
    # Step 2: Ingest 1 Meeting for Priya (Isolation Verification)
    # ---------------------------------------------------------
    print("\n--- STEP 2: Ingesting Meeting for 'Priya' via POST /meetings ---")
    print(f"  Notes: \"{PRIYA_MEETING['notes']}\"")
    p_res = client.post("/meetings", json=PRIYA_MEETING)
    assert p_res.status_code == 201, f"Failed storing Priya's meeting: {p_res.text}"
    p_data = p_res.json()
    assert p_data.get("status") == "success"
    print(f"  ✅ Retained in Hindsight bank '{p_data.get('bank_id')}'.")

    # ---------------------------------------------------------
    # Step 3: Prepare Briefing for Rahul (Multi-Meeting Synthesis)
    # ---------------------------------------------------------
    print("\n--- STEP 3: Preparing Briefing for 'Rahul' (GET /prepare/Rahul) ---")
    r_prep = client.get("/prepare/Rahul")
    assert r_prep.status_code == 200, f"Prepare Rahul failed: {r_prep.text}"
    r_briefing_data = r_prep.json()

    assert r_briefing_data.get("status") == "success"
    assert r_briefing_data.get("has_memories") is True
    assert r_briefing_data.get("memory_count", 0) > 0

    briefing_text = r_briefing_data.get("briefing", "")
    print("\n" + "-" * 50)
    print("📋 RAHUL'S SYNTHESIZED EXECUTIVE BRIEFING:")
    print("-" * 50)
    print(briefing_text)
    print("-" * 50)

    # Multi-interaction memory checks
    b_low = briefing_text.lower()

    # Meeting 1 verification: Sales dashboard
    has_dashboard = "dashboard" in b_low or "sales" in b_low
    print(f"  ✓ Remembers Meeting 1 (Sales Dashboard): {has_dashboard}")
    assert has_dashboard, "Briefing failed to remember Meeting 1 sales dashboard."

    # Meeting 2 verification: Prototype / Friday / Export
    has_prototype_or_friday = any(k in b_low for k in ["prototype", "friday", "export", "updated version"])
    print(f"  ✓ Remembers Meeting 2 (Prototype / Friday / Export): {has_prototype_or_friday}")
    assert has_prototype_or_friday, "Briefing failed to remember Meeting 2 prototype/deadline."

    # Meeting 3 verification: Simplicity / Short explanations / Progress
    has_preferences = any(k in b_low for k in ["simple", "short", "progress", "update", "explanation"])
    print(f"  ✓ Remembers Meeting 3 (Simplicity & Short Explanations): {has_preferences}")
    assert has_preferences, "Briefing failed to remember Meeting 3 preferences."

    # Verify NO cross-contamination from Priya
    has_priya_bleed = any(k in b_low for k in ["priya", "onboarding", "figma", "october 5"])
    print(f"  ✓ Memory Isolation (No Priya bleed into Rahul): {not has_priya_bleed}")
    assert not has_priya_bleed, "Contamination detected: Priya's notes appeared in Rahul's briefing!"

    # ---------------------------------------------------------
    # Step 4: Prepare Briefing for Priya (Isolation Verification)
    # ---------------------------------------------------------
    print("\n--- STEP 4: Preparing Briefing for 'Priya' (GET /prepare/Priya) ---")
    p_prep = client.get("/prepare/Priya")
    assert p_prep.status_code == 200, f"Prepare Priya failed: {p_prep.text}"
    p_briefing_data = p_prep.json()

    assert p_briefing_data.get("status") == "success"
    assert p_briefing_data.get("has_memories") is True
    p_text = p_briefing_data.get("briefing", "")
    p_low = p_text.lower()

    print("\n" + "-" * 50)
    print("📋 PRIYA'S SYNTHESIZED EXECUTIVE BRIEFING:")
    print("-" * 50)
    print(p_text)
    print("-" * 50)

    # Priya memory checks
    has_priya_topic = any(k in p_low for k in ["mobile", "onboarding", "mockup", "october", "slack", "figma"])
    print(f"  ✓ Remembers Priya's Topics (Mobile Onboarding / Figma / Oct 5): {has_priya_topic}")
    assert has_priya_topic, "Briefing failed to remember Priya's specific topics."

    # Verify NO cross-contamination from Rahul
    has_rahul_bleed = any(k in p_low for k in ["rahul", "sales dashboard", "friday"])
    print(f"  ✓ Memory Isolation (No Rahul bleed into Priya): {not has_rahul_bleed}")
    assert not has_rahul_bleed, "Contamination detected: Rahul's notes appeared in Priya's briefing!"

    # ---------------------------------------------------------
    # Step 5: Test Unknown Person (Zero Hallucination Verification)
    # ---------------------------------------------------------
    print("\n--- STEP 5: Testing Unknown Contact 'UnknownPerson' (GET /prepare/UnknownPerson) ---")
    u_prep = client.get("/prepare/UnknownPerson")
    assert u_prep.status_code == 200, f"Prepare UnknownPerson failed: {u_prep.text}"
    u_briefing_data = u_prep.json()

    assert u_briefing_data.get("status") == "success"
    assert u_briefing_data.get("has_memories") is False
    assert u_briefing_data.get("memory_count") == 0
    u_text = u_briefing_data.get("briefing", "")

    print(f"  Memory Status: has_memories={u_briefing_data.get('has_memories')}")
    print(f"  Explicit text check: 'Not available in memory.' count = {u_text.count('Not available in memory.')}")
    assert "Not available in memory." in u_text, "Unknown person briefing did not include 'Not available in memory.'"
    assert not any(k in u_text.lower() for k in ["rahul", "priya", "sales dashboard", "figma", "prototype"]), \
        "Unknown contact leaked facts from other contacts!"
    print("  ✓ Zero Hallucination Confirmed: No invented facts or cross-contamination.")

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    print("\n" + "=" * 75)
    print("🎉 ALL HACKATHON DEMO SCENARIO CHECKS PASSED SUCCESSFULLY!")
    print("=" * 75)
    print("Summary of verified capabilities:")
    print("1. Multi-interaction recall: Stored 3 sequential meetings for Rahul; synthesized into 1 coherent briefing.")
    print("2. Memory cross-isolation: Rahul and Priya maintain completely isolated memory partitions.")
    print("3. Zero-hallucination guardrail: UnknownPerson returns explicit 'Not available in memory.' with 0 memories.")
    print("4. Full-stack integration: Web UI, FastAPI backend, and Hindsight Cloud fully operational.")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_demo()
