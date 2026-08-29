#!/bin/sh
set -e
mkdir -p \
  "${HTML_LORE_CONTENT:-/data/content}" \
  "${HTML_LORE_META:-/data/meta}/items" \
  "${HTML_LORE_META:-/data/meta}/config" \
  "${HTML_LORE_PUBLIC:-/data/public}"
exec node server.js
