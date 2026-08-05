#!/usr/bin/env bash
echo "=== Distribution ==="
cat /etc/os-release | grep -E '^(NAME|VERSION|ID)='
echo
echo "=== Basiswerkzeuge ==="
for t in git curl python3 pkg-config gperf ninja cmake unzip zip xz rsync bzip2 lsb_release ccache; do
  printf '%-14s ' "$t"
  command -v "$t" >/dev/null && echo ok || echo FEHLT
done
echo
echo "=== Python ==="
python3 --version
echo "which python3: $(command -v python3)"
echo
echo "=== Java (nur falls Chromium kein eigenes mitbringt) ==="
command -v java >/dev/null && java -version 2>&1 | head -1 || echo "kein System-Java"
ls -d /home/gee/kiwi-rebase/build/chromium/src/third_party/jdk/current 2>/dev/null && echo "-> Chromium bringt eigenes JDK mit"