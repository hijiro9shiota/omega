"""Configuration loader merging defaults with overrides."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: Path | str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}
    overrides = _env_overrides(prefix="ORYON_")
    return _merge_dict(config, overrides)


def _env_overrides(prefix: str) -> Dict[str, Any]:
    overrides: Dict[str, Any] = {}
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        normalized = key[len(prefix):].lower().replace("__", ".")
        _assign(overrides, normalized.split("."), value)
    return overrides


def _assign(container: Dict[str, Any], keys: list[str], value: Any) -> None:
    key = keys[0]
    if len(keys) == 1:
        container[key] = value
        return
    container.setdefault(key, {})
    _assign(container[key], keys[1:], value)


def _merge_dict(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = value
    return result
