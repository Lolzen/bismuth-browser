#!/usr/bin/env bash
REP=/home/gee/kiwi-rebase/reports
for v in list-reference-138.0.7204.310 149-reference; do
  echo "=== $v ==="
  awk '/interface TabActionState/,/^    }/' "$REP/$v/TabProperties.java"
done