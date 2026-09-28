# MeetMind
AI Meeting Preparation Agent

> **MeetMind** is an executive meeting preparation agent powered by **Hindsight**, the biomimetic long-term memory engine. It eliminates lost context between meetings by retaining discussions, commitments, deadlines, and preferences across interactions, synthesizing concise, hallucination-free executive briefings before every meeting.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Hindsight](https://img.shields.io/badge/Memory-Hindsight-6C5CE7?style=flat)](https://hindsight.vectorize.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Project Screenshots

![MeetMind Executive Dashboard](docs/screenshots/dashboard.png)
*Figure 1: MeetMind Dashboard featuring the 4-stage processing pipeline, Before & After memory comparison, and quick-demo controls.*

| Meeting Retention Flow | Executive Briefing & Memory Status |
|:---:|:---:|
| ![Retain Flow](docs/screenshots/retain_flow.png) | ![Briefing Output](docs/screenshots/briefing_result.png) |
| *Figure 2: Retain pipeline storing structured notes into Hindsight* | *Figure 3: 8-part synthesized briefing with grounded memory trace* |

---

## Demo Video & Live Demo

- 📺 **Demo Video**: [Watch the 60-Second MeetMind Hackathon Walkthrough](https://youtu.be/YOUR_DEMO_VIDEO_HERE) *(Placeholder: Replace with YouTube / Loom link)*
- 🌐 **Live Demo**: [https://meetmind-demo.onrender.com](https://meetmind-demo.onrender.com) *(Placeholder: Replace with deployed URL)*
- 📖 **Interactive Swagger API Docs**: `http://localhost:8000/docs`

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [How Hindsight Is Used](#how-hindsight-is-used)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [Demo Scenario](#demo-scenario)
- [Testing](#testing)
- [Future Improvements](#future-improvements)

---

## Problem

Modern knowledge workers and executives spend upwards of 20 hours each week in meetings. However, the connective tissue between these meetings is consistently lost:

1. **Context Fragmentation**: Decisions agreed upon, commitments made in passing, deadlines promised, and individual stakeholder preferences become buried across fragmented personal notebooks, Slack threads, or email chains.
2. **Passive Note-Taking Silos**: Traditional productivity tools (Notion, Google Docs, Apple Notes) are passive text repositories. They do not retain a dynamic mental model of the person you are meeting with, nor do they proactively prepare you for subsequent conversations.
3. **Stateless LLM Amnesia**: Standard LLM chatbots suffer from context window amnesia. Pasting long transcripts or historical logs into prompt windows is expensive, unscalable, prone to attention degradation, and vulnerable to hallucination when context is missing.
4. **Broken Continuity & Lost Trust**: Walking into a meeting having forgotten a pledge made two weeks ago damages professional relationships and wastes the first 10 minutes of every call recalling past progress.

---

## Solution

**MeetMind** transforms meeting management from passive note-taking into an active, intelligent preparation partner:

- **Persistent Stakeholder Memory**: MeetMind builds a cumulative, evolving memory profile for every colleague, client, and stakeholder using Hindsight's biomimetic memory banks.
- **Active Context Synthesis**: Before your next call, MeetMind queries your Hindsight memory bank to instantly surface unresolved commitments, past decisions, upcoming deadlines, and nuances in stakeholder communication style.
- **Strict Grounding & Zero Hallucination**: If a piece of information was never discussed or stored, MeetMind explicitly flags it as *"Not available in memory."* rather than inventing facts.
- **60-Second Executive Advantage**: Instead of spending 15 minutes digging through historical notes before a call, executives receive an instant, actionable 8-part briefing in under 3 seconds.

---

## How Hindsight Is Used

MeetMind leverages the complete biomimetic cognitive cycle of the **Hindsight API**:

```
 ┌────────────────┐       ┌─────────────────┐       ┌──────────────────┐
 │     RETAIN     │  ──▶  │     RECALL      │  ──▶  │     REFLECT      │
 │  (retain.py)   │       │   (recall.py)   │       │   (reflect.py)   │
 └────────────────┘       └─────────────────┘       └──────────────────┘
   Extracts & Stores        Hybrid Semantic           Synthesizes multi-
   structured memory        & entity retrieval        meeting intelligence
   into Hindsight bank      for target contact        into 8-part briefing
```

### 1. Retain (`retain.py`)
- **What it does**: Translates unstructured meeting input into structured, durable memory units.
- **How it works**: When a meeting note is submitted, MeetMind parses the contact name, meeting date, key discussion points, commitments made, deadlines, and personal preferences into a canonical memory payload.
- **Hindsight Integration**: Calls `hindsight_client.retain()` against the configured `bank_id`, tagging memories with `contact:<name>` and indexing entities into the biomimetic graph.

### 2. Recall (`recall.py`)
- **What it does**: Fetches precision context tailored to the target contact.
- **How it works**: Queries Hindsight for all retained memories relevant to a contact across past interactions.
- **Hindsight Integration**: Leverages Hindsight's multi-strategy search (combining semantic vector embeddings, BM25 keyword matching, entity graph traversal, and temporal recency decay) to return an ordered set of memory fragments without noise.

### 3. Reflect (`reflect.py`)
- **What it does**: Generates grounded, longitudinal intelligence from recalled memories across all previous meetings.
- **How it works**: Ingests all recalled memory fragments, parses commitment lifecycles (tracking promises that became completed, pending, or overdue/missed), incorporates the user's learned preparation style, and reflects across time.
- **Hindsight Integration**: Uses Hindsight Reflect to compile a comprehensive **14-part executive briefing**:
  1. **Contact Name**: Target stakeholder identity.
  2. **Previous Discussions**: Synthesized themes across historical meetings.
  3. **Decisions Made**: Cumulative decisions agreed upon over time.
  4. **Promises and Commitments**: Explicit ownership, responsible party, and deadlines.
  5. **Pending Follow-ups**: Unfinished action items requiring attention.
  6. **Completed Follow-ups**: Items verified as delivered or resolved.
  7. **Missed / Overdue Follow-ups**: Promises that passed their agreed deadline without delivery.
  8. **Deadlines & Milestones**: Upcoming target delivery dates.
  9. **Contact Communication Preferences**: Stakeholder style (e.g. blockers first, concise updates, async Slack).
  10. **My Preferred Meeting Preparation Style**: Learned user briefing style (summary length, priority focus, tone).
  11. **Relationship / Context**: Cumulative collaboration profile and interaction history.
  12. **Important Changes Since the Last Meeting**: Overdue items, resolved milestones, and blockers.
  13. **Recommended Questions for the Next Meeting**: 3 strategic, context-grounded questions.
  14. **Suggested Opening / Talking Points**: Action-oriented conversation starters.

### 4. Commitment Lifecycle Tracking
- Automatically tracks promises across meetings:
  - **`Pending`**: A promise made whose deadline has not yet arrived or status is ongoing.
  - **`Completed`**: A deliverable confirmed as reviewed, delivered, or accepted in a subsequent meeting.
  - **`Missed / Overdue`**: A promise where the deadline passed without delivery or was explicitly flagged as overdue.

### 5. Persistent Memory & User Style Learning
- **Persistent Memory**: Unlike stateless LLM chatbots where history vanishes between sessions, Hindsight memory banks persist indefinitely. Meeting 5 seamlessly recalls context established in Meeting 1.
- **User Style Learning (`POST & GET /preferences/user`)**: MeetMind learns your personal briefing preferences (e.g. "Ultra-concise bullet points", "Blockers first", "Direct & action-oriented") and adapts future briefings automatically.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Executive Browser UI                            │
│    (HTML5, Vanilla JS, Responsive CSS, Memory Timeline, Status Badges) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼  REST API (JSON over HTTP)
┌────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Backend                              │
│              (main.py - CORS, Validation, Async Handlers)              │
│                                                                        │
│   POST /meetings                  GET /prepare/{contact}               │
│   GET /followups/{contact}        POST & GET /preferences/user         │
│   GET /health                     GET /                                │
└─────────┬───────────────────────────────┬──────────────────────────────┘
          │                               │
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│    retain.py     │            │    recall.py     │
│ (Memory Ingest)  │            │ (Hybrid Search & │
└─────────┬────────┘            │  Commitment FSM) │
          │                     └─────────┬────────┘
          │                               │
          │                               ▼
          │                     ┌──────────────────┐
          │                     │    reflect.py    │
          │                     │ (14-Part Briefing│
          │                     │   & Synthesis)   │
          │                     └─────────┬────────┘
          │                               │
          ▼                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Hindsight Memory Cloud                          │
│     (Biomimetic Memory Bank: Vectors, Entity Graphs, Temporal Decay)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Features

- **Longitudinal Meeting Intelligence**: Tracks context across days, weeks, or months of sequential meetings.
- **Cross-Meeting Commitment Tracking**: Categorizes every promise into `Pending`, `Completed`, or `Missed / Overdue`.
- **Learned User Preparation Style**: Persistent memory customization for summary length, priority order, and communication tone.
- **14-Part Executive Briefing**: In-depth, grounded pre-meeting briefing with zero fabricated facts.
- **What MeetMind Learned Card**: Highlights cumulative stakeholder insights and commitment lifecycle status.
- **Chronological Memory Timeline**: Visual timeline of all prior interactions with exact dates and notes.
- **Visible 4-Step Processing Pipeline**: Live pipeline stepper illustrating Retain ➔ Hindsight ➔ Recall ➔ AI Briefing.
- **Memory Status Indicator**: Clear `✓ Hindsight Memory Used` badge confirming live memory grounding.
- **Strict Contact Memory Isolation**: Shiva, Rahul, and Priya maintain 100% isolated memory spaces.
- **Strict Zero Hallucination**: Unknown contacts return an explicit `Not available in memory.` notice.

---

## Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend** | HTML5, Vanilla JavaScript, Modern CSS | Lightweight, 0ms build time, zero dependency vulnerabilities, universal browser compatibility. |
| **Backend API** | FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous Python REST framework with automatic schema validation. |
| **Memory Engine** | Hindsight SDK (`hindsight-client`) | Biomimetic long-term memory engine with native Retain, Recall, and Reflect capabilities. |
| **Configuration** | `python-dotenv`, `python-dateutil` | Secure, twelve-factor app configuration and robust ISO timestamp handling. |
| **Testing** | Standard Library + Pytest-compatible suites | Comprehensive 12-scenario enterprise QA suite and connectivity diagnostics. |

---

## Setup Instructions

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed.
- A Hindsight API Key (from [Hindsight Cloud Console](https://ui.hindsight.vectorize.io)).

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/MeetMind.git
cd MeetMind
```

### 3. Create a Virtual Environment
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Variables

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```ini
# Hindsight API Base URL (Default: https://api.hindsight.vectorize.io)
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io

# Your private Hindsight API Key
HINDSIGHT_API_KEY=your_hindsight_api_key_here

# The persistent memory bank ID used by MeetMind
HINDSIGHT_BANK_ID=meetmind-demo
```

> [!WARNING]
> Never commit `.env` or expose your `HINDSIGHT_API_KEY` to public repositories. `.env` is included in `.gitignore`.

---

## Running Locally

### Start the Server
Run the FastAPI application with Uvicorn:

```bash
python main.py
```

The application will start at:
- **Web Interface**: [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Demo Scenario

The repository includes a comprehensive multi-interaction test dataset directly executable from the web UI:

```
                      ─── RAHUL'S PROGRESSION ───
 Meeting 1 (Sep 10)       Meeting 2 (Sep 17)        Meeting 3 (Sep 24)
┌──────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│ Sales Dashboard  │ ──▶│ Prototype Review   │ ──▶│ Keep it Simple     │
│ Weekly Updates   │    │ Export Feature Req │    │ Short Explanations │
│ Initial Scope    │    │ Promise: Friday    │    │ Executive Style    │
└──────────────────┘    └────────────────────┘    └────────────────────┘
                                   │
                                   ▼
          SYNTHESIZED RAHUL BRIEFING (All 3 meetings merged)
          - Remembers Friday prototype promise from M2
          - Remembers weekly cadence from M1
          - Respects brevity and simplicity preference from M3
                                   │
                                   ▼
          STRICT ISOLATION VERIFICATION (Priya & Unknown)
          - Priya: Mobile app onboarding flow (Zero Rahul bleed)
          - Unknown Contact: "Not available in memory." (Zero hallucination)
```

### 1-Click Execution via UI:
1. Navigate to `http://localhost:8000`.
2. Click **"🚀 Auto-Run Complete Demo Scenario"** in the top demo bar.
3. The system will sequentially ingest all 4 meetings and generate the final cross-interaction briefing in real time.

---

## Testing

MeetMind includes an enterprise-grade automated test suite:

### 1. Senior QA 12-Scenario Comprehensive Suite
Tests memory retention, multi-meeting accumulation, briefing synthesis, isolation, edge cases, and error tolerance:
```bash
python test_senior_qa.py
```
*Expected Result: 12/12 PASS (100% success rate)*

### 2. Longitudinal Agent Product Verification Suite
Validates all 15 core product requirements including commitment lifecycle states, user style learning, 14-part briefing, and 3-meeting Shiva scenario:
```bash
python test_longitudinal_agent.py
```
*Expected Result: 15/15 PASS (100% success rate)*

### 3. End-to-End Demo Scenario Verification
Validates the complete hackathon multi-meeting script (Rahul, Priya, UnknownPerson):
```bash
python test_demo_scenario.py
```

### 4. API & Backend Endpoint Suite
Verifies status codes, JSON validation, and error envelopes:
```bash
python test_backend.py
```

### 5. Hindsight Cloud Connectivity Diagnostic
Verifies network connectivity and bank access:
```bash
python test_connectivity.py
```

---

## Future Improvements

1. **Calendar & Email Automation**: Bi-directional integration with Google Calendar and Outlook 365 to automatically trigger briefings 15 minutes before scheduled meetings.
2. **Real-Time Audio Ingestion**: Automatic transcription via Whisper or Deepgram to parse and retain meeting notes directly from Zoom, Google Meet, or Microsoft Teams.
3. **Task & CRM Synchronization**: Two-way sync with Jira, Linear, Asana, and Salesforce to turn identified follow-up commitments into assigned tickets.
4. **Multi-Participant Entity Disambiguation**: Advanced graph mapping for meetings with 5+ attendees, attributing commitments to specific individuals.
5. **Local Offline Sidecar**: Support for fully offline, on-premise Hindsight container instances for privacy-conscious enterprise deployments.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
