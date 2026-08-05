#!/usr/bin/env bash
F=/home/gee/kiwi-rebase/reports/149-reference/TabSwitcherPaneCoordinatorFactory.java
echo "=== Konstruktor / Modus-Zuweisung ==="
sed -n '140,165p' "$F"
echo
echo "=== getTabListMode ==="
sed -n '222,245p' "$F"