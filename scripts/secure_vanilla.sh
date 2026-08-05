#!/usr/bin/env bash
set -e
R=/home/gee/kiwi-rebase
S=$R/build/chromium/src
TAG=149.0.7827.238

mkdir -p "$R/artifacts" "$R/docs"
cp "$S/out/Vanilla/apks/ChromePublic.apk" "$R/artifacts/vanilla-$TAG.apk"
cp "$S/out/Vanilla/args.gn" "$R/args.gn.template"
echo "$TAG" > "$R/CHROMIUM_TARGET"

cd "$R"
[ -d .git ] || git init
grep -q '^artifacts/' .gitignore 2>/dev/null || echo 'artifacts/' >> .gitignore
grep -q '^build/' .gitignore 2>/dev/null || echo 'build/' >> .gitignore
git add -A
git commit -m "Phase 2: Vanilla-Build $TAG laeuft" || echo "nichts zu committen"
git tag -f "vanilla-$TAG"

ls -lh "$R/artifacts/"
git log --oneline -1