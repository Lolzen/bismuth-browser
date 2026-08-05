cd /home/gee/kiwi-rebase/upstream/src.next
#!/usr/bin/env bash
for f in $(git diff --diff-filter=D --name-only b2a61e552c94..kiwi); do
  n="$(printf '%s' "$f" | tr '/' '_')"
  [ -s "/home/gee/kiwi-rebase/patches/by-file/$n.patch" ] \
    || echo "FEHLT/LEER: $f"
done