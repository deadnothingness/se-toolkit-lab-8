# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Checkpoint 1:** "What is the agentic loop?"

```
The agentic loop is the core reasoning cycle that autonomous AI agents follow to accomplish tasks independently.

The Cycle: Perceive → Reason → Act → Observe → Repeat

1. Perceive: Gather information from the environment (user input, file states, tool outputs).
2. Reason: Analyze the goal, plan next steps, and decide which action to take.
3. Act: Execute actions using available tools (file operations, web searches, commands, etc.).
4. Observe: Receive feedback from actions—results, errors, or state changes.
5. Repeat: Continue the loop until the goal is achieved or a stopping condition is met.

Why It Matters: This loop enables autonomy. Instead of requiring step-by-step instructions, an agent can:
- Break down complex tasks independently
- Adapt to unexpected results
- Self-correct when errors occur
- Make decisions based on real-time feedback
```

**Checkpoint 2:** "What labs are available in our LMS?"

```
Based on the workspace structure, here are the available labs in your Software Engineering Toolkit LMS:

 Lab    Directory                           
 ───────────────────────────────────────────
 Lab 1  lab-01-market-product-and-git
 Lab 2  se-toolkit-lab-2
 Lab 3  se-toolkit-lab-3
 Lab 4  se-toolkit-lab-4
 Lab 5  se-toolkit-lab-5
 Lab 6  se-toolkit-lab-6
 Lab 7  se-toolkit-lab-7
 Lab 8  se-toolkit-lab-8 (current workspace)

You have 8 labs total. Lab 1 focuses on market/product research and Git fundamentals, while Labs 2-8 are progressive software engineering toolkit exercises.
```

> Note: Without MCP tools, the agent hallucinated by reading workspace files instead of the LMS backend. This is expected behavior for Part A.

## Task 1B — Agent with LMS tools

**Checkpoint 1:** "What labs are available?"

```
Here are the 8 labs available in your LMS:

 ID  Lab Title                                  
 ────────────────────────────────────────────── 
 1   Lab 01 – Products, Architecture & Roles    
 2   Lab 02 — Run, Fix, and Deploy a Backend    
     Service                                    
 3   Lab 03 — Backend API: Explore, Debug,      
     Implement, Deploy                          
 4   Lab 04 — Testing, Front-end, and AI Agents 
 5   Lab 05 — Data Pipeline and Analytics       
     Dashboard                                  
 6   Lab 06 — Build Your Own Agent              
 7   Lab 07 — Build a Client with an AI Coding  
     Agent                                      
 8   Lab 08 — (current lab)                     

The labs progress from foundational concepts (products, architecture) through backend development, testing, data pipelines, and culminate in building AI agents. You're currently working in Lab 08.
```

**Checkpoint 2:** "Describe the architecture of the LMS system"

```
Based on the documentation and codebase, here's the LMS (Learning Management Service) System Architecture:

Overview:
The LMS is a containerized learning platform built for the Software Engineering Toolkit course. It follows the OBER data model and uses the C4 architecture documentation approach.

High-Level Architecture:

External Actors (Student, Admin/Instructor, Developer)
         │
         ▼
    Caddy (Port 42002) - Reverse Proxy + Static File Server
         │
    ┌────┼────┐
    ▼    ▼    ▼
FastAPI  Nanobot  pgAdmin
(Port    (WS:     (Port
42001)   8765)    42003)
    │        │
    ▼        ▼
PostgreSQL  MCP Tools
(Port       (LMS API)
42004)

Observability Stack:
- OTEL Collector → VictoriaLogs + VictoriaTraces

Core Components:
1. Caddy (Reverse Proxy) - Serves React/Flutter frontends, proxies API requests
2. FastAPI Backend (Python) - Routers: Items, Interactions, Learners; Auth: Bearer token; ORM: SQLModel
3. PostgreSQL Database - Tables: item, learner, interacts; Schema: OBER-compatible hierarchy
4. Nanobot Agent - AI-powered natural language interface with MCP tools
5. Frontend Clients - React SPA, Flutter Web, Telegram Bot
6. Qwen Code API - LLM gateway for Nanobot
7. Observability Stack - OpenTelemetry Collector, VictoriaLogs, VictoriaTraces
8. pgAdmin - Web-based database management UI

Data Model (OBER-based):
- Item (tree hierarchy): id, type, parent_id, title, description, attributes
- Learner: id, name, email, enrolled_at
- Interacts: learner_id, item_id, kind, created_at
```

## Task 1C — Skill prompt

**Checkpoint:** "Show me the scores" (without specifying a lab)

```
LMS Scores Summary

The LMS backend is healthy (56 items loaded), but there's no student submission data yet:

 Lab     Completion  Passed  Total  Avg Score 
 ──────────────────────────────────────────── 
 Lab 01  0%          0       0      —         
 Lab 02  0%          0       0      —         
 Lab 03  0%          0       0      —         
 Lab 04  0%          0       0      —         
 Lab 05  0%          0       0      —         
 Lab 06  0%          0       0      —         
 Lab 07  0%          0       0      —         
 Lab 08  0%          0       0      —         

Status: Fresh deployment — no learners registered and no submissions recorded yet. Scores will populate once students start submitting their work.
```

> The agent now lists all available labs with their scores (all 0% since this is a fresh deployment) instead of hallucinating or asking for clarification. This follows the skill prompt guidance.

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
