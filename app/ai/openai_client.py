from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=BASE_DIR / ".env")


def _read_api_key_from_path(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def _extract_output_text(resp: Dict[str, Any]) -> str:
    # SDKs expose output_text; raw HTTP does not always include it.
    direct = resp.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct

    texts: List[str] = []
    for item in resp.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                text = part.get("text", "")
                if text:
                    texts.append(text)

    return "\n".join(texts).strip()


@dataclass
class OpenAIClient:
    model: str
    base_url: str | None = None
    api_key: str | None = None
    timeout_seconds: int = 60

    def __post_init__(self) -> None:
        if not self.base_url:
            self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            key_path = os.getenv("OPENAI_API_KEY_PATH")
            if key_path:
                self.api_key = _read_api_key_from_path(BASE_DIR / key_path)

        if not self.api_key:
            raise RuntimeError(
                "Missing OpenAI API key. Set OPENAI_API_KEY or OPENAI_API_KEY_PATH in .env."
            )

    def complete(self, system: str, user: str, max_output_tokens: int = 800) -> str:
        payload = {
            "model": self.model,
            "input": user,
            "max_output_tokens": int(max_output_tokens),
        }
        if system:
            payload["instructions"] = system

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(
            f"{self.base_url}/responses",
            json=payload,
            headers=headers,
            timeout=self.timeout_seconds,
        )

        if resp.status_code >= 400:
            raise RuntimeError(f"OpenAI API error {resp.status_code}: {resp.text}")

        data = resp.json()
        text = _extract_output_text(data)
        if not text:
            raise RuntimeError("OpenAI API returned no text output.")
        return text
