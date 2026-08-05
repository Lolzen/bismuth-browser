#!/usr/bin/env bash
set -e
DEV=/dev/nvme0n1p2
MNT=/mnt/void
LOCAL=/home/gee/kiwi-rebase/build

sudo mkdir -p "$MNT"
mountpoint -q "$MNT" || sudo mount "$DEV" "$MNT"

UUID=$(sudo blkid -s UUID -o value "$DEV")
grep -q "$UUID" /etc/fstab || echo "UUID=$UUID $MNT f2fs defaults,users,exec 0 2" | sudo tee -a /etc/fstab

echo "=== Besitzverhaeltnisse dort ==="
ls -ldn "$MNT/home/gee"
echo "deine UID/GID hier: $(id -u):$(id -g)"

TARGET="$MNT/home/gee/kiwi-build"
mkdir -p "$TARGET"

rm -rf "$LOCAL"; mkdir -p "$LOCAL"
sudo mount --bind "$TARGET" "$LOCAL"
grep -q "$LOCAL" /etc/fstab || echo "$TARGET $LOCAL none bind 0 0" | sudo tee -a /etc/fstab

echo "=== Case-Sensitivity ==="
touch "$LOCAL/TestFile"
[ -e "$LOCAL/testfile" ] && echo "PROBLEM: case-insensitive" || echo "ok"
rm -f "$LOCAL/TestFile"

df -h "$LOCAL"