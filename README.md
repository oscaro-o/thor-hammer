# Everyone Got Thor's Hammer

A short narrative game about what is still worth paying for once execution becomes free.

**English · 简体中文 · 繁體中文** — switchable in-game, no reload, progress preserved.

---

## What it is

One morning, every person on earth wakes up holding Thor's hammer. A week's work finishes
before lunch. A year of practice takes a minute. Nothing you can make is scarce any more.

You play a carver with twenty years in his hands, across six chapters, making six decisions
that decide what he ends up selling — his hours, or his judgement.

It is a game about AI, told without ever saying the word until the last screen.

## The design idea

Five meters. Four of them move when you choose.

The fifth one doesn't. It is labelled **"market price of *can you make it?*"** and it falls
from 100 to 3 over the six chapters no matter what you do. That is the whole lesson in one
bar: your effort is racing a line you cannot move.

At the end you get a rank — **The Eye / The Editor / The Craftsman / The Piece Worker** —
plus a recap of the six lessons your own choices produced, and a share card you can
download as a PNG.

## Running it

Single file, zero dependencies, no build step. Open `index.html`. That's it.

```bash
open index.html            # macOS
start index.html           # Windows
```

It works offline. There is no analytics, no tracking, no external request of any kind.

## Live

| Where | URL |
|---|---|
| GitHub repo | https://github.com/oscaro-o/thor-hammer |
| GitHub Pages (permanent backup) | https://oscaro-o.github.io/thor-hammer/ |
| VPS (Trilumi server) | https://hetu.trilumi.xyz/hammer/ |

Both serve the same file. The Pages copy survives any server work; the VPS copy
is the one to move to a proper subdomain later.

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire game. This is the deployable artifact. |
| `og.png` | 1200×630 social preview image. |
| `og.html` | Browser tool that regenerates `og.png`. |
| `tools/make-og.py` | Terminal version of the same thing (needs Pillow). |
| `deploy.sh` | One-command deploy to the VPS. |
| `.github/workflows/deploy.yml` | Auto-deploy on push to `main`. |

## Deploying

### Option A — from your machine

```bash
./deploy.sh                      # deploys to /home/hetu.trilumi.xyz/public_html/hammer
./deploy.sh /some/other/path     # or override it
```

It tars the site over SSH and unpacks it on the server, then fixes ownership and
prints the HTTP status of the live URL. Requires the `hetu` host alias in
`~/.ssh/config` and `~/.ssh/hetu_deploy`.

### Option B — automatically on every push

Add these four repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | Value |
|---|---|
| `SSH_HOST` | `212.85.27.147` |
| `SSH_USER` | `root` |
| `SSH_PRIVATE_KEY` | contents of `~/.ssh/hetu_deploy` (the **private** key) |
| `DEPLOY_PATH` | `/home/hetu.trilumi.xyz/public_html/hammer` |

Then every push to `main` deploys. You can also trigger it by hand from the Actions
tab. The workflow fails loudly with a list of missing secrets if any are unset, so
it can never half-deploy.

> The private key goes into GitHub Secrets, which are encrypted and never printed to
> workflow logs — but they *are* readable by anyone with admin rights on the repo.
> If you'd rather not, use Option A and delete the workflow file.

## Moving it to a proper domain

`hetu.trilumi.xyz/hammer/` is a sandbox path, chosen because it touches nothing
that already exists. When you want a real home:

1. CyberPanel → **Websites → Create Website**, domain e.g. `hammer.trilumi.xyz`
2. Point the DNS A record at `212.85.27.147`
3. CyberPanel → **SSL → Issue SSL**
4. `./deploy.sh /home/hammer.trilumi.xyz/public_html`
5. Update the `og:image` / `twitter:image` meta tags in `index.html` to the new
   absolute URL, and the `DEPLOY_PATH` secret if you use Option B.

## A note on the metaphor

Thor's hammer comes from **Norse mythology, which is public domain** — unlike a certain
wuxia sword, which is not. The artwork here is abstract geometry; there is no depiction of
the character, and no Marvel design language. If you ever want one more degree of distance,
rename it to the mythological name *Mjolnir* — at the cost of some recognition.

## License

© 2026. All rights reserved.
