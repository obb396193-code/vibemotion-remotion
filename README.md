# vibemotion-remotion

A **growing library of Remotion video recipes**, packaged as a Claude skill — the sibling of **[vibemotion-hyperframes](https://github.com/obb396193-code/vibemotion-hyperframes)** (pure-code motion-graphics via HyperFrames). Reach for this one when a video is **material-heavy** (lots of local images / footage), needs **OCR-positioned highlights / annotations**, or wants **batch / parametrized** output.

> This is an **agent skill**: the entry point is [`SKILL.md`](SKILL.md). This README is the human-facing overview.

## What it's for
Mainly to **reproduce + grow a menu of Remotion videos** you can pick from. The first validated recipe is `article-highlight` (below); each new validated type lands in `examples/` as a runnable template, so the menu gets richer over time.

## Recipe menu (pick one — or ask for a new one)
| Recipe | What | Status |
|---|---|---|
| **article-highlight** | image/screenshot + **OCR-located highlights** + blur-in + subtle zoom & 3D rotate | ✅ validated |
| footage / screen-rec packaging | real footage base + titles / captions / transitions / grade on top | ⏳ candidate (`<OffthreadVideo>`) |
| data-driven | animated charts / counters / leaderboards (Zod-fed data) | ⏳ candidate |
| batch / parametrized | one template × N datasets → dozens of clips | ⏳ candidate (`--props`) |
| photo Ken Burns | slow pan/zoom over a photo set + transitions | ⏳ candidate |
| caption burn-in | burn SRT / word-by-word captions into a video | ⏳ candidate (`@remotion/captions`) |

## The first recipe — article-highlight
White FHD bg, article centered → blur-in over 1s → subtle 5s zoom + ~15°/axis 3D rotation → **rough.js highlighter marks behind the text** (multiply blend) on phrases located by **Tesseract OCR**, swept in left→right. Source: [`examples/article-highlight/`](examples/article-highlight).

Swap in your own image: drop it in `public/`, run `scripts/ocr-to-highlights.py <img> "phrase 1" "phrase 2"`, re-render — the composition reads `highlights.json`, so the code stays untouched.

## Scripts
- `scripts/ocr-to-highlights.py` — Tesseract OCR → `highlights.json` (phrase boxes in image px).
- `scripts/render.sh` — render with a **clean `chrome-headless-shell`**, dodging the two classic Remotion render failures (slow auto-download / uncontrollable system Chrome).

## Install
```bash
git clone https://github.com/obb396193-code/vibemotion-remotion.git ~/.claude/skills/vibemotion-remotion
```

## Requirements
- Node + **Remotion** — free for individuals & teams up to 3; companies need a license ([remotion.dev/license](https://remotion.dev/license)).
- `tesseract` CLI (`brew install tesseract`).
- a clean `chrome-headless-shell` for rendering (playwright's cache works; `render.sh` finds it).

## License & attribution
Original code/docs: **MIT** ([`LICENSE`](LICENSE)). Remotion, roughjs, Tesseract keep their own licenses — see [`NOTICE.md`](NOTICE.md).
