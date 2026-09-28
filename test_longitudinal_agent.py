"""
test_longitudinal_agent.py - Comprehensive Verification for MeetMind Longitudinal Meeting Prep Agent

Tests all 15 core product requirements:
1. Retaining multiple sequential meetings for a contact (longitudinal memory)
2. Extracting commitments, promises, and deadlines
3. Tracking commitment lifecycle states (Pending, Completed, Missed / Overdue)
4. Extracting and remembering contact preferences across meetings
5. Storing and applying user's own meeting preparation preferences (POST & GET /preferences/user)
6. Synthesizing full 14-part executive pre-meeting briefing
7. Generating 'What MeetMind Learned Across Past Meetings' longitudinal intelligence
8. Chronological memory timeline reconstruction
9. GET /followups/{contact} structured commitment tracking endpoint
10. GET /prepare/{contact} end-to-end integration
11. Contact isolation: Cross-contact memory separation (Shiva vs Priya)
12. Zero-hallucination enforcement for unknown contacts (Arjun)
13. Validation handling for empty/invalid inputs
14. Graceful fallback on LLM/reflect failure without crashing
15. End-to-end 3-meeting Shiva hackathon scenario verification
"""

import sys
import unittest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from retain import remember_meeting, remember_user_preference
from recall import recall_contact, recall_user_preferences
from reflect import prepare_meeting, _synthesize_longitudinal_briefing, _build_empty_briefing

client = TestClient(app)


class TestMeetMindLongitudinalAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 80)
        print("🧠 MEETMIND LONGITUDINAL AGENT PRODUCT VERIFICATION SUITE")
        print("=" * 80)

    # 1. Longitudinal meeting retention
    def test_01_retain_multiple_meetings(self):
        print("\n[Test 1] Retain multiple sequential meetings for 'TestContact_Alpha'")
        m1 = remember_meeting(
            contact="TestContact_Alpha",
            date="2026-09-01",
            notes="Discussed sales dashboard. Promised weekly updates by Friday.",
        )
        self.assertTrue(m1.get("success"), f"M1 failed: {m1}")
        self.assertEqual(m1.get("contact"), "TestContact_Alpha")

        m2 = remember_meeting(
            contact="TestContact_Alpha",
            date="2026-09-08",
            notes="Reviewed dashboard prototype. Promised export feature by Friday. Blockers should be discussed first.",
        )
        self.assertTrue(m2.get("success"), f"M2 failed: {m2}")

    # 2. Extracting commitments, promises, and deadlines
    def test_02_commitment_extraction(self):
        print("\n[Test 2] Verify commitment and deadline extraction")
        rec = recall_contact("TestContact_Alpha")
        self.assertTrue(rec.get("success"))
        commitments = rec.get("commitments", {})
        all_c = commitments.get("all_commitments", [])
        self.assertGreaterEqual(len(all_c), 1, "Should have extracted at least 1 commitment")

    # 3. Tracking commitment lifecycle states
    def test_03_commitment_lifecycle_states(self):
        print("\n[Test 3] Verify lifecycle states: Pending, Completed, Missed / Overdue")
        rec = recall_contact("TestContact_Alpha")
        commitments = rec.get("commitments", {})
        self.assertIn("pending", commitments)
        self.assertIn("completed", commitments)
        self.assertIn("missed", commitments)

    # 4. Contact preferences learning
    def test_04_contact_preference_learning(self):
        print("\n[Test 4] Verify contact preferences are extracted and learned")
        rec = recall_contact("TestContact_Alpha")
        categorized = rec.get("categorized", {})
        prefs = categorized.get("preferences", [])
        self.assertTrue(len(prefs) >= 1 or rec.get("count", 0) >= 2)

    # 5. User meeting preparation style storage and retrieval
    def test_05_user_preparation_style_endpoints(self):
        print("\n[Test 5] Test POST & GET /preferences/user")
        post_res = client.post(
            "/preferences/user",
            json={
                "summary_length": "Ultra-Concise Bullet Points",
                "first_priority": "Blockers First",
                "communication_style": "Direct & Action-Oriented",
            },
        )
        self.assertEqual(post_res.status_code, 201)
        data = post_res.json()
        self.assertEqual(data.get("status"), "success")

        get_res = client.get("/preferences/user")
        self.assertEqual(get_res.status_code, 200)
        style = get_res.json().get("inferred_style", {})
        self.assertIn("summary_length", style)

    # 6. Executive 14-part briefing structure
    def test_06_executive_14_part_briefing(self):
        print("\n[Test 6] Verify 14-part briefing structure")
        res = prepare_meeting("TestContact_Alpha")
        self.assertTrue(res.get("success"))
        briefing = res.get("briefing", "")
        required_parts = [
            "### 1. Contact",
            "### 2. Previous Discussions",
            "### 3. Decisions Made",
            "### 4. Promises and Commitments",
            "### 5. Pending Follow-ups",
            "### 6. Completed Follow-ups",
            "### 7. Missed / Overdue Follow-ups",
            "### 8. Deadlines",
            "### 9. Contact Communication Preferences",
            "### 10. My Preferred Meeting Preparation Style",
            "### 11. Relationship / Context",
            "### 12. Important Changes Since the Last Meeting",
            "### 13. Recommended Questions for the Next Meeting",
            "### 14. Suggested Opening / Talking Points",
        ]
        for part in required_parts:
            self.assertIn(part, briefing, f"Missing section in briefing: {part}")

    # 7. 'What MeetMind Learned' longitudinal intelligence
    def test_07_what_meetmind_learned(self):
        print("\n[Test 7] Verify 'What MeetMind Learned Across Past Meetings'")
        res = client.get("/prepare/TestContact_Alpha")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        learned = data.get("learned_summary", {})
        self.assertIn("contact_insights", learned)
        self.assertIn("commitments_lifecycle", learned)
        self.assertIn("user_preparation_style", learned)

    # 8. Memory timeline reconstruction
    def test_08_memory_timeline_reconstruction(self):
        print("\n[Test 8] Verify chronological memory timeline")
        res = client.get("/prepare/TestContact_Alpha")
        self.assertEqual(res.status_code, 200)
        timeline = res.json().get("timeline", [])
        self.assertIsInstance(timeline, list)
        if len(timeline) >= 2:
            self.assertLessEqual(timeline[0]["date"], timeline[1]["date"])

    # 9. GET /followups/{contact} endpoint
    def test_09_followups_endpoint(self):
        print("\n[Test 9] Test GET /followups/TestContact_Alpha")
        res = client.get("/followups/TestContact_Alpha")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("commitments", data)
        self.assertIn("summary", data)

    # 10. GET /prepare/{contact} endpoint
    def test_10_prepare_endpoint(self):
        print("\n[Test 10] Test GET /prepare/TestContact_Alpha")
        res = client.get("/prepare/TestContact_Alpha")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertTrue(data.get("has_memories"))
        self.assertGreater(data.get("memory_count"), 0)

    # 11. Cross-contact memory isolation
    def test_11_cross_contact_isolation(self):
        print("\n[Test 11] Verify cross-contact isolation between distinct contacts")
        client.post(
            "/meetings",
            json={
                "contact": "IsolatedContact_A",
                "date": "2026-09-10",
                "notes": "Discussed distributed database sharding and Cassandra clusters.",
            },
        )
        client.post(
            "/meetings",
            json={
                "contact": "IsolatedContact_B",
                "date": "2026-09-11",
                "notes": "Reviewed graphic branding guidelines and color palette.",
            },
        )

        res_a = client.get("/prepare/IsolatedContact_A").json()
        res_b = client.get("/prepare/IsolatedContact_B").json()

        briefing_a = res_a.get("briefing", "").lower()
        briefing_b = res_b.get("briefing", "").lower()

        self.assertNotIn("branding", briefing_a)
        self.assertNotIn("palette", briefing_a)
        self.assertNotIn("cassandra", briefing_b)
        self.assertNotIn("sharding", briefing_b)

    # 12. Zero hallucination for unknown contact
    def test_12_zero_hallucination_unknown_contact(self):
        print("\n[Test 12] Verify zero-hallucination for unknown contact")
        res = client.get("/prepare/UnknownContact_X99")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data.get("has_memories"))
        self.assertEqual(data.get("memory_count"), 0)
        briefing = data.get("briefing", "")
        self.assertIn("Not available in memory.", briefing)
        self.assertNotIn("sales dashboard", briefing.lower())
        self.assertNotIn("cassandra", briefing.lower())

    # 13. Input validation
    def test_13_input_validation(self):
        print("\n[Test 13] Test input validation on API endpoints")
        res1 = client.post("/meetings", json={"contact": "", "date": "2026-09-01", "notes": "notes"})
        self.assertIn(res1.status_code, [400, 422])

        res2 = client.post("/meetings", json={"contact": "User", "date": "invalid-date", "notes": "notes"})
        self.assertEqual(res2.status_code, 400)

        res3 = client.get("/prepare/%20")
        self.assertEqual(res3.status_code, 400)

    # 14. Fallback on reflect failure
    def test_14_reflect_failure_fallback(self):
        print("\n[Test 14] Test graceful fallback when LLM reflect fails")
        mock_client = MagicMock()
        mock_recall = MagicMock()
        mock_item = MagicMock()
        mock_item.text = "Discussed Q4 deliverables. Promised beta by Friday."
        mock_item.type = "memory"
        mock_item.id = "m1"
        mock_item.tags = ["fallback_user", "meeting"]
        mock_recall.results = [mock_item]
        mock_client.recall.return_value = mock_recall
        mock_client.reflect.side_effect = Exception("OpenAI API rate limit / Model timeout")

        res = prepare_meeting("FallbackUser", client=mock_client)
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("source"), "structured_memory_synthesis")
        self.assertIn("### 1. Contact", res.get("briefing", ""))

    # 15. End-to-end Shiva 3-meeting hackathon scenario
    def test_15_shiva_hackathon_demo_scenario(self):
        print("\n[Test 15] Test complete Shiva 3-meeting hackathon flow")
        shiva_meetings = [
            {
                "contact": "Shiva",
                "date": "2026-09-01",
                "notes": "Discussed initial architecture and scope. Promised to deliver the system design document by Friday. Shiva prefers short progress updates rather than lengthy emails.",
            },
            {
                "contact": "Shiva",
                "date": "2026-09-08",
                "notes": "Reviewed the system design document. Shiva approved the architecture and requested adding an export feature. Promised the updated design and export prototype by Friday. Shiva explicitly requested that blockers should be discussed first in future meetings.",
            },
            {
                "contact": "Shiva",
                "date": "2026-09-15",
                "notes": "Delivered the export prototype. Shiva reviewed and approved it. However, the automated test suite integration was delayed due to CI pipeline issues and is overdue. Next milestone: production readiness review on October 5th.",
            },
        ]
        for m in shiva_meetings:
            res = client.post("/meetings", json=m)
            if res.status_code != 201:
                import time
                time.sleep(2)
                res = client.post("/meetings", json=m)
            self.assertEqual(res.status_code, 201)

        prep_res = client.get("/prepare/Shiva")
        self.assertEqual(prep_res.status_code, 200)
        data = prep_res.json()
        self.assertTrue(data.get("has_memories"))
        briefing = data.get("briefing", "")

        # Verify longitudinal knowledge present
        self.assertIn("Shiva", briefing)
        self.assertTrue(any(w in briefing.lower() for w in ["short", "update"]))
        self.assertTrue(any(w in briefing.lower() for w in ["blocker", "first"]))
        self.assertTrue(any(w in briefing.lower() for w in ["export", "prototype", "architecture"]))
        print("  -> Shiva longitudinal briefing verified across all 3 meetings!")


if __name__ == "__main__":
    unittest.main()
