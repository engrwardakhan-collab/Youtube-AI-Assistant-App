from pathlib import Path
from app.ai.triage_engine import TriageConfig, CommentTriageEngine, TriageResult

_DEFAULT_CFG = Path("runtime/triage_rules.json")
_FALLBACK_CFG = Path("runtime/triage.rules")
_CFG_PATH = _DEFAULT_CFG if _DEFAULT_CFG.exists() else _FALLBACK_CFG
if not _CFG_PATH.exists():
    raise FileNotFoundError(
        "Missing triage config. Expected one of: "
        f"{_DEFAULT_CFG.as_posix()} or {_FALLBACK_CFG.as_posix()}"
    )
_CFG = TriageConfig.load(_CFG_PATH)
_ENGINE = CommentTriageEngine(_CFG)

def triage_comment(comment) -> TriageResult:
    # Uses ONLY comment.text → works with your existing YouTube comment object
    return _ENGINE.triage_text(comment.text)
