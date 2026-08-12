#!/usr/bin/env bash
set -e
N="${1:?Nummer, z.B. 9001}"
NAME="${2:?Kurzname, z.B. mv2-enabled}"
R=/home/gee/kiwi-rebase
S=$R/build/chromium/src
TAG=149.0.7827.238

cd "$S"
git checkout -f "$TAG"
git clean -fd --exclude=out
git switch -c "feat/$NAME" 2>/dev/null || git switch "feat/$NAME"

NOTE="$R/docs/port-notes/$N-$NAME.md"
mkdir -p "$R/docs/port-notes"

if [ ! -f "$NOTE" ]; then
cat > "$NOTE" <<NOTEEOF
# $N-$NAME

## Absicht

## Kiwis Umsetzung (105)
- Dateien:
- Hook-Stellen:

## Umsetzung in 149
- Hook-Stellen:
- Abweichungen und warum:

## Referenzversion

## Status
offen
NOTEEOF
fi

echo "Branch feat/$NAME bereit."
echo "Notiz: $NOTE"