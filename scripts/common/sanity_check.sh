#!/usr/bin/env bash
SRC=/home/gee/kiwi-rebase/upstream/src.next
PDIR=/home/gee/kiwi-rebase/patches/by-file
WT=/tmp/kiwi-sanity

git -C "$SRC" worktree remove --force "$WT" 2>/dev/null
rm -rf "$WT"
git -C "$SRC" worktree add --detach "$WT" b2a61e552c94 || exit 1

cd "$WT" || exit 1
ok=0; fail=0
while IFS= read -r p; do
  if git apply --3way --whitespace=nowarn "$p" 2>/dev/null; then
    ok=$((ok+1))
  else
    fail=$((fail+1)); echo "FAIL $(basename "$p")"
  fi
done < <(find "$PDIR" -maxdepth 1 -name '*.patch' | LC_ALL=C sort)

echo "ok=$ok fail=$fail   (erwartet: ok=577 fail=0)"
echo "--- Vollstaendigkeitsbeweis ---"
git add -A >/dev/null 2>&1
git diff --cached --shortstat
echo "erwartet: 577 files changed, 13806 insertions(+), 834 deletions(-)"