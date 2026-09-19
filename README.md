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

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire game. This is the deployable artifact. |
| `og.html` | Tool page — renders and downloads `og.png` (the 1200×630 social preview image). |
| `deploy.sh` | One-command deploy to the VPS. |
| `.github/workflows/deploy.yml` | Auto-deploy on push to `main`. |

## Deploying

### Option A — from your machine

```bash
./deploy.sh                      # uses the default target below
./deploy.sh /some/other/path     # or override it
```

It tars the site over SSH and unpacks it on the server. Requires the `hetu` host alias in
`~/.ssh/config` and `~/.ssh/hetu_deploy`.

### Option B — automatically on every push

Add these four repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | Value |
|---|---|
| `SSH_HOST` | `212.85.27.147` |
| `SSH_USER` | `root` |
| `SSH_PRIVATE_KEY` | contents of `~/.ssh/hetu_deploy` (the **private** key) |
| `DEPLOY_PATH` | absolute path to the web root on the server |

Then every push to `main` deploys. You can also trigger it by hand from the Actions tab.

> The private key goes into GitHub Secrets, which are encrypted and never exposed to
> workflow logs — but they *are* readable by anyone with admin rights on the repo.
> If you'd rather not, use Option A and skip the workflow.

## One thing left to do

`og:image` and `twitter:image` in `index.html` currently point at a **relative** `og.png`.
Most social platforms require an **absolute** URL. Once the domain is settled:

1. Open `og.html`, click the button, save the file as `og.png` in this folder
2. Commit it
3. Change both meta tags to `https://<your-domain>/og.png`

Until then, shared links will show a plain text card instead of an image.

## A note on the metaphor

Thor's hammer comes from **Norse mythology, which is public domain** — unlike a certain
wuxia sword, which is not. The artwork here is abstract geometry; there is no depiction of
the character, and no Marvel design language. If you ever want one more degree of distance,
rename it to the mythological name *Mjolnir* — at the cost of some recognition.

## License

© 2026. All rights reserved.
