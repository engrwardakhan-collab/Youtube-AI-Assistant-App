from __future__ import annotations

from fastapi import FastAPI, HTTPException,Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from datetime import datetime, timezone

from app.config import Settings
from app.auth.token_store import TokenStore
from app.auth.google_oauth_client import GoogleOAuthClient
from app.auth.token_manager import TokenManager
from app.errors import RefreshTokenMissing

from app.review.stores import DraftStores
from app.review.metrics import Metrics
from app.youtube.reply_poster import YouTubeReplyPoster


app = FastAPI(
    title="YouTube Review UI",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

stores = DraftStores(Path("runtime"))
metrics = Metrics(Path("runtime/metrics.json"))


def _build_services():
    s = Settings()

    if not s.REFRESH_TOKEN_PATH.exists():
        raise RefreshTokenMissing(f"Refresh token file not found at: {s.REFRESH_TOKEN_PATH}")

    store = TokenStore(refresh_token_path=s.REFRESH_TOKEN_PATH, cache_path=s.TOKENS_CACHE_PATH)
    oauth_client = GoogleOAuthClient(
        token_url=s.GOOGLE_TOKEN_URL,
        client_id=s.CLIENT_ID,
        client_secret=s.CLIENT_SECRET,
    )
    manager = TokenManager(store=store, oauth_client=oauth_client, refresh_early_seconds=s.REFRESH_EARLY_SECONDS)
    return YouTubeReplyPoster(manager)


def _escape(s: str | None) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@app.post("/refresh")
def refresh():
    """
    Fetch new comments + draft replies + save to runtime/drafts.
    This calls run_once() from main.py
    """
    try:
        from main import run_once  # <-- after you add run_once() in main.py
        result = run_once()

        # Pass fetched count in query string
        fetched = result.get("fetched", 0)
        return RedirectResponse(url=f"/?fetched={fetched}", status_code=303)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {e}")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    drafts = stores.list_pending()

    fetched_param = request.query_params.get("fetched")
    no_comments_message = ""

    if fetched_param is not None:
        try:
            fetched_count = int(fetched_param)
            if fetched_count == 0:
                no_comments_message = """
            <div style="padding:14px; border:1px solid #ddd; border-radius:10px; background:#f9f9f9; margin-bottom:15px;">
              No comments available
            </div>
            """
        except ValueError:
            pass


    cards = []
    for d in drafts:
        original = _escape(d.original_text)
        reply = _escape(d.reply_text)

        cards.append(f"""
        <div style="border:1px solid #ddd; padding:14px; margin:12px 0; border-radius:10px;">
          <div style="font-size:13px; color:#666;">
            <b>{_escape(d.author) or "Unknown"}</b>
            &nbsp;·&nbsp;<code>{_escape(d.comment_id)}</code>
            &nbsp;·&nbsp;{_escape(d.published_at)}
          </div>

          <div style="margin-top:8px; padding:10px; background:#f7f7f7; border-radius:8px;">
            {original}
          </div>

          <div style="margin-top:10px;">
            <div style="font-size:13px; color:#666; margin-bottom:6px;">AI Reply</div>
            <form method="post" action="/draft/{_escape(d.comment_id)}/approve">
              <textarea name="edited_reply_text" rows="3" style="width:100%; padding:10px;">{reply}</textarea>

              <div style="margin-top:10px; display:flex; gap:10px; align-items:center;">
                <button type="submit">Approve & Post</button>
              </div>
            </form>

            <form method="post" action="/draft/{_escape(d.comment_id)}/reject" style="margin-top:10px;">
              <input name="reason" placeholder="Reject reason (optional)" style="width:70%; padding:8px;"/>
              <button type="submit">Reject</button>
            </form>
          </div>
        </div>
        """)

    html = f"""
    <html>
      <head><title>YouTube Review UI</title></head>
      <body style="font-family: Arial; margin: 24px; max-width: 1100px;">
        <h2>YouTube Comment Review</h2>

        <div style="display:flex; gap:12px; align-items:center; margin-bottom:14px;">
          <form method="post" action="/refresh" style="margin:0;">
            <button type="submit">Fetch New Comments</button>
          </form>
          <a href="/errors">View Failed Posts</a>
        </div>

        <p>Pending: <b>{len(drafts)}</b></p>
        {no_comments_message}


        {''.join(cards) if cards else '<div style="padding:14px;border:1px solid #ddd;border-radius:10px;">No pending drafts</div>'}
      </body>
    </html>
    """
    return HTMLResponse(html)


@app.get("/errors", response_class=HTMLResponse)
def errors_page():
    errs = stores.list_errors()

    cards = []
    for d in errs:
        original = _escape(d.original_text)
        reply = _escape(d.reply_text)

        # NOTE: "error" is not part of DraftRecord, but it exists in the JSON file
        # so we read it raw here for display
        err_file = (Path("runtime") / "errors" / f"{d.comment_id}.json")
        err_msg = ""
        try:
            import json as _json
            err_msg = _json.loads(err_file.read_text(encoding="utf-8")).get("error", "")
        except Exception:
            err_msg = ""

        cards.append(f"""
        <div style="border:1px solid #f0b6b6; padding:14px; margin:12px 0; border-radius:10px; background:#fff6f6;">
          <div style="font-size:13px; color:#666;">
            <b>{_escape(d.author) or "Unknown"}</b>
            &nbsp;·&nbsp;<code>{_escape(d.comment_id)}</code>
          </div>

          <div style="margin-top:8px; padding:10px; background:#fff; border-radius:8px;">
            {original}
          </div>

          <div style="margin-top:8px; color:#b00020; font-size:13px;">
            <b>Failed:</b> {_escape(err_msg)}
          </div>

          <form method="post" action="/draft/{_escape(d.comment_id)}/retry" style="margin-top:10px;">
            <textarea name="edited_reply_text" rows="3" style="width:100%; padding:10px;">{reply}</textarea>

            <div style="margin-top:10px; display:flex; gap:10px;">
              <button type="submit">Retry Post</button>
              <button formaction="/draft/{_escape(d.comment_id)}/reject" formmethod="post">Reject</button>
            </div>
          </form>
        </div>
        """)

    html = f"""
    <html>
      <head><title>Failed Posts</title></head>
      <body style="font-family: Arial; margin: 24px; max-width: 1100px;">
        <h2>Failed Posts</h2>
        <p><a href="/">← Back to Pending</a></p>
        <p>Failures: <b>{len(errs)}</b></p>

        {''.join(cards) if cards else '<div style="padding:14px;border:1px solid #ddd;border-radius:10px;">No failures</div>'}
      </body>
    </html>
    """
    return HTMLResponse(html)


@app.post("/draft/{comment_id}/approve")
def approve(comment_id: str, edited_reply_text: str | None = None):
    d = stores.get_pending(comment_id)
    if not d:
        raise HTTPException(status_code=404, detail="Draft not found")

    reply_text = (edited_reply_text or d.reply_text or "").strip()
    if not reply_text:
        raise HTTPException(status_code=400, detail="Reply text is empty")

    poster = _build_services()

    try:
        metrics.inc("approved", 1)
        yt_resp = poster.reply_with_retry(parent_comment_id=comment_id, reply_text=reply_text)
        metrics.inc("posted", 1)

        stores.move_to_processed(
            d.model_copy(update={"reply_text": reply_text}),
            extra={
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "youtube_response": yt_resp,
                "status": "posted",
            },
        )
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        metrics.inc("post_failures", 1)
        stores.move_to_errors(d.model_copy(update={"reply_text": reply_text}), error=str(e))
        return RedirectResponse(url="/errors", status_code=303)


@app.post("/draft/{comment_id}/retry")
def retry(comment_id: str, edited_reply_text: str | None = None):
    d = stores.get_error(comment_id)
    if not d:
        raise HTTPException(status_code=404, detail="Failed draft not found")

    reply_text = (edited_reply_text or d.reply_text or "").strip()
    if not reply_text:
        raise HTTPException(status_code=400, detail="Reply text is empty")

    poster = _build_services()

    try:
        yt_resp = poster.reply_with_retry(parent_comment_id=comment_id, reply_text=reply_text)

        stores.move_error_to_processed(
            d.model_copy(update={"reply_text": reply_text}),
            extra={
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "youtube_response": yt_resp,
                "status": "posted",
            },
        )
        metrics.inc("posted", 1)
        return RedirectResponse(url="/errors", status_code=303)

    except Exception as e:
        stores.update_error(comment_id, error=str(e))
        metrics.inc("post_failures", 1)
        return RedirectResponse(url="/errors", status_code=303)


@app.post("/draft/{comment_id}/reject")
def reject(comment_id: str, reason: str | None = None):
    # allow reject from either pending or errors
    d = stores.get_pending(comment_id) or stores.get_error(comment_id)
    if not d:
        raise HTTPException(status_code=404, detail="Draft not found")

    metrics.inc("rejected", 1)
    stores.move_to_rejected(d, reason=reason)
    return RedirectResponse(url="/", status_code=303)
