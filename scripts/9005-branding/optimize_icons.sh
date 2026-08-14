#!/usr/bin/env bash
R=/home/gee/kiwi-rebase/build/chromium/src/chrome/android/java/res_chromium_base
BAK=/home/gee/kiwi-rebase/branding/icon_pngs_original
mkdir -p "$BAK"

vorher=0; nachher=0
for d in mdpi hdpi xhdpi xxhdpi xxxhdpi; do
  for n in app_icon layered_app_icon layered_app_icon_background; do
    f="$R/mipmap-$d/$n.png"
    [ -f "$f" ] || continue
    mkdir -p "$BAK/mipmap-$d"
    [ -f "$BAK/mipmap-$d/$n.png" ] || cp "$f" "$BAK/mipmap-$d/$n.png"
    a=$(stat -c%s "$f")
    pngquant --quality=80-98 --skip-if-larger --strip --force --output "$f" -- "$f" 2>/dev/null
    b=$(stat -c%s "$f")
    vorher=$((vorher+a)); nachher=$((nachher+b))
    printf '  %-8s %-28s %7d -> %7d\n' "$d" "$n" "$a" "$b"
  done
done
echo
echo "Summe: $vorher -> $nachher Bytes"
echo "Originale gesichert unter $BAK"