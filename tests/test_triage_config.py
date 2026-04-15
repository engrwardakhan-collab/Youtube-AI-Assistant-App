import importlib
import os
from pathlib import Path
import pytest


def _make_empty_rules(path: Path):
    path.write_text("{}")


def test_triage_fails_without_config(tmp_path, monkeypatch):
    # Ensure no config files exist in any of the search paths
    monkeypatch.chdir(tmp_path)
    # remove any stray directories
    for sub in ["config", "app/config", "runtime"]:
        (tmp_path / sub).mkdir(parents=True, exist_ok=True)

    # Reload module to trigger import-time search
    import app.ai.triage as triage_mod
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        importlib.reload(triage_mod)


def test_triage_loads_from_root_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    _make_empty_rules(cfg_dir / "triage_rules.json")

    import app.ai.triage as triage_mod
    importlib.reload(triage_mod)  # should not raise


def test_triage_loads_from_app_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "app" / "config"
    cfg_dir.mkdir(parents=True)
    _make_empty_rules(cfg_dir / "triage_rules.json")

    import app.ai.triage as triage_mod
    importlib.reload(triage_mod)  # should not raise


def test_triage_loads_from_runtime(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "runtime"
    cfg_dir.mkdir()
    _make_empty_rules(cfg_dir / "triage_rules.json")

    import app.ai.triage as triage_mod
    importlib.reload(triage_mod)  # should not raise
