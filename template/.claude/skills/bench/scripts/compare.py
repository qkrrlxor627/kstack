#!/usr/bin/env python3
"""두 측정 요약 CSV를 키 열(쿼리 id 등) 기준으로 비교해 Markdown 표를 만든다.

사용:
    python3 .claude/skills/bench/scripts/compare.py <before.csv> <after.csv> \
        [--key id] [--ignore started_at,...] [--out compare.md] [--labels baseline,after]

- 숫자 열: `before → after (차이)`로 쓰고, 값이 바뀌면 ⚠️를 붙인다.
- 문자 열: 바뀌면 `before → after ⚠️`, 같으면 값 하나만 쓴다.
- 숫자 열은 맨 위 "전체" 표에 중앙값을 따로 보여 준다.
값은 CSV에 기록된 것만 쓴다 — 계산(차이·중앙값) 외에 추정치를 넣지 않는다.
"""
import argparse
import csv
import statistics
from pathlib import Path


def load(path: Path, key: str) -> tuple[list[str], dict[str, dict]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        if key not in cols:
            raise SystemExit(f"{path}: 키 열 '{key}'이 없습니다. 열: {', '.join(cols)}")
        return cols, {row[key]: row for row in reader}


def num(v: str | None) -> float | None:
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def fmt(x: float) -> str:
    return str(int(x)) if x == int(x) else f"{x:.3f}".rstrip("0").rstrip(".")


def cell(b: str | None, a: str | None) -> str:
    if b is None or a is None:
        return f"{b if b is not None else '없음'} → {a if a is not None else '없음'} ⚠️"
    nb, na = num(b), num(a)
    if nb is not None and na is not None:
        if nb == na:
            return fmt(nb)
        return f"{fmt(nb)} → {fmt(na)} ({'+' if na > nb else ''}{fmt(na - nb)}) ⚠️"
    return b if b == a else f"{b} → {a} ⚠️"


def render(bl: str, al: str, key: str, cols: list[str], before: dict, after: dict) -> str:
    numeric = [c for c in cols if c != key and all(num(r.get(c)) is not None
                                                   for r in list(before.values()) + list(after.values()) if r.get(c))]
    lines = [f"# 비교: `{al}` vs `{bl}`", "", "## 전체 (숫자 열 중앙값)", "",
             f"| 지표 | {bl} | {al} | 차이 |", "|---|---|---|---|"]
    for c in numeric:
        bv = [num(r[c]) for r in before.values() if num(r.get(c)) is not None]
        av = [num(r[c]) for r in after.values() if num(r.get(c)) is not None]
        if bv and av:
            mb, ma = statistics.median(bv), statistics.median(av)
            lines.append(f"| {c} | {fmt(mb)} | {fmt(ma)} | {'+' if ma > mb else ''}{fmt(ma - mb)}{' ⚠️' if ma != mb else ''} |")
    lines += ["", f"## {key}별 (⚠️ = 바뀐 값)", "",
              "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    changed = 0
    for k in sorted(set(before) | set(after)):
        b, a = before.get(k, {}), after.get(k, {})
        cells = [k] + [cell(b.get(c) if b else None, a.get(c) if a else None) for c in cols if c != key]
        changed += any("⚠️" in x for x in cells)
        lines.append("| " + " | ".join(x.replace("|", "\\|") for x in cells) + " |")
    lines += ["", f"바뀐 행: {changed} / {len(set(before) | set(after))}"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("--key", default="id")
    ap.add_argument("--ignore", default="", help="비교에서 뺄 열(쉼표 구분)")
    ap.add_argument("--labels", default="", help="표에 쓸 이름 before,after (기본: 파일 이름)")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    bcols, before = load(args.before, args.key)
    acols, after = load(args.after, args.key)
    ignore = {c for c in args.ignore.split(",") if c}
    cols = [c for c in bcols if c not in ignore] + [c for c in acols if c not in bcols and c not in ignore]
    bl, al = (args.labels.split(",") + ["", ""])[:2]
    md = render(bl or args.before.stem, al or args.after.stem, args.key, cols, before, after)
    print(md)
    if args.out:
        args.out.write_text(md)
        print(f"저장: {args.out}")


if __name__ == "__main__":
    main()
