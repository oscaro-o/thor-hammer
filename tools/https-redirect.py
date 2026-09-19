#!/usr/bin/env python3
"""
Force HTTPS for a CyberPanel site on OpenLiteSpeed.

IMPORTANT: this server runs **OpenLiteSpeed**, not LiteSpeed Enterprise.
`.htaccess` is an Enterprise-only feature — OpenLiteSpeed silently ignores it
(the vhost says `autoLoadHtaccess 1`, but that flag does nothing in OLS).
That is why the redirect has to go into the vhost config itself.

Run it ON THE SERVER as root:

    ssh hetu '/usr/local/CyberCP/bin/python /tmp/https-redirect.py aihammer.trilumi.xyz'

It is idempotent and takes a timestamped backup of the vhost config first.
Restart OpenLiteSpeed afterwards:

    systemctl restart lshttpd

CAVEAT: CyberPanel regenerates the vhost config when you change site settings
(PHP version, SSL, rewrite rules in the UI). If that happens, the rule is lost —
re-run this script, or paste the same rules into
CyberPanel → Websites → <domain> → Rewrite Rules.
"""
import os
import shutil
import sys
import time

CONF_TMPL = "/usr/local/lsws/conf/vhosts/{domain}/vhost.conf"

OLD = """rewrite  {
 enable                  1
  autoLoadHtaccess        1
}"""

NEW = """rewrite  {
 enable                  1
  autoLoadHtaccess        1
  rules                   <<<END_rules
RewriteCond %{HTTPS} !=on
RewriteCond %{REQUEST_URI} !^/\\.well-known/
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]
  END_rules
}"""


def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else "aihammer.trilumi.xyz"
    conf = CONF_TMPL.format(domain=domain)

    if not os.path.exists(conf):
        print(f"ERROR: no vhost config at {conf}")
        return 1

    src = open(conf).read()

    if "RewriteCond %{HTTPS}" in src:
        print("already has an HTTPS redirect — nothing to do")
        return 0

    backup = conf + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(conf, backup)
    print("backup:", backup)

    if OLD not in src:
        print("ERROR: could not find the expected vhost-level rewrite block.")
        print("       Open the file and add the rules by hand:")
        print(NEW)
        return 1

    open(conf, "w").write(src.replace(OLD, NEW, 1))
    print("redirect rule inserted into", conf)
    print()
    print("now restart:  systemctl restart lshttpd")
    return 0


if __name__ == "__main__":
    sys.exit(main())
