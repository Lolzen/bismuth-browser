#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/scripts
cd "$S" || exit 1
mkdir -p 9010-account-manager-delegate wip

move() {
  d="$1"; shift
  for f in "$@"; do
    [ -f "$f" ] && mv "$f" "$d/" && echo "$d/$f"
  done
}

# was zum Delegaten gehoert
move 9010-account-manager-delegate \
  find_delegate.sh fetch_delegate.sh add_delegate_build.py finish_delegate.py

# Sackgassen und nie angewendete Anlaeufe
move wip \
  enable_dice.py dice_guards.py dice_batchupload.py dice_batchupload2.py \
  dice_ui_guard.py fix_signin_crash.py use_account_chooser.py log_accounts.py

echo
echo "=== noch lose ==="
ls -p | grep -v /