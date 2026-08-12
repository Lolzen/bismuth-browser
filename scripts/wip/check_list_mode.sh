#!/usr/bin/env bash
F=/home/gee/kiwi-rebase/reports/149-reference/TabListCoordinator.java
echo "=== Enum-Definition ==="
grep -n -A12 'TabListMode' "$F" | head -30
echo
echo "=== LIST-Verwendungen ==="
grep -n 'TabListMode.LIST\|== LIST\|case LIST\|MODE_LIST' "$F"
echo
echo "=== Layout-Auswahl nach Modus ==="
grep -n 'LinearLayoutManager\|GridLayoutManager\|setLayoutManager' "$F"