🚀 YouTube AI Comment Assistant

An AI-powered assistant that helps YouTube creators automatically fetch, classify, draft, review, and publish comment replies — while keeping humans in full control.

Built using Python, FastAPI, YouTube OAuth, and OpenAI.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

✨ Overview

Managing YouTube comments at scale is time-consuming and inconsistent.

This assistant:

Fetches new comments automatically

Classifies them using AI

Generates smart reply drafts

Requires human approval

Publishes approved replies to YouTube

It automates the workflow — without sacrificing control or safety.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🎯 Problem

Creators receive hundreds of comments daily.

Manual replies:

Take hours

Reduce consistency

Slow growth

Create burnout

There is no structured system to manage comment workflows efficiently.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🧠 Solution

This project provides a structured AI-assisted workflow:

Fetch YouTube comments via OAuth

Classify comments (question, complaint, praise, other)

Generate contextual reply drafts

Store drafts locally

Review in a clean web interface

Approve → Post to YouTube

Human approval is required before publishing.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🛠 Key Features

🔎 Automated comment fetching

🧩 AI-based comment triage

✍️ AI-generated reply drafting

🛡 Human-in-the-loop approval

🌐 FastAPI review UI

📊 Runtime metrics tracking

🔐 Secure local secret management

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🏗 Architecture Flow



-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

⚙️ Tech Stack

Python 3.10+

FastAPI

Uvicorn

Pydantic

YouTube Data API (OAuth 2.0)

OpenAI API

JSON-based runtime state management

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🔒 Security & Safety

No secrets stored in repository

API keys stored in secrets/ directory

Human approval required before posting

Runtime data isolated in runtime/ folder

No auto-publishing without review

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🚀 Quickstart (Windows)

1️⃣ Clone Repository

git clone <your-repo-url>
cd youtube-ai-assistant

------------------------------------------------------------------------------------------

2️⃣ Create Virtual Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

----------------------------------------------------------------------------------------

3️⃣ Install Dependencies
pip install -r requirements.txt

----------------------------------------------------------------------------------------

4️⃣ Configure Environment

Copy:
.env.example

to:
.env

Fill in:

YT_CLIENT_ID

YT_CLIENT_SECRET

YOUTUBE_CHANNEL_ID

Place secrets inside:

secrets/openai_api_key
secrets/refresh_token.txt

-----------------------------------------------------------------------------------------------------------------

5️⃣ Run Web Review UI
.\run-ui.bat

Open:

http://127.0.0.1:8000

------------------------------------------------------------------------------------------------------

6️⃣ Run CLI Workflow (Fetch + Draft)

.\run-cli.bat

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

📁 Project Structure

app/

 ├── ai/
 
 ├── youtube/
 
 ├── review/
 
 ├── auth/

runtime/

secrets/

main.py

requirements.txt

run-ui.bat

run-cli.bat

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

📸 Screenshots

Add images inside /screenshots folder:
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🎥 Demo Video

Add your Loom or YouTube demo link here.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🛣 Roadmap

Multi-channel support

Creator tone customization

Bulk approval mode

Comment analytics dashboard

Cloud deployment version

MCP / Copilot integration

---------------------------------------------------------------------------------------------------------------------------------------------------------------------

🏆 Competition Category

Creative Apps – AI Productivity Tool for Content Creators

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

👩‍💻 Author

Warda Khan
Applied AI Engineer | AI Automation Builder
