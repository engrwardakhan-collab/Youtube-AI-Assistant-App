from __future__ import annotations

import json
from typing import List, Dict, Any, Tuple

from app.ai.types import DraftReply, CommentCategory


SYSTEM_PROMPT = """
Draft short, polite, human YouTube replies for the channel owner.

Rules:
- Never invent facts; if unsure, ask ONE question.
- Never ask for contact info.
- If medical, legal, financial, abusive, hate, or threat content → needs_human=true.
- Output ONLY valid JSON (no markdown, no prose).

Input: list of comments.
Output: JSON array (same length), each item:
comment_id, reply_text, category (question|complaint|praise|other), confidence (0..1), needs_human (bool), reasons[].

"""


def _make_user_prompt(comments: List[Any]) -> str:
    # comments are your existing fetched comment objects from app.youtube.model
    lines = ["Draft replies for these comments:\n"]
    for i, c in enumerate(comments, start=1):
        text = (c.text or "").strip().replace("\n", " ")
        if len(text) > 300:
            text = text[:300] + "..."
        lines.append(f"{i}) comment_id: {c.comment_id}")
        lines.append(f"   author: {c.author}")
        lines.append(f"   text: {text}")
        lines.append("")
    lines.append("Return ONLY JSON array.")
    return "\n".join(lines)


def batch_draft_replies(
    comments: List[Any],
    openai_client,
) -> Tuple[List[DraftReply], List[Dict[str, Any]]]:
    """
    Returns:
      drafts: List[DraftReply]
      failures: list of {comment_id, error, raw}
    """
    if not comments:
        return [], []

    raw = openai_client.complete(
        system=SYSTEM_PROMPT,
        user=_make_user_prompt(comments),
        max_output_tokens=200,
    ).strip()

    failures: List[Dict[str, Any]] = []

    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("LLM output is not a JSON array")
    except Exception as e:
        # If batch fails, fail all items (but still return usable failure info)
        for c in comments:
            failures.append({"comment_id": c.comment_id, "error": f"batch_json_parse_failed:{e}", "raw": raw})
        return [], failures

    # Map drafts by comment_id for robustness
    drafts: List[DraftReply] = []
    by_id = {c.comment_id: c for c in comments}

    for item in data:
        try:
            cid = str(item.get("comment_id", "")).strip()
            if cid not in by_id:
                raise ValueError("unknown_comment_id_returned")

            draft = DraftReply(
                comment_id=cid,
                reply_text=str(item.get("reply_text", "")).strip(),
                category=CommentCategory(str(item.get("category", "other")).strip()),
                confidence=float(item.get("confidence", 0.5)),
                needs_human=bool(item.get("needs_human", True)),
                reasons=list(item.get("reasons", [])),
            )

            # Guardrails
            if not draft.reply_text:
                draft.reply_text = "Thanks for your comment! Can you clarify a bit so I can help accurately?"
                draft.needs_human = True
                draft.reasons.append("empty_reply_text")

            if draft.confidence < 0.55:
                draft.needs_human = True
                draft.reasons.append("low_confidence")

            drafts.append(draft)

        except Exception as e:
            failures.append({"comment_id": item.get("comment_id", None), "error": f"item_parse_failed:{e}", "raw": item})

    # If model missed some comment_ids, record failures
    drafted_ids = {d.comment_id for d in drafts}
    missing = [c.comment_id for c in comments if c.comment_id not in drafted_ids]
    for cid in missing:
        failures.append({"comment_id": cid, "error": "missing_from_batch_output", "raw": raw})

    return drafts, failures
