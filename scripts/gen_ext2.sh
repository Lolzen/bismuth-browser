#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
export PATH="/home/gee/kiwi-rebase/build/depot_tools:$PATH"
cd "$S"

cat > out/Ext/args.gn <<'ARGS'
target_os = "android"
target_cpu = "arm64"

is_debug = false
is_official_build = false
symbol_level = 1
blink_symbol_level = 0

is_component_build = false
use_remoteexec = false

dcheck_always_on = false
treat_warnings_as_errors = false
disable_android_lint = true

is_desktop_android = true
enable_service_discovery = false

proprietary_codecs = true
ffmpeg_branding = "Chrome"

cc_wrapper = "ccache"
ARGS

gn gen out/Ext
gn args out/Ext --list --short | grep -iE "desktop_android|enable_extensions|dcheck"