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
- **What it does**: Generates grounded, actionable intelligence from recalled memories.
- **How it works**: Ingests all recalled memory fragments and runs cognitive reflection to detect patterns, unresolved action items, and evolution of commitments over time.
- **Hindsight Integration**: Uses Hindsight Reflect to compile an 8-part executive briefing:
  1. Contact Name
  2. Previous Discussions (synthesized across multiple meetings)
  3. Decisions Made
  4. Unresolved Commitments
  5. Deadlines & Milestones
  6. Stakeholder Preferences & Communication Style
  7. Follow-up Items
  8. Three Strategic Questions to Ask in the Next Meeting

### 4. Persistent Memory
- Unlike prompt-stuffing approaches where history is wiped when a chat session ends, Hindsight memory banks persist perpetually. Meeting 5 effortlessly recalls context established in Meeting 1, even if months have elapsed.

### 5. How Memory Improves Future Meeting Preparation
- **Cumulative Learning**: Each meeting augments the existing bank. If Rahul asks for simplicity in Meeting 1, requests an export feature in Meeting 2, and stresses brevity in Meeting 3, the briefing synthesizes all three into a coherent strategy.
- **Accountability Tracking**: Promises made to clients are tracked across time until explicitly closed out.
- **Zero Hallucination Guardrails**: Unknown contacts or unmentioned topics receive clear empty indicators, ensuring executive reliability.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Executive Browser UI                            │
│           (HTML5, Vanilla JS, Glassmorphism CSS, Trace Drawer)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼  REST API (JSON over HTTP)
┌────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Backend                              │
│              (main.py - CORS, Validation, Async Handlers)              │
│                                                                        │
│   POST /meetings          GET /prepare/{contact}         GET /health   │
└─────────┬───────────────────────────────┬──────────────────────────────┘
          │                               │
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│    retain.py     │            │    recall.py     │
│ (Memory Ingest)  │            │ (Hybrid Search)  │
└─────────┬────────┘            └─────────┬────────┘
          │                               │
          │                               ▼
          │                     ┌──────────────────┐
          │                     │    reflect.py    │
          │                     │ (Reasoning Core) │
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

- **Structured Meeting Capture**: Clean form to ingest meeting contact, date, and notes with instant feedback.
- **Visible 4-Step Processing Pipeline**: Visual stepper demonstrating:
  `Save Meeting ──▶ Hindsight Memory ──▶ Recall Past Context ──▶ AI Briefing`
- **8-Part Actionable Briefing**: Delivers a structured executive briefing covering past discussions, decisions, commitments, deadlines, preferences, follow-ups, and 3 strategic questions.
- **Hindsight Memory Status & Trace**: Visual badge (`✓ Hindsight Memory Used`) and an expandable **Memory Trace Drawer** allowing users to inspect raw recalled fragments.
- **Before & After Memory Impact Card**: Side-by-side comparison illustrating the difference between a stateless LLM (generic, hallucinated) vs. MeetMind + Hindsight (grounded, longitudinal).
- **Interactive 60-Second Demo Bar**: Preset buttons to immediately test multi-meeting synthesis (Rahul), contact isolation (Priya), and zero-hallucination guardrails (Unknown Contact).
- **Strict Contact Memory Isolation**: Memories for Contact A never bleed into Contact B.
- **Robust Error Handling**: Graceful degradation, clear error banners, and non-blocking asynchronous execution.

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

### 2. End-to-End Demo Scenario Verification
Validates the complete hackathon multi-meeting script (Rahul, Priya, UnknownPerson):
```bash
python test_demo_scenario.py
```

### 3. API & Backend Endpoint Suite
Verifies status codes, JSON validation, and error envelopes:
```bash
python test_backend.py
```

### 4. Hindsight Cloud Connectivity Diagnostic
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
