from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from oryon.core.utils.config_loader import load_config


def test_load_config_with_env_override(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump({"defaults": {"data_dir": "foo"}}, fh)
    monkeypatch.setenv("ORYON_DEFAULTS__DATA_DIR", "bar")
    config = load_config(config_path)
    assert config["defaults"]["data_dir"] == "bar"
