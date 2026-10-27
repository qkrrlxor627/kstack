#!/usr/bin/env bash
# kstack 설치: 평가 가이드 → 기준 분석 → final-report 작업 환경을 대상 프로젝트에 복사한다.
#
# 사용: bash ~/kstack/install.sh <대상 프로젝트> [--author "이름 <email>"] [--project 이름] [--commit-config] [--force]
#   --author         커밋 작성자 표기 (기본: 대상 저장소의 git config user.name <user.email>)
#   --project        프로젝트 이름 (기본: 폴더 이름)
#   --commit-config  .claude/·CLAUDE.md·doc/workClaude.md를 .git/info/exclude에 넣지 않는다(저장소에 올릴 때)
#   --force          이미 있는 kstack 파일을 덮어쓴다 (doc/criteria/의 mission.md·standard.md·ids.md는 절대 덮지 않음)
set -euo pipefail

KSTACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$KSTACK_DIR/template"

die() { echo "kstack: $*" >&2; exit 1; }

[ $# -ge 1 ] || die "대상 프로젝트 경로가 필요합니다. 예: bash $0 ~/work/my-proj"
TARGET="$1"; shift
AUTHOR=""; PROJECT=""; COMMIT_CONFIG=0; FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --author) AUTHOR="${2:?--author 값이 필요합니다}"; shift 2 ;;
    --project) PROJECT="${2:?--project 값이 필요합니다}"; shift 2 ;;
    --commit-config) COMMIT_CONFIG=1; shift ;;
    --force) FORCE=1; shift ;;
    *) die "알 수 없는 옵션: $1" ;;
  esac
done

[ -d "$TARGET" ] || die "폴더가 없습니다: $TARGET"
TARGET="$(cd "$TARGET" && pwd)"
git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 || die "git 저장소가 아닙니다: $TARGET (git init 후 다시 실행)"
GIT_DIR="$(cd "$TARGET" && cd "$(git rev-parse --git-dir)" && pwd)"

if [ -z "$AUTHOR" ]; then
  name="$(git -C "$TARGET" config user.name || true)"; email="$(git -C "$TARGET" config user.email || true)"
  [ -n "$name" ] || die "--author를 주거나 대상 저장소에 git config user.name을 설정하세요"
  AUTHOR="$name${email:+ <$email>}"
fi
[ -n "$PROJECT" ] || PROJECT="$(basename "$TARGET")"

# 1. 충돌 확인 — 평가 가이드 원본은 어떤 경우에도 덮지 않는다
conflicts=()
while IFS= read -r rel; do
  [ -e "$TARGET/$rel" ] && conflicts+=("$rel")
done < <(cd "$TEMPLATE" && find . -type f ! -name '.DS_Store' | sed 's|^\./||' | sort)
if [ ${#conflicts[@]} -gt 0 ] && [ $FORCE -eq 0 ]; then
  printf '  %s\n' "${conflicts[@]}" >&2
  die "위 파일이 이미 있습니다. 덮어쓰려면 --force (기존 설정은 먼저 백업하세요)"
fi

# 2. 복사 + 자리표시자 치환
TODAY="$(date +%Y-%m-%d)"
esc() { printf '%s' "$1" | sed -e 's/[\/&|]/\\&/g'; }
while IFS= read -r rel; do
  mkdir -p "$TARGET/$(dirname "$rel")"
  sed -e "s|{{AUTHOR}}|$(esc "$AUTHOR")|g" \
      -e "s|{{PROJECT}}|$(esc "$PROJECT")|g" \
      -e "s|{{DATE}}|$TODAY|g" "$TEMPLATE/$rel" > "$TARGET/$rel"
done < <(cd "$TEMPLATE" && find . -type f ! -name '.DS_Store' ! -name '*.pyc' | sed 's|^\./||' | sort)
chmod +x "$TARGET"/.claude/hooks/*.py "$TARGET"/.claude/skills/*/scripts/*.py 2>/dev/null || true
mkdir -p "$TARGET/outputs/final-report"

# 3. 로컬 전용 처리 (이 과제와 같은 방식: 원격에 Claude 설정을 올리지 않음)
if [ $COMMIT_CONFIG -eq 0 ]; then
  EXCLUDE="$GIT_DIR/info/exclude"; mkdir -p "$(dirname "$EXCLUDE")"; touch "$EXCLUDE"
  for p in ".claude/" "CLAUDE.md" "doc/workClaude.md"; do
    grep -qxF "$p" "$EXCLUDE" || echo "$p" >> "$EXCLUDE"
  done
fi

cat <<EOF
kstack 설치 완료 → $TARGET
  프로젝트: $PROJECT / 작성자: $AUTHOR
  로컬 전용(.git/info/exclude): $([ $COMMIT_CONFIG -eq 0 ] && echo "예" || echo "아니오 (--commit-config)")

다음 할 일
  1. 평가 가이드를 넣는다: doc/criteria/mission.md, doc/criteria/standard.md  (doc/criteria/README.md 참고)
  2. 그 폴더에서 claude 실행 → /kstack-setup   (C/K ID 표 생성, 사람 확인)
  3. /improve v1 → (선택) /bench baseline → 코드 수정 → /report-step P1 … → /bench after → /final-report
EOF
