#!/usr/bin/env bash
echo "=== Blockgeraete ==="
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT,FSAVAIL,FSUSE%
echo
echo "=== aktuell gemountet ==="
mount | grep -E 'nvme|f2fs'
echo
echo "=== fstab ==="
grep -v '^#' /etc/fstab | grep -v '^$'