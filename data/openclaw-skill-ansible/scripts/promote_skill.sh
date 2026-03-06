#!/usr/bin/env bash
set -euo pipefail
SRC=$1
DEST=${2:-skills/local}
# simple promote: validate then move to dest and commit
./scripts/validate_skill.sh "$SRC"
NAME=$(basename "$SRC")
DESTDIR="$DEST/$NAME"
if [ -d "$DESTDIR" ]; then
  echo "Destination exists: $DESTDIR" && exit 1
fi
mkdir -p $(dirname "$DESTDIR")
mv "$SRC" "$DESTDIR"
# create a promotion commit
git add "$DESTDIR"
git commit -m "Promote skill $NAME to $DEST"

echo "Promoted $NAME to $DESTDIR"
