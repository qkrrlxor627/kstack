#!/usr/bin/env python3
"""PostToolUse(Edit|Write) hook — 감시 폴더의 코드를 고친 직후 단위 테스트를 돌린다.

감시 폴더·확장자·명령은 .claude/kstack.json의 test(watch, ext, cmd, timeout)에서 읽는다.
watch나 cmd가 비어 있으면 아무것도 하지 않는다.
통과하면 조용히 exit 0. 실패하면 실패 요약을 stderr에 쓰고 exit 2 → Claude가 결과를 받아
바로 고칠 수 있다(파일 수정은 이미 끝난 뒤라 되돌리지는 않는다).
"""
import json
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _kstack  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    test = _kstack.load()["test"]
    watch, cmd = tuple(test.get("watch") or ()), test.get("cmd") or ""
    if not watch or not cmd:
        return 0
    root = _kstack.project_root()
    path = (data.get("tool_input") or {}).get("file_path") or ""
    try:
        rel = Path(path).resolve().relative_to(root).as_posix()
    except ValueError:
        return 0   # 프로젝트 밖 파일
    if not (rel.endswith(tuple(test.get("ext") or (".py",))) and rel.startswith(watch)):
        return 0

    argv = shlex.split(cmd)
    venv_python = root / ".venv" / "bin" / "python3"
    if argv[0] in ("python", "python3") and venv_python.exists():
        argv[0] = str(venv_python)
    timeout = test.get("timeout", 90)
    try:
        proc = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[auto_pytest] 테스트가 {timeout}초 안에 끝나지 않았습니다.", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"[auto_pytest] 테스트 명령을 실행할 수 없습니다: {e}. kstack.json의 test.cmd를 확인하세요.", file=sys.stderr)
        return 0
    if proc.returncode == 0:
        return 0
    tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-25:])
    print(f"[auto_pytest] {rel} 수정 후 단위 테스트 실패:\n{tail}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
