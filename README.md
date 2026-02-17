🚀 YouTube AI Comment Assistant

An AI-powered assistant that helps YouTube creators automatically fetch, triage, draft, review, and publish comment replies — with a human-in-the-loop safety layer.

Built using Python, FastAPI, YouTube Data API (OAuth), and OpenAI.

✨ What It Does

Fetches new comments from your YouTube channel

Classifies comments (question, complaint, praise, other)

Generates AI-powered reply drafts

Flags risky comments for human review

Provides a clean web UI to approve or edit replies

Posts approved replies directly to YouTube

Tracks metrics and reply history

🧠 Why This Project

Creators receive hundreds of comments.

Manually replying:

Takes hours

Kills consistency

Slows channel growth

This assistant:

Automates 80% of the workflow

Keeps humans in control

Saves massive time

🎥 Demo

👉 Add your Loom / YouTube demo link here

📸 Screenshots

Add these inside a /screenshots folder and reference them here:

Review Dashboard

Drafted Replies List

Approve / Reject Flow

“No Comments Available” State

Example:

![Dashboard](screenshots/dashboard.png)

🏗 Architecture Overview

Workflow:

Fetch YouTube comments via OAuth

Run AI triage classification

Generate draft replies

Store drafts in runtime folder

Review via FastAPI UI

Approve → Post to YouTube API

Human approval is required before posting.

⚙️ Tech Stack

Python 3.10+

FastAPI

Uvicorn

Pydantic

YouTube Data API (OAuth 2.0)

OpenAI API

File-based state storage (JSON runtime tracking)

🔒 Safety & Human-in-the-Loop

Comments are categorized before reply

Risky comments can be flagged

Replies require manual approval

No auto-post without review

API keys stored securely outside repo

🚀 Quickstart
1️⃣ Clone Repository
git clone <your-repo-url>
cd youtube-ai-assistant

2️⃣ Create Virtual Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment

Copy:

.env.example


to:

.env


Fill in:

YT_CLIENT_ID

YT_CLIENT_SECRET

YOUTUBE_CHANNEL_ID

Place your secrets inside:

secrets/openai_api_key
secrets/refresh_token.txt

5️⃣ Run Web UI
python -m uvicorn app.review.webapp:app --reload


Open:

http://127.0.0.1:8000

6️⃣ Run CLI Workflow (Fetch + Draft)
python main.py

📊 Project Structure
app/
 ├── ai/
 ├── youtube/
 ├── review/
 ├── auth/
runtime/
secrets/
main.py
requirements.txt

🛣 Roadmap

Future improvements:

Multi-channel support

Creator tone selection (professional / funny / brand voice)

Bulk approve mode

Comment analytics dashboard

Cloud deployment version

Copilot / MCP integration

🎯 Competition Category

Creative Apps – AI Productivity Tool for Content Creators

👩‍💻 Author

Built by Warda Khan
Applied AI Engineer | AI Automation Builder
