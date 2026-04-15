from pathlib import Path
from app.ai.triage_engine import TriageConfig, CommentTriageEngine, TriageResult

# the triage configuration can live in a few different locations depending on
# how the project is set up. historically it lived in `runtime/`, but some
# workflows keep it under `app/config` and others under a top‑level `config`
# directory. check all of the candidates and pick the first one that exists.
_SEARCH_PATHS = [
    Path("config/triage_rules.json"),       # root-level config dir
    Path("app/config/triage_rules.json"),   # module-local config
    # Path("runtime/triage_rules.json"),      # legacy runtime location
    # Path("runtime/triage.rules"),           # older format
]
_CFG_PATH = next((p for p in _SEARCH_PATHS if p.exists()), None)
if _CFG_PATH is None:
    raise FileNotFoundError(
        "Missing triage config. Expected one of: "
        + ", ".join(p.as_posix() for p in _SEARCH_PATHS)
    )

_CFG = TriageConfig.load(_CFG_PATH)
_ENGINE = CommentTriageEngine(_CFG)

def triage_comment(comment) -> TriageResult:
    # Uses ONLY comment.text → works with your existing YouTube comment object
    return _ENGINE.triage_text(comment.text)
