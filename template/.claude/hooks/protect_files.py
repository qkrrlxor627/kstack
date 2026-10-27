#!/usr/bin/env python3
"""PreToolUse(Bash) hook — 평가 가이드(미션·기준표) 원본을 Bash로 바꾸지 못하게 막는다.

settings.json의 deny Edit(...)는 Edit 도구만 막는다. 이 hook은 그 빈틈(Bash의 >, sed -i,
mv, rm 등)을 막는다. 읽기(cat, grep, sed -n)는 통과시킨다.
보호 대상은 .claude/kstack.json의 protected에서 읽는다.
차단: stderr에 이유 + exit 2 / 통과: exit 0
"""
import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _kstack  # noqa: E402

PROTECTED = tuple(_kstack.load()["protected"])
NAMES = tuple(p.split("/")[-1] for p in PROTECTED)   # 상대경로로 cd 후 써도 잡히도록 파일명으로 비교


def hits(token: str) -> bool:
    return bool(NAMES) and token.strip("'\"").endswith(NAMES)


def check(command: str) -> str | None:
    # 리다이렉션으로 덮어쓰기/덧붙이기: ... > doc/criteria/mission.md
    for m in re.finditer(r">>?\s*(\S+)", command):
        if hits(m.group(1)):
            return f"리다이렉션(>)으로 {m.group(1)}에 쓸 수 없습니다"
    for part in re.split(r"&&|\|\||;|\|", command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        if not tokens:
            continue
        cmd, args = tokens[0], tokens[1:]
        targets = [a for a in args if hits(a)]
        if not targets:
            continue
        if cmd in ("rm", "mv", "truncate", "tee", "dd", "chmod", "unlink"):
            return f"{cmd}로 원본 {targets[0]}을 바꿀 수 없습니다"
        if cmd in ("sed", "perl") and any(a.startswith("-i") for a in args):
            return f"{cmd} -i로 원본 {targets[0]}을 바꿀 수 없습니다"
        if cmd == "cp" and hits(args[-1]):
            return f"cp로 원본 {args[-1]}을 덮어쓸 수 없습니다"
        if cmd == "git" and args[:1] and args[0] in ("rm", "mv", "checkout", "restore"):
            return f"git {args[0]}로 원본 {targets[0]}을 바꿀 수 없습니다"
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    reason = check((data.get("tool_input") or {}).get("command") or "")
    if reason:
        print(f"[protect_files] 차단: {reason}. 평가 가이드는 원본 보존 대상입니다(CLAUDE.md). "
              "내용을 바꾸려면 사용자에게 직접 수정을 요청하세요.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
