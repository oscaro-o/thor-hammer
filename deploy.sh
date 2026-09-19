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

# --- sanity checks before touching the server -------------------------------
[ -f index.html ] || { echo "!! index.html not found — run this from the repo root"; exit 1; }
case "$TARGET" in
  ""|"/"|"/home"|"/var"|"/var/www") echo "!! refusing to deploy to '$TARGET'"; exit 1 ;;
esac
case "$TARGET" in
  /home/*/public_html*) : ;;
  *) echo "!! target should live under /home/<domain>/public_html — got '$TARGET'"; exit 1 ;;
esac

FILES=(index.html)
[ -f og.png ] && FILES+=(og.png)

echo "→ host    : $HOST_ALIAS"
echo "→ target  : $TARGET"
echo "→ files   : ${FILES[*]}"
echo

# --- upload -----------------------------------------------------------------
# tar over ssh: no rsync needed on either end. Ownership is copied from the
# parent directory so LiteSpeed can actually read what we drop in.
tar czf - "${FILES[@]}" | ssh -o ConnectTimeout=15 "$HOST_ALIAS" "
  set -e
  mkdir -p '$TARGET'
  tar xzf - -C '$TARGET'
  OWNER=\$(stat -c '%U:%G' \"\$(dirname '$TARGET')\")
  chown -R \"\$OWNER\" '$TARGET'
  find '$TARGET' -type d -exec chmod 755 {} +
  find '$TARGET' -type f -exec chmod 644 {} +
  echo
  ls -la '$TARGET'
"

# --- report the live URL ----------------------------------------------------
DOMAIN=$(printf '%s' "$TARGET" | sed -nE 's#^/home/([^/]+)/public_html.*#\1#p')
SUB=$(printf '%s' "$TARGET" | sed -nE 's#^/home/[^/]+/public_html/?(.*)$#\1#p')
if [ -n "$SUB" ]; then URL="https://${DOMAIN}/${SUB}/"; else URL="https://${DOMAIN}/"; fi

echo
echo "✓ deployed"
printf '  %s → ' "$URL"
# write to a local temp file rather than /dev/null: curl on Windows chokes on
# large responses written to the null device (error 23), and mktemp hands back a
# unix-style path that Windows curl cannot resolve
TMP=".deploy-check.tmp"
curl -sS -L -o "$TMP" -w 'HTTP %{http_code}  %{size_download} bytes\n' "$URL" \
  || echo "(deployed, but could not reach it from here)"
rm -f "$TMP"
