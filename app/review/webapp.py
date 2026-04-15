from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from datetime import datetime, timezone

from app.config import Settings
from app.auth.token_store import TokenStore
from app.auth.google_oauth_client import GoogleOAuthClient
from app.auth.token_manager import TokenManager
from app.errors import RefreshTokenMissing

from app.review.stores import DraftStores
from app.review.metrics import Metrics, build_dashboard, read_triage
from app.youtube.reply_poster import YouTubeReplyPoster
from app.review.metrics import list_triage_by_decision
import re


app = FastAPI(
    title="YouTube Review UI",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

stores = DraftStores()
metrics = Metrics()
RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", "runtime"))


def _build_services():
    s = Settings()

    if not s.REFRESH_TOKEN_PATH.exists():
        raise RefreshTokenMissing(f"Refresh token file not found at: {s.REFRESH_TOKEN_PATH}")

    store = TokenStore(refresh_token_path=s.REFRESH_TOKEN_PATH, cache_path=s.ACCESS_TOKEN_PATH)
    oauth_client = GoogleOAuthClient(
        token_url=s.GOOGLE_TOKEN_URL,
        client_id=s.CLIENT_ID,
        client_secret=s.CLIENT_SECRET,
    )
    manager = TokenManager(store=store, oauth_client=oauth_client, refresh_early_seconds=s.REFRESH_EARLY_SECONDS)
    return YouTubeReplyPoster(manager)


def _escape(s: str | None) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# CSS Styles - separated to avoid linter false positives
CSS_HOME_STYLES = r"""
  :root{
    --bg:#f6f6f6;
    --surface:#ffffff;
    --surface-soft:#f6f7f8;
    --surface-hover:#fbfbfb;
    --muted:#5f6368;
    --muted-soft:#8a8f98;
    --text:#0f0f0f;
    --border:#e2e2e2;
    --border-strong:#d3d3d3;
    --chip:#f4f5f6;
    --good:#e6f4ea;
    --warn:#fff4e5;
    --bad:#fde8e7;
    --accent:#ff0033;
    --accent-dark:#cc0000;
    --accent-soft:#fff1f1;
    --shadow-sm:0 1px 2px rgba(15,15,15,.05), 0 1px 1px rgba(15,15,15,.03);
    --shadow-md:0 12px 28px rgba(15,15,15,.08), 0 2px 6px rgba(15,15,15,.04);
    --shadow-red:0 8px 22px rgba(204,0,0,.18);
  }

  html{
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

  body{
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial;
    margin: 0;
    background:
      linear-gradient(180deg, rgba(255,255,255,.86), rgba(246,246,246,0) 260px),
      radial-gradient(900px 320px at 50% -180px, rgba(204,0,0,.08), transparent 70%),
      var(--bg);
    color: var(--text);
  }

  .container{ max-width: 1100px; margin: 0 auto; padding: 26px 18px 60px; }

  .topbar{
  position: sticky; top: 0; z-index: 5;
  background:
    linear-gradient(135deg, #7f0505 0%, #b00000 48%, #d41414 100%);
  border-bottom: 1px solid rgba(90,0,0,.35);
  padding: 10px 0;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 26px rgba(127,5,5,.16), 0 1px 2px rgba(0,0,0,.08);
}

.topbar::before{
  content: none;
}

.topbar::after{
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  height: 1px;
  width: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.55), rgba(255,220,220,.75), transparent);
}

.topbar-inner{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  padding: 8px 0;
}

.title{
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.1;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 12px;
  text-wrap: balance;
}

.brand-mark{
  position: relative;
  display: inline-flex;
  flex: 0 0 auto;
  width: 34px;
  height: 24px;
  background: linear-gradient(135deg, #ffffff, #ffe7e7);
  border-radius: 7px;
  box-shadow: 0 5px 16px rgba(40,0,0,.20);
}

.brand-mark::after{
  content: "";
  position: absolute;
  left: 13px;
  top: 7px;
  width: 0;
  height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-left: 8px solid #b00000;
}

.title-text{
  display: inline-block;
  max-width: min(72vw, 720px);
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(30,0,0,.32);
}

.subtitle{
  color: rgba(255,244,244,.84);
  font-size: 15px;
  margin-top: 8px;
  letter-spacing: 0;
  padding-left: 46px;
  max-width: 760px;
}

.actions{
  display:flex;
  align-items:center;
  gap:14px;
  flex-wrap:wrap;
}

.link{
  color: rgba(255,244,244,.78);
  opacity:1;
  text-decoration:none;
  border-bottom:2px solid transparent;
  font-size: 14px;
  font-weight: 650;
  letter-spacing: 0;
  padding: 8px 2px;
  transition: color .18s ease, border-color .18s ease;
}

.link:hover{
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,.9);
}

  .topbar-inner{ display:flex; align-items:center; justify-content:space-between; gap:12px; }
.subtitle {
  color: rgba(255,244,244,.84);
  font-size: 14px;
  margin-top: 6px;
  letter-spacing: 0;
}  .subtitle{ color: rgba(255,244,244,.88); font-size: 13px; margin-top: 4px; }

  .actions{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
  .link{ color: rgba(255,244,244,.78); opacity:1; text-decoration:none; border-bottom:2px solid transparent; }
  .link:hover{ color: #ffffff; border-bottom-color: rgba(255,255,255,.9); }

  .btn{
    border: 1px solid var(--border);
    background: linear-gradient(180deg, #ffffff, var(--surface-soft));
    color: var(--text);
    padding: 9px 12px;
    border-radius: 8px;
    font-weight: 650;
    cursor:pointer;
    transition: transform .05s ease, background .2s ease, border-color .2s ease, box-shadow .2s ease;
  }
  .btn:hover{ background: linear-gradient(180deg, #ffffff, #eeeeee); border-color: var(--border-strong); box-shadow: 0 2px 8px rgba(0,0,0,.08); }
  .btn:active{ transform: translateY(1px); }
  .btn-primary{
    background: linear-gradient(180deg, #e60000, var(--accent-dark));
    border-color: var(--accent-dark);
    color: #ffffff;
  }
  .btn-primary:hover{ background: linear-gradient(180deg, #d10000, #b30000); border-color: #b30000; box-shadow: var(--shadow-red); }

  .row{ display:flex; gap:14px; flex-wrap:wrap; align-items:stretch; margin-top: 18px; }
  .cards{ display:flex; gap:12px; flex-wrap:wrap; margin-top: 16px; }

  .card{
    background: linear-gradient(180deg, #ffffff, #fbfbfb);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    min-width: 190px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .18s ease, border-color .18s ease, background .18s ease;
  }
  .card:hover{
    border-color: var(--border-strong);
    background: var(--surface-hover);
    box-shadow: var(--shadow-md);
  }
  .card-label{
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: uppercase;
}

.card-value{
  font-size: 30px;
  font-weight: 850;
  letter-spacing: 0;
  margin-top: 6px;
  color: var(--text);
}
  .card-hint{ color: var(--muted); font-size: 12px; margin-top: 6px; }

  .bubble{
  margin-top: 10px;
  padding: 12px 12px;
  background: linear-gradient(180deg, #f8f8f8, var(--surface-soft));
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
}

  .section{
    margin-top: 14px;
    background: linear-gradient(180deg, #ffffff, #fbfbfb);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    box-shadow: var(--shadow-sm);
  }
  .section h3{ margin:0 0 10px 0; font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: 0; }

  .insight-row{ display:flex; gap:16px; flex-wrap:wrap; font-size: 13px; color: var(--text); }
  .muted{ color: var(--muted); font-size: 13px; }

  .pill{
    display:inline-flex; align-items:center; gap:6px;
    padding: 4px 10px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, #ffffff, var(--chip));
    border-radius: 999px;
    font-size: 12px;
    color: var(--text);
    margin-left: 8px;
    white-space: nowrap;
  }
  .pill-ok{ background: var(--good); }
  .pill.good{ background: var(--good); }
  .pill.warn{ background: var(--warn); }
  .pill.bad{ background: var(--bad); }

  .draft{
    position: relative;
    margin-top: 14px;
    background: linear-gradient(180deg, #ffffff, #fbfbfb);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    box-shadow: var(--shadow-sm);
    transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
    overflow: hidden;
  }
  .draft::before{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-dark));
    opacity: .9;
  }
  .draft:hover{
    border-color: var(--border-strong);
    background: linear-gradient(180deg, #ffffff, var(--surface-hover));
    box-shadow: var(--shadow-md);
  }
  .bubble{
    margin-top: 10px;
    padding: 12px 12px;
    background: linear-gradient(180deg, #f8f8f8, var(--surface-soft));
    border: 1px solid var(--border);
    border-radius: 8px;
  }

  textarea{
    box-sizing: border-box;
    width: 100%;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, #ffffff, #fcfcfc);
    color: var(--text);
    font-family: inherit;
    font-size: 14px;
    line-height: 1.35;
    outline: none;
  }
  textarea:focus{ border-color: var(--accent-dark); box-shadow: 0 0 0 3px var(--accent-soft); }

  input{
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, #ffffff, #fcfcfc);
    color: var(--text);
    outline: none;
    width: min(560px, 70vw);
  }
  input:focus{ border-color: var(--accent-dark); box-shadow: 0 0 0 3px var(--accent-soft); }

  .controls{ display:flex; gap:10px; align-items:center; margin-top: 10px; flex-wrap:wrap; }

  .empty{
    margin-top: 16px;
    border: 1px dashed #c7c7c7;
    border-radius: 8px;
    padding: 18px;
    background: linear-gradient(180deg, #ffffff, #fbfbfb);
  }
  .empty-title{ font-size: 16px; font-weight: 800; }
  .empty-subtitle{ color: var(--muted); margin-top: 6px; font-size: 13px; }

  .toast{
    margin-top: 14px;
    padding: 12px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: linear-gradient(180deg, #ffffff, #fbfbfb);
  }

  .panel{
    background: linear-gradient(180deg, #ffffff, #fbfbfb);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
  }

  .alert,
  .danger-box{
    margin-top: 12px;
    padding: 12px;
    border: 1px solid #f5c2c0;
    border-radius: 8px;
    background: var(--bad);
    color: #8b0000;
  }

  .meta{
    color: var(--muted-soft);
    margin-left: 8px;
  }

  .card-title{
    color: var(--text);
    font-size: 15px;
  }

  @media (max-width: 720px){
    .topbar-inner{ align-items:flex-start; flex-direction:column; }
    .title{ font-size: 28px; }
    .actions{ width:100%; gap:12px; }
    input{ width: 100%; box-sizing: border-box; }
    .controls{ align-items:stretch; }
  }
"""

CSS_IGNORED_STYLES = r"""
  body { font-family: Arial; margin: 24px; max-width: 1100px; }
  .muted { color:#666; font-size:13px; }

  .row { border:1px solid #e5e7eb; padding:14px; margin:12px 0; border-radius:12px; background:#fff; }
  .text { margin-top:10px; padding:12px; background:#f7f7f7; border-radius:10px; font-size:14px; }
  .meta { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
  .right { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }

  .pill { display:inline-block; padding:4px 8px; border:1px solid #e5e7eb; border-radius:999px; font-size:12px; opacity:.9; }
  .badge-low { border-color:#d1d5db; }
  .badge-warn { border-color:#fca5a5; }
  .badge-good { border-color:#86efac; }

  .reason { margin-top:10px; font-size:13px; color:#555; }
  a { text-decoration:none; }
"""


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
    dashboard = build_dashboard(RUNTIME_DIR, drafts)

    # -------------------------
    # build dashboard HTML safely (avoid nested f-string issues)
    # -------------------------
    dashboard_cards_html = ""
    for c in dashboard.get("cards", []):
        dashboard_cards_html += (
            "<div class='card'>"
            f"<div class='card-label'>{_escape(str(c.get('label','')))}</div>"
            f"<div class='card-value'>{_escape(str(c.get('value','')))}</div>"
            f"<div class='card-hint'>{_escape(str(c.get('hint','')))}</div>"
            "</div>"
        )

    ins = dashboard.get("insights", {}) or {}
    top_intent = _escape(str(ins.get("top_intent") or "—"))
    keywords = _escape(", ".join(ins.get("top_keywords") or []) or "—")

    risk_alerts = ins.get("risk_alerts") or []
    risk_alerts_html = ""
    if risk_alerts:
        risk_items = "".join([f"<li>{_escape(str(a))}</li>" for a in risk_alerts])
        risk_alerts_html = f"<div class='alert'><b>risk alerts:</b><ul>{risk_items}</ul></div>"

    dashboard_insights_html = f"""
    <div class="section">
      <h3>ai insights</h3>
      <div class="insight-row">
        <div><b>top intent:</b> {top_intent}</div>
        <div><b>keywords:</b> {keywords}</div>
      </div>
      {risk_alerts_html}
    </div>
    """

    fetched_param = request.query_params.get("fetched")

    no_comments_message = ""

    # Show ONLY if a fetch just happened AND fetched=0
    if fetched_param is not None:
        try:
            fetched_count = int(fetched_param)
            if fetched_count == 0:
                no_comments_message = """
                <div class="panel" style="margin:14px 0;">
                  <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
                    <div>
                      <div style="font-weight:800; font-size:14px;">no comments available</div>
                      <div class="muted" style="margin-top:6px;">
                        we didn't find any new comments this time. try again later.
                      </div>
                    </div>
                    <div class="pill pill-ok">all clear</div>
                  </div>
                </div>
                """
        except ValueError:
            pass
        
    auto_clear_fetched_js = ""

    if fetched_param is not None:
        auto_clear_fetched_js = """
    <script>
      // remove ?fetched=... from URL so banner doesn't persist
      const url = new URL(window.location.href);
      url.searchParams.delete('fetched');
      window.history.replaceState({}, '', url.toString());
    </script>
    """

    cards = []
    for d in drafts:
        original = _escape(d.original_text)
        reply = _escape(d.reply_text)

        triage = read_triage(RUNTIME_DIR, d.comment_id)
        label = triage.get("label") or triage.get("category")
        priority = triage.get("priority")

        spam_score = triage.get("spam_score")
        relevance_score = triage.get("relevance_score")

        # pick pill color based on scores (simple)
        spam_pct = round(float(spam_score) * 100) if isinstance(spam_score, (int, float)) else None
        rel_pct  = round(float(relevance_score) * 100) if isinstance(relevance_score, (int, float)) else None

        spam_class = "bad" if (spam_pct is not None and spam_pct >= 50) else ("warn" if (spam_pct is not None and spam_pct >= 25) else "")
        rel_class  = "good" if (rel_pct is not None and rel_pct >= 60) else ""

        cards.append(f"""
<div class="draft">
  <div class="muted">
    <b class="card-title">{_escape(d.author) or "Unknown"}</b>
<span class="meta">{_escape(d.published_at) if hasattr(d, "published_at") else ""}</span>

    {f"<span class='pill'>intent: {_escape(str(label))}</span>" if label else ""}
    {f"<span class='pill'>priority: {_escape(str(priority))}</span>" if priority else ""}

    {f"<span class='pill {spam_class}'>spam: {spam_pct}%</span>" if spam_pct is not None else ""}
    {f"<span class='pill {rel_class}'>relevance: {rel_pct}%</span>" if rel_pct is not None else ""}
  </div>

  <div class="bubble">{original}</div>

  <div class="muted" style="margin-top:12px;">AI Reply</div>

  <form method="post" action="/draft/{_escape(d.comment_id)}/approve">
    <textarea name="edited_reply_text" rows="4">{reply}</textarea>

    <div class="controls">
      <button class="btn btn-primary" type="submit">Approve & Post</button>
    </div>
  </form>

  <form method="post" action="/draft/{_escape(d.comment_id)}/reject" style="margin-top:10px;">
    <div class="controls">
      <input name="reason" placeholder="Reject reason (optional)" />
      <button class="btn" type="submit">Reject</button>
    </div>
  </form>
</div>
""")

    html = f"""
<html>
  <head>
    <title>YouTube Review UI</title>
    <style>
{CSS_HOME_STYLES}
</style>
  </head>

  <body>
  {_topbar("YouTube Comment Review AI Assistant",
         "Approve, Edit, and Post Replies — with AI Triage",
         "Pending")}

  <div class="container">
    <div class="row" style="justify-content:space-between; align-items:center;">
  <div class="muted">Pending: <b>{len(drafts)}</b></div>

  <form method="post" action="/refresh" style="margin:0;">
    <button class="btn btn-primary" type="submit">Fetch New Comments</button>
  </form>
</div>

    {no_comments_message}
    {auto_clear_fetched_js}

    <div class="cards">
      {dashboard_cards_html}
    </div>

    {dashboard_insights_html}

    {''.join(cards) if cards else """
      <div class="empty">
        <div class="empty-title">🎉 you're all caught up</div>
        <div class="empty-subtitle">
          no new comments need your attention right now. click <b>fetch new comments</b> to check again.
        </div>
      </div>
    """}
  </div>
</body>
</html>
"""

    return HTMLResponse(html)


def _topbar(title: str, subtitle: str, active: str) -> str:
    def tab(label: str, href: str, key: str) -> str:
        style = "color: #ffffff; border-bottom-color: rgba(255,255,255,.95);" if key == active.lower() else ""
        return f"<a class='link' href='{href}' style='{style}'>{label}</a>"

    return f"""
    <div class="topbar">
      <div class="container topbar-inner">
        <div>
          <div class="title"><span class="brand-mark"></span><span class="title-text">{_escape(title)}</span></div>
          <div class="subtitle">{_escape(subtitle)}</div>
        </div>

        <div class="actions">
          {tab("Pending", "/", "pending")}
          {tab("Failed Posts", "/errors", "errors")}
          {tab("Ignored", "/ignored", "ignored")}
        </div>
      </div>
    </div>
    """

@app.get("/ignored", response_class=HTMLResponse)
def ignored_page(request: Request):
    items = list_triage_by_decision(RUNTIME_DIR, "ignore")
    only_high_spam = request.query_params.get("only_high_spam") == "1"

    # -------------------------
    # High-spam filtering (more inclusive)
    # -------------------------
    if only_high_spam:
        filtered = []
        for it in items:
            reasons = [str(r) for r in (it.get("reasons") or [])]

            # keep if any reason mentions spam (spam_phrases, spam_score, etc.)
            has_spam_reason = any("spam" in r.lower() for r in reasons)

            spam_score = _safe_float(it.get("spam_score", 0.0))
            # NOTE: 0.7 was too strict for many real cases
            if spam_score >= 0.5 or has_spam_reason:
                filtered.append(it)

        items = filtered

    # -------------------------
    # Build cards
    # -------------------------
    cards_html = []
    for it in items:
        spam_f = _safe_float(it.get("spam_score", 0))
        rel_f = _safe_float(it.get("relevance_score", 0))

        spam_pct = round(spam_f * 100)
        rel_pct = round(rel_f * 100)

        spam_class = "bad" if spam_f >= 0.7 else ("warn" if spam_f >= 0.35 else "")
        rel_class = "good" if rel_f >= 0.7 else ("warn" if rel_f <= 0.2 else "")

        reasons = ", ".join(it.get("reasons") or []) or "—"
        text_clean = _escape(_clean_comment_text(it.get("text")))

        cards_html.append(f"""
        <div class="draft">
          <div class="muted">
            <b class="card-title">{_escape(it.get("author")) or "Unknown"}</b>
            <span class="meta">{_escape(it.get("published_at")) or ""}</span>

            <span class="pill">intent: {_escape(str(it.get("category") or "—"))}</span>
            <span class="pill {rel_class}">relevance: {rel_pct}%</span>
            <span class="pill {spam_class}">spam: {spam_pct}%</span>
          </div>

          <div class="bubble" style="white-space:pre-wrap;">{text_clean}</div>

          <div class="muted" style="margin-top:10px;">
            <b>reasons:</b> {_escape(reasons)}
          </div>
        </div>
        """)

    # -------------------------
    # Toggle link UI (THIS was missing in your HTML)
    # -------------------------
    toggle_link = (
        "<a class='link' href='/ignored'>show all</a>"
        if only_high_spam
        else "<a class='link' href='/ignored?only_high_spam=1'>show high spam only</a>"
    )

    html = f"""
    <html>
      <head>
        <title>Ignored</title>
        <style>
{CSS_HOME_STYLES}
        </style>
      </head>

      <body>
        {_topbar(
            "Ignored / Low-value",
            "spam + low relevance comments (for visibility)",
            "ignored")}

        <div class="container">
          <div class="row" style="justify-content:space-between; align-items:center;">
            <div class="muted">Total ignored: <b>{len(items)}</b></div>
            <div>{toggle_link}</div>
          </div>

          {''.join(cards_html) if cards_html else """
            <div class="empty">
              <div class="empty-title">nothing to show</div>
              <div class="empty-subtitle">
                try <b>show high spam only</b>, or fetch more comments to generate ignored items.
              </div>
            </div>
          """}
        </div>
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

        err_file = (RUNTIME_DIR / "errors" / f"{d.comment_id}.json")
        err_msg = ""
        try:
            import json as _json
            err_msg = _json.loads(err_file.read_text(encoding="utf-8")).get("error", "")
        except Exception:
            err_msg = ""

        cards.append(f"""
<div class="draft">
  <div class="muted">
    <b class="card-title">{_escape(d.author) or "Unknown"}</b>
    <span class="pill bad">failed</span>
    <div class="meta" style="margin-top:6px;">failed to post • retry or reject</div>
  </div>

  <div class="bubble" style="white-space:pre-wrap;">{original}</div>

  <div class="danger-box"><b>error:</b> {_escape(err_msg) or "unknown error"}</div>

  <form method="post" action="/draft/{_escape(d.comment_id)}/retry" style="margin-top:12px;"
        onsubmit="return confirm('retry posting this reply?');">
    <div class="muted" style="margin-bottom:8px;">edit reply (optional)</div>
    <textarea name="edited_reply_text" rows="3" style="white-space:pre-wrap;">{reply}</textarea>

    <div class="controls">
      <button class="btn" type="submit">Retry Post</button>
      <button class="btn"
              formaction="/draft/{_escape(d.comment_id)}/reject"
              formmethod="post"
              onclick="return confirm('reject this failed draft?');">
        Reject
      </button>
    </div>
  </form>
</div>
""")

    html = f"""
    <html>
      <head>
        <title>Failed Posts</title>
        <style>
{CSS_HOME_STYLES}
        </style>
      </head>

      <body>
        {_topbar("Failed Posts",
         "replies that didn’t post successfully",
         "errors")}

        <div class="container">
          <div class="row">
            <div class="muted">Failures: <b>{len(errs)}</b></div>
          </div>

          {''.join(cards) if cards else """
            <div class="empty">
              <div class="empty-title">no failures 🎉</div>
              <div class="empty-subtitle">when a post fails, it will show up here with the error.</div>
            </div>
          """}
        </div>
      </body>
    </html>
    """
    return HTMLResponse(html)


@app.post("/draft/{comment_id}/approve")
def approve(comment_id: str, edited_reply_text: str | None = Form(None)):
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
def retry(comment_id: str, edited_reply_text: str | None = Form(None)):
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
def reject(comment_id: str, reason: str | None = Form(None)):    # allow reject from either pending or errors
    d = stores.get_pending(comment_id) or stores.get_error(comment_id)
    if not d:
        raise HTTPException(status_code=404, detail="Draft not found")

    metrics.inc("rejected", 1)
    stores.move_to_rejected(d, reason=reason)
    return RedirectResponse(url="/", status_code=303)

def _clean_comment_text(text: str | None) -> str:
    """
    Removes anchor tags + raw urls from triage text for nicer UI.
    """
    t = text or ""
    # remove <a ...>...</a>
    t = re.sub(r"<a\s+href=.*?>.*?</a>", "", t, flags=re.IGNORECASE)
    # remove raw urls
    t = re.sub(r"https?://\S+", "", t)
    # collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")

    return t

def _safe_float(x, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default
