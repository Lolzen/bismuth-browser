for f in $(git -C /home/gee/kiwi-rebase/upstream/src.next ls-tree -r --name-only b2a61e552c94 \
           | grep -Ev '\.(png|jpg|webp|ico|ttf|zip|jar|so)$' | shuf -n 30); do
  curl -sf "https://chromium.googlesource.com/chromium/src/+/refs/tags/105.0.5195.24/$f?format=TEXT" \
    -o /tmp/b64 || { echo "MISSING  $f"; continue; }
  base64 -d < /tmp/b64 > /tmp/remote
  cmp -s /tmp/remote "$f" && echo "MATCH    $f" || echo "DIFF     $f"
  sleep 0.15
done