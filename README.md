# What is super — local build

Local sync of the Claude Design project **“Like-for-like page design”**
(`03aa55d0-58f8-4f72-a7f9-33cfb2a08cf4`).

## Run it

```bash
python3 serve.py          # http://localhost:8000
```

The index links the three pages:

| Page | Notes |
| --- | --- |
| `What is super - Responsive.dc.html` | Entry point. Picks mobile/desktop at a `mobileBreakpoint` of 1280px. |
| `What is super.dc.html` | Desktop layout. |
| `What is super - Mobile.dc.html` | Mobile layout, 390px preview. |

Opening the `.dc.html` files directly with `file://` will **not** work — the
runtime uses `fetch` to resolve `<dc-import>` components, which needs an HTTP
origin. Use the server.

## Why there is a server

`support.js` is the Deck Components runtime. It expects `window.React` and
`window.ReactDOM` to already exist — in the design app the host injects them.
The synced `.dc.html` files don't reference React at all.

Rather than editing the synced files (which would make them diverge from the
project and complicate pushing changes back), `serve.py` injects the vendored
UMD builds from `vendor/` into `<head>` on the way out. The files on disk stay
byte-identical to what's in the project.

Babel is *not* needed: the runtime only loads it for `<x-import>` of external
JSX modules, and these pages use only `<dc-import>`.

## Assets over the DesignSync cap

Four assets exceed the **256 KiB cap** on the DesignSync `get_file` API — it
truncates mid-stream with no range/offset parameter, so they can't be pulled
through that path at all. All four are now the real files, supplied directly
by the user (from the project's `uploads/`, which mirror these under
different names) rather than fetched through DesignSync:

| Asset | Size | Source |
| --- | --- | --- |
| `assets/quiz-photo.png` | 358,381 B | `uploads/photo-blob-container.png` |
| `assets/icon-working.svg` | 321,091 B | `uploads/Group 80095.svg` |
| `assets/icon-in-retirement.svg` | 436,281 B | `uploads/Group 80089.svg` |
| `assets/lost-super-photo.png` | 515,903 B | `uploads/image 8.png` |

Nothing in `assets/` is a placeholder anymore. Along the way, before the real
files arrived, `.dcsync/placeholders.py` generated dashed-outline/flat-fill
stand-ins for all four, and the two icons briefly used a recolor of
`icon-transition.svg` instead. Both scripts are kept only as a reference for
the technique — neither is needed to build the site now.

`assets/icon-transition.svg` came through DesignSync intact at 256,182 bytes —
just under the cap — the only one of the four that didn't need a manual drop-in.

## Layout

```
What is super*.dc.html    3 synced pages
support.js                Deck Components runtime (generated, don't edit)
assets/                   render-critical assets referenced by the pages
vendor/                   React 18.3.1 + ReactDOM UMD builds
serve.py                  dev server, injects React
.dcsync/                  sync tooling (harvest/extract/placeholder scripts)
```

`.dcsync/harvest.py` and `.dcsync/extract.py` pull file contents out of
DesignSync tool results and write them to disk, so large/binary assets don't
have to be retyped by hand.

## Not synced

The project also holds `uploads/` (26 files) and `shots/` (2) — pasted design
references and screenshots, not referenced by any of the three pages. They were
left alone; several are likely over the same 256 KiB cap.
