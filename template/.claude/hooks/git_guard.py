#!/usr/bin/env python3
"""PreToolUse(Bash) hook — 기여자는 사람 작성자만, Claude 설정은 원격에 올리지 않는다.

하네스가 Bash 명령 실행 직전에 stdin으로 JSON을 넘긴다:
  {"tool_name": "Bash", "tool_input": {"command": "..."}, ...}
차단하려면 stderr에 이유를 쓰고 exit 2 — Claude는 그 이유를 받아 명령을 고친다.
통과는 exit 0.
로컬 전용 경로와 작성자는 .claude/kstack.json의 local_only, author에서 읽는다.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _kstack  # noqa: E402

CFG = _kstack.load()
AUTHOR = CFG.get("author") or "저장소 git config의 작성자"
# 업로드 금지 경로 (.git/info/exclude와 같은 대상)
_names = "|".join(re.escape(p.rstrip("/")) for p in CFG["local_only"])
LOCAL_ONLY = re.compile(rf"(^|[\s/'\"])({_names})(/|\s|$|['\"])") if _names else None
# Claude 공동 작성자·생성 표기
ATTRIBUTION = re.compile(r"co-authored-by|generated with \[?claude|noreply@anthropic\.com", re.I)


def check(command: str) -> str | None:
    # 체인(&&, ;, |)으로 묶인 명령도 각각 검사한다
    for part in re.split(r"&&|\|\||;|\|", command):
        part = part.strip()
        if not re.search(r"\bgit\b", part):
            continue
        if re.search(r"\bgit\b.*\badd\b", part):
            if re.search(r"(\s-f\b|\s--force\b)", part):
                return "git add -f/--force는 금지입니다. ignore된 로컬 전용 파일이 올라갈 수 있습니다."
            if LOCAL_ONLY and LOCAL_ONLY.search(part + " "):
                return f"{', '.join(CFG['local_only'])}는 로컬 전용이라 git add 할 수 없습니다. 경로에서 빼고 다시 실행하세요."
        if re.search(r"\bgit\b.*\b(commit|tag)\b", part):
            if ATTRIBUTION.search(part):
                return f"커밋/태그 메시지에 Claude 공동 작성자·생성 표기(Co-Authored-By 등)를 넣을 수 없습니다. 작성자는 {AUTHOR}입니다."
            if re.search(r"--author\b", part):
                return f"--author로 작성자를 바꿀 수 없습니다. 작성자는 저장소 git config({AUTHOR})로 고정입니다."
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0   # 입력이 이상하면 막지 않는다 (hook이 작업 전체를 멈추지 않도록)
    reason = check((data.get("tool_input") or {}).get("command") or "")
    if reason:
        print(f"[git_guard] 차단: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
