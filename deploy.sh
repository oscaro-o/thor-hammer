#!/usr/bin/env bash
# Deploy the game to the VPS.
#
#   ./deploy.sh                     # deploy to the default target
#   ./deploy.sh /some/other/path    # deploy somewhere else
#
# Requires the `hetu` host alias in ~/.ssh/config (see README).

set -euo pipefail

HOST_ALIAS="${HOST_ALIAS:-hetu}"
TARGET="${1:-/home/hetu.trilumi.xyz/public_html/hammer}"

cd "$(dirname "$0")"

# sanity checks before touching the server
[ -f index.html ] || { echo "!! index.html not found — run this from the repo root"; exit 1; }
case "$TARGET" in
  ""|"/"|"/home"|"/var"|"/var/www") echo "!! refusing to deploy to '$TARGET'"; exit 1 ;;
esac

FILES=(index.html)
[ -f og.png ] && FILES+=(og.png)

echo "→ host    : $HOST_ALIAS"
echo "→ target  : $TARGET"
echo "→ files   : ${FILES[*]}"
echo

tar czf - "${FILES[@]}" | ssh -o ConnectTimeout=15 "$HOST_ALIAS" \
  "mkdir -p '$TARGET' && tar xzf - -C '$TARGET' && echo && ls -la '$TARGET'"

# derive the public URL from the filesystem path: /home/<domain>/public_html[/sub]
DOMAIN=$(printf '%s' "$TARGET" | sed -nE 's#^/home/([^/]+)/public_html.*#\1#p')
SUB=$(printf '%s' "$TARGET" | sed -nE 's#^/home/[^/]+/public_html/?(.*)$#\1#p')
URL="https://${DOMAIN}/${SUB}"

echo
echo "✓ deployed"
if [ -n "$DOMAIN" ]; then
  printf '  %s → ' "$URL"
  curl -s -o /dev/null -w 'HTTP %{http_code}  %{size_download} bytes\n' "$URL" || echo "(could not reach it yet)"
fi
