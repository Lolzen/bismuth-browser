#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
export PATH="/home/gee/kiwi-rebase/build/depot_tools:$PATH"
cd "$S"

mkdir -p out/Vanilla
cat > out/Vanilla/args.gn <<'ARGS'
target_os = "android"
target_cpu = "arm64"

is_debug = false
is_official_build = false
symbol_level = 1
blink_symbol_level = 0

is_component_build = false
use_remoteexec = false

proprietary_codecs = true
ffmpeg_branding = "Chrome"
ARGS

gn gen out/Vanilla
gn args out/Vanilla --list --short --overrides-only