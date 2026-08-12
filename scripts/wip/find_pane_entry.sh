#!/usr/bin/env bash
REP=/home/gee/kiwi-rebase/reports
echo "=== Pane-Klassen in 149 ==="
grep -i 'tabswitcherpane\|hubmanager\|/hub/' "$REP/upstream-target-paths.txt" | head -25
echo
echo "=== wo TabListMode konfiguriert werden koennte ==="
grep -E 'TabListCoordinator|TabListMode|TabListContainerProperties' "$REP/upstream-target-paths.txt"