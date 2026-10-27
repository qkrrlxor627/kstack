#!/usr/bin/env bash
# kstack 자체 점검: 임시 저장소에 설치 → 파일·치환·hook·스크립트 동작을 확인한다.
set -uo pipefail
KSTACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
P="$TMP/proj"; mkdir -p "$P"; git -C "$P" init -q
pass=0; fail=0
ok()  { echo "  ok   $1"; pass=$((pass+1)); }
bad() { echo "  FAIL $1"; fail=$((fail+1)); }
expect() { # expect <설명> <기대 exit> <명령...>
  local d="$1" want="$2"; shift 2
  "$@" >/dev/null 2>&1; local got=$?
  [ "$got" = "$want" ] && ok "$d" || bad "$d (exit $got, 기대 $want)"
}
hook() { # hook <스크립트> <JSON>
  (cd "$P" && printf '%s' "$2" | CLAUDE_PROJECT_DIR="$P" python3 ".claude/hooks/$1")
}

echo "[설치]"
expect "install.sh 실행" 0 bash "$KSTACK_DIR/install.sh" "$P" --author "테스트 <t@example.com>" --project demo
expect "재설치는 거부" 1 bash "$KSTACK_DIR/install.sh" "$P" --author "x"
expect "--force 재설치" 0 bash "$KSTACK_DIR/install.sh" "$P" --author "테스트 <t@example.com>" --project demo --force
expect "git 저장소 아니면 거부" 1 bash "$KSTACK_DIR/install.sh" "$TMP" --author "x"
grep -q "테스트 <t@example.com>" "$P/CLAUDE.md" && ok "CLAUDE.md 작성자 치환" || bad "CLAUDE.md 작성자 치환"
grep -q '"project": "demo"' "$P/.claude/kstack.json" && ok "kstack.json 프로젝트 치환" || bad "kstack.json 프로젝트 치환"
! grep -rq "{{" "$P/CLAUDE.md" "$P/.claude/kstack.json" "$P/doc/workClaude.md" && ok "자리표시자 남지 않음" || bad "자리표시자 남음"
[ "$(grep -c '^CLAUDE.md$' "$P/.git/info/exclude")" = 1 ] && ok "exclude 중복 없이 추가" || bad "exclude"
for f in .claude/settings.json .claude/kstack.json; do
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$P/$f" && ok "$f JSON 유효" || bad "$f JSON"
done
for s in "$P"/.claude/skills/*/SKILL.md "$P"/.claude/agents/*.md; do
  head -1 "$s" | grep -q '^---$' && grep -q '^name:' "$s" && grep -q '^description:' "$s" \
    && ok "frontmatter $(basename "$(dirname "$s")")/$(basename "$s")" || bad "frontmatter $s"
done

echo "[protect_files]"
expect "> 로 원본 쓰기 차단" 2 hook protect_files.py '{"tool_input":{"command":"echo x > doc/criteria/mission.md"}}'
expect "sed -i 차단" 2 hook protect_files.py '{"tool_input":{"command":"sed -i s/a/b/ doc/criteria/standard.md"}}'
expect "cat 통과" 0 hook protect_files.py '{"tool_input":{"command":"cat doc/criteria/mission.md"}}'
expect "다른 파일 쓰기 통과" 0 hook protect_files.py '{"tool_input":{"command":"echo x > outputs/a.md"}}'

echo "[git_guard]"
expect "Co-Authored-By 커밋 차단" 2 hook git_guard.py '{"tool_input":{"command":"git commit -m \"x\n\nCo-Authored-By: Claude <noreply@anthropic.com>\""}}'
expect "--author 차단" 2 hook git_guard.py '{"tool_input":{"command":"git commit --author=x -m y"}}'
expect "git add CLAUDE.md 차단" 2 hook git_guard.py '{"tool_input":{"command":"git add CLAUDE.md"}}'
expect "git add .claude 차단" 2 hook git_guard.py '{"tool_input":{"command":"git add .claude"}}'
expect "git add doc/workClaude.md 차단" 2 hook git_guard.py '{"tool_input":{"command":"git add doc/workClaude.md"}}'
expect "일반 커밋 통과" 0 hook git_guard.py '{"tool_input":{"command":"git add src/a.py && git commit -m \"fix: a\""}}'

echo "[auto_pytest]"
expect "기본값(watch·cmd 비어 있음)은 통과" 0 hook auto_pytest.py "{\"tool_input\":{\"file_path\":\"$P/src/a.py\"}}"
python3 - "$P/.claude/kstack.json" <<'PY'
import json, sys
p = sys.argv[1]; c = json.load(open(p))
c["test"].update(watch=["src/"], cmd="false"); json.dump(c, open(p, "w"))
PY
expect "테스트 실패 시 2" 2 hook auto_pytest.py "{\"tool_input\":{\"file_path\":\"$P/src/a.py\"}}"
expect "감시 밖 파일은 통과" 0 hook auto_pytest.py "{\"tool_input\":{\"file_path\":\"$P/README.md\"}}"

echo "[scripts]"
printf 'id,ms,label\nq1,100,a\nq2,200,b\n' > "$TMP/b.csv"
printf 'id,ms,label\nq1,50,a\nq2,200,c\n' > "$TMP/a.csv"
out="$(python3 "$P/.claude/skills/bench/scripts/compare.py" "$TMP/b.csv" "$TMP/a.csv" --labels before,after)"
echo "$out" | grep -q "100 → 50 (-50) ⚠️" && echo "$out" | grep -q "b → c ⚠️" && echo "$out" | grep -q "바뀐 행: 2 / 2" \
  && ok "compare.py" || bad "compare.py"
mkdir -p "$P/src"; printf '# [P1 BEFORE] old\n# [P1·#2 AFTER] new\n' > "$P/src/a.py"
(cd "$P" && python3 .claude/skills/final-report/scripts/code_index.py src) | grep -q '`src/a.py:2`' \
  && ok "code_index.py" || bad "code_index.py"

echo "결과: $pass passed, $fail failed"
[ $fail -eq 0 ]
