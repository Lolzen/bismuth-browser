#!/usr/bin/env bash
# Baut einen Chromium-Baum auf und wendet die Patch-Serie an.
# Aufruf: ./bootstrap.sh <zielverzeichnis>
set -e

DEST="${1:?Zielverzeichnis angeben, z.B. ~/bismuth-build}"
REPO="$(cd "$(dirname "$0")" && pwd)"
TAG="$(cat "$REPO/CHROMIUM_TARGET")"

echo "== Chromium $TAG nach $DEST =="
mkdir -p "$DEST"
cd "$DEST"

# --- depot_tools ---
if [ ! -d depot_tools ]; then
  git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
fi
export PATH="$DEST/depot_tools:$PATH"

# --- Checkout ---
mkdir -p chromium
cd chromium

if [ ! -f .gclient ]; then
  cat > .gclient <<GCLIENT
solutions = [
  {
    "name": "src",
    "url": "https://chromium.googlesource.com/chromium/src.git@$TAG",
    "managed": True,
    "custom_deps": {},
    "custom_vars": {
      "checkout_android": True,
    },
  },
]
target_os = ["android"]
GCLIENT
fi

echo "== gclient sync (dauert lange, HTTP 429 ist normal) =="
gclient sync --nohooks --no-history --jobs 4

echo "== gclient runhooks =="
gclient runhooks

# --- Patches ---
cd src
echo "== Patches =="
while read -r p; do
  [ -z "$p" ] && continue
  echo "-- $p"
  git apply --3way "$REPO/patches/$p"
done < "$REPO/patches/series"

# --- args.gn ---
mkdir -p out/Default
if [ ! -f out/Default/args.gn ]; then
  cp "$REPO/args.gn.template" out/Default/args.gn
  echo
  echo "args.gn aus Vorlage angelegt."
  echo "Vor dem Bauen die API-Key-Platzhalter ersetzen:"
  echo "  $DEST/chromium/src/out/Default/args.gn"
fi

echo
echo "== fertig =="
echo "cd $DEST/chromium/src"
echo "gn gen out/Default"
echo "autoninja -C out/Default chrome_public_apk"