🚀🚀 YouTube AI Comment Assistant

Reply to YouTube comments 10x faster — without losing control.

An AI-powered backend that fetches, classifies, drafts, and manages YouTube comment replies — with human approval built in.

Built using Python, FastAPI, YouTube OAuth,Guardrail and OpenAI.

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

Growing YouTube channels receive dozens to hundreds of comments daily.

Manual reply management:

• Consumes hours every week  
• Creates inconsistent messaging  
• Makes it easy to miss important questions  
• Leads to creator burnout  

There is no structured workflow for managing comments intelligently.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🧠 Solution

This assistant introduces a structured AI workflow:

1. Fetch new comments via YouTube OAuth  
2. Classify each comment using AI (question, complaint, praise, other)  
3. Generate contextual reply drafts  
4. Store drafts locally for traceability  
5. Review in a FastAPI-based UI  
6. Approve → Publish to YouTube  

AI assists. Humans decide.

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

🏗 Architecture

YouTube API → Fetcher → AI Triage → AI Drafter → Runtime Store → Review UI → Publish

<img width="1536" height="1024" alt="ChatGPT Image Feb 21, 2026, 06_28_17 AM" src="https://github.com/user-attachments/assets/32461fe0-88fe-47fc-89ad-52a7b4fe697e" />


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

git clone https://github.com/engrwardakhan-collab/Youtube-AI-Assistant-App.git
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
<img width="1884" height="807" alt="Screenshot 2026-02-21 113402" src="https://github.com/user-attachments/assets/5e8f1f53-6f7e-4cd6-b690-4def294168dd" />
<img width="1776" height="904" alt="Screenshot 2026-02-21 113503" src="https://github.com/user-attachments/assets/be3bdfda-298a-4f24-98e0-d7bbd0460ba1" />
<img width="1782" height="686" alt="Screenshot 2026-02-21 113524" src="https://github.com/user-attachments/assets/69f0dc6f-e7af-4894-8a95-6de1a9ec6dee" />
<img width="1810" height="645" alt="Screenshot 2026-02-21 113537" src="https://github.com/user-attachments/assets/800b23df-0b44-4e9a-9f03-85f486399032" />

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🎥 Demo Video

https://www.loom.com/share/3948c00a2bd947babbfcb6c998527710
---------------------------------------------------------------------------------------------------------------------------------------------------------------------

🏆 Competition Category

Creative Apps – AI Productivity Tool for Content Creators

--------------------------------------------------------------------------------------------------------------------------------------------------------------------
**How GitHub Copilot helped build this**

Copilot suggestions used to scaffold FastAPI routes, Pydantic models, OAuth flow boilerplate

Copilot Chat used to debug issues (OAuth refresh, YouTube API errors, pagination, rate limits)

Copilot used to refactor (separating services, error handling, retries, typing, test scaffolding)

<img width="601" height="1026" alt="image" src="https://github.com/user-attachments/assets/21b5b5cc-95e4-4b8f-9d68-a9ed06b9ad3c" />

-----------------------------------------------------------------------------------------------------------------------------------------------------------

👩‍💻 Author

Warda Khan
Applied AI Engineer | AI Automation Builder
