# YouTube AI Comment Assistant

A Python app that fetches your latest YouTube comments, triages them, and drafts human-sounding replies with an LLM. Replies are saved for **human review** before anything is posted.

## Status
Active development — core auth and YouTube ingestion implemented; AI drafting and triage evolving.

## Why this exists
Recruiters: this project shows practical API integration, stateful processing, and safe LLM usage with a human-in-the-loop workflow.

## What it does
1. **OAuth refresh**: Uses a stored refresh token to get a valid access token.
2. **Fetch comments**: Pulls recent comment threads for your channel.
3. **Dedupe + checkpointing**: Avoids reprocessing old comments and spam duplicates.
4. **Rule-based triage**: Filters spam, low-value comments, and prioritizes questions/complaints.
5. **LLM drafting**: Batches comments and drafts short, polite replies.
6. **Human review**: Writes drafts to disk so a human can approve before posting.

## Features
- YouTube Data API v3 integration (read comments, reply endpoint ready)
- Stateful processing with checkpoints and replied-ID tracking
- JSON-based triage rules for spam and intent detection
- Batch LLM drafting with failure handling
- Human-in-the-loop safety: **no auto-posting**

## Tech stack
- Python 3.x
- YouTube Data API v3
- Requests
- `python-dotenv` for `.env` configuration
- LLM provider abstraction (OpenAI-compatible wrapper; provider-agnostic by design)

## Project structure
```
app/
  ai/
    triage_engine.py     # rules + scoring
    triage.py            # triage entrypoint
    batch_drafter.py     # LLM batch drafting
    openai_client.py     # provider wrapper (implement complete())
  auth/
    google_oauth_client.py
    token_manager.py
    token_store.py
  youtube/
    comment_fetcher.py
    youtube_client.py
runtime/
  checkpoint.json
  tokens.json
  triage.rules           # JSON rules file
secrets/
  refresh_token.txt
main.py
```

## Setup
1. Create a virtual environment and install deps:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install python-dotenv
   ```

2. Create a `.env` file in the project root:
   ```env
   YT_CLIENT_ID=your_google_oauth_client_id
   YT_CLIENT_SECRET=your_google_oauth_client_secret
   YOUTUBE_CHANNEL_ID=your_channel_id

   REFRESH_TOKEN_PATH=secrets/refresh_token.txt
   TOKENS_CACHE_PATH=runtime/tokens.json
   ```

3. Place your Google OAuth refresh token at `secrets/refresh_token.txt`.

4. Ensure the triage rules file is valid JSON. By default it is `runtime/triage.rules`.
   - If you rename it, also update `app/ai/triage.py` to match.

## Run
```powershell
python main.py
```

## Human-in-the-loop workflow
- Draft replies are written to `runtime/drafts/` as JSON files.
- Review/approve drafts manually before posting.
- The project intentionally **does not auto-post** replies yet.

## Notes
- `app/youtube/youtube_client.py` already includes `reply_to_comment()` for posting replies.
- The LLM wrapper should expose a `complete(system, user, max_output_tokens)` method.
- Add any missing dependencies to `requirements.txt` as you wire providers.

## License
Not specified yet.

> Note: This repository is a learning + portfolio project. Design favors clarity and safety over maximum automation.
