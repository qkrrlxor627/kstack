"""hook 공통: .claude/kstack.json 설정을 읽는다. 파일이 없거나 깨져 있으면 기본값을 쓴다."""
import json
import os
from pathlib import Path

DEFAULTS = {
    "author": "",
    "protected": ["doc/criteria/mission.md", "doc/criteria/standard.md"],
    "local_only": [".claude", "CLAUDE.md", "doc/workClaude.md"],
    "test": {"watch": [], "ext": [".py"], "cmd": "", "timeout": 90},
}


def project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()


def load() -> dict:
    cfg = dict(DEFAULTS)
    try:
        cfg.update(json.loads((project_root() / ".claude" / "kstack.json").read_text()))
    except (OSError, json.JSONDecodeError):
        pass
    return cfg
