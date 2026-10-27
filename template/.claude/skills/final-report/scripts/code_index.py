#!/usr/bin/env python3
"""코드의 `[Px BEFORE]` / `[Px AFTER]` 주석을 모아 최종 코드 위치 색인(Markdown)을 만든다.

사용:
    python3 .claude/skills/final-report/scripts/code_index.py [--out 00_code_index.md] <폴더 또는 파일>...

주석 규칙: `# [P1 BEFORE] 설명`, `// [P2·N3 AFTER] 설명`, `<!-- [#14 AFTER] -->` 처럼
대괄호 안에 ID(여러 개면 ·로 연결)와 BEFORE/AFTER를 쓴다.
"""
import argparse
import re
import subprocess
from pathlib import Path

TAG = re.compile(r"\[((?:[A-Z]+\d+|#\d+)(?:[·,/](?:[A-Z]+\d+|#\d+))*) (BEFORE|AFTER)\]")
SKIP = {".git", ".venv", "node_modules", "__pycache__", ".claude", "outputs", "dist", "build"}


def files(paths: list[str]) -> list[Path]:
    out = []
    for p in map(Path, paths):
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out += [f for f in sorted(p.rglob("*")) if f.is_file() and not SKIP & set(f.parts)]
    return out


def head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


def sort_key(row):
    ids, kind, path, line, _ = row
    m = re.match(r"([A-Z#]+)(\d+)", ids)
    return (m.group(1), int(m.group(2))) if m else (ids, 0), path, line, kind


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    rows = []
    for f in files(args.paths):
        try:
            lines = f.read_text().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, text in enumerate(lines, 1):
            for m in TAG.finditer(text):
                note = text[m.end():].strip(" -#/*>─").strip() or text.strip()
                rows.append((m.group(1), m.group(2), f.as_posix(), n, note.replace("|", "\\|")))
    rows.sort(key=sort_key)
    md = [f"# 최종 코드 위치 색인 (HEAD {head()} 기준, 자동 생성)", "",
          "- 각 단계 문서의 `파일:줄`은 그 단계 커밋 당시 줄 번호다. 지금 위치는 이 표를 쓴다.",
          "- 직접 찾기: `grep -rn \"\\[P1 \" <소스 폴더>`", "",
          "| 문제 | 구분 | 위치 | 주석 내용 |", "|---|---|---|---|"]
    md += [f"| {i} | {k} | `{p}:{n}` | {t} |" for i, k, p, n, t in rows]
    md += ["", f"합계: {len(rows)}곳 / 문제 ID {len({r[0] for r in rows})}개"]
    text = "\n".join(md) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"저장: {args.out} ({len(rows)}곳)")
    else:
        print(text)


if __name__ == "__main__":
    main()
