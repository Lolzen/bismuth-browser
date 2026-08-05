#!/usr/bin/env bash
git ls-remote --tags https://chromium.googlesource.com/chromium/src '149.0.7827.*' | awk '{print $2}' | sed 's|refs/tags/||' | sort -V | tail -5