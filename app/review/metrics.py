from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


class Metrics:
    def __init__(self, path: Path = Path("runtime/metrics.json")):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({}, indent=2), encoding="utf-8")

    def inc(self, key: str, n: int = 1) -> None:
        data = self._read()
        data[key] = int(data.get(key, 0)) + n
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _read(self) -> Dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}
