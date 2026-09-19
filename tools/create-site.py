#!/usr/bin/env python3
"""
Create a CyberPanel website from the command line.

Why this exists: the CyberPanel CLI (`cyberpanel createWebsite ...`) is broken on
this server — `listWebsitesPretty` returns `0` and `listUsers` returns an empty
array even though 10 sites exist. Rather than trust a tool that lies, this calls
the exact same internal function the web UI and the REST API call
(`WebsiteManager.submitWebsiteCreation`), from CyberPanel's own Python
environment, with the DB already configured.

Run it ON THE SERVER as root:

    scp tools/create-site.py hetu:/tmp/
    ssh hetu '/usr/local/CyberCP/bin/python /tmp/create-site.py aihammer.trilumi.xyz'

It is idempotent: if the domain already exists in CyberPanel it exits without
touching anything.

Prerequisites (in order — this script does NOT do them for you):
  1. DNS A record must already exist and resolve to this server, otherwise the
     Let's Encrypt step will fail.
  2. The `package` and `websiteOwner` you pass must already exist in CyberPanel.

What it does: creates the Linux-side layout, the LiteSpeed vhost, the CyberPanel
DB record, and issues a Let's Encrypt certificate (the internal path forces
ssl=1, so SSL happens as part of creation).
"""
import os
import sys

sys.path.insert(0, "/usr/local/CyberCP")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CyberCP.settings")

import django  # noqa: E402

django.setup()

from loginSystem.models import Administrator          # noqa: E402
from websiteFunctions.models import Websites          # noqa: E402
from websiteFunctions.website import WebsiteManager   # noqa: E402


def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else "aihammer.trilumi.xyz"
    email = sys.argv[2] if len(sys.argv) > 2 else "admin@trilumi.xyz"
    owner = sys.argv[3] if len(sys.argv) > 3 else "admin"
    package = sys.argv[4] if len(sys.argv) > 4 else "Default"
    php = sys.argv[5] if len(sys.argv) > 5 else "PHP 8.1"

    if Websites.objects.filter(domain=domain).exists():
        print(f"SKIP: {domain} already exists in CyberPanel — nothing changed")
        return 0

    try:
        admin = Administrator.objects.get(userName=owner)
    except Administrator.DoesNotExist:
        print(f"ERROR: no CyberPanel user named {owner!r}")
        return 1

    print(f"domain : {domain}")
    print(f"owner  : {admin.userName} (pk={admin.pk})")
    print(f"package: {package}")
    print(f"php    : {php}")
    print()

    data = {
        "domainName":    domain,
        "adminEmail":    email,
        "ownerEmail":    email,
        "websiteOwner":  owner,
        "ownerPassword": "unused-owner-already-exists",
        "package":       package,
        "packageName":   package,
        "phpSelection":  php,
        "websitesLimit": 1,
        "acl":           "user",
        # forced to 1 by the internal path, so SSL is issued during creation
        "ssl":           1,
        "dkimCheck":     1,
        "openBasedir":   1,
        "mailDomain":    0,
        "apacheBackend": 0,
        "HA":            0,
    }

    resp = WebsiteManager().submitWebsiteCreation(admin.pk, data)
    body = resp.content.decode("utf-8", "replace") if hasattr(resp, "content") else str(resp)

    print("--- response ---")
    print(body[:1200])
    print()

    if Websites.objects.filter(domain=domain).exists():
        print(f"OK: {domain} is now registered")
        print(f"    document root: /home/{domain}/public_html")
        return 0

    print("WARNING: not registered afterwards — check the response above")
    return 1


if __name__ == "__main__":
    sys.exit(main())
