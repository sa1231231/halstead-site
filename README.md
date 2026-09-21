# halstead-site

Landing page for halsteadsystems.com. Static HTML, no build step.

## Deploy

Vercel: import this repo, framework preset "Other", no build command, output directory `.` (root).
Changes go straight to `main`; there are no pull requests on this repo.

## Edit

Everything lives in `index.html`. Colors and fonts are CSS variables at the top of the `<style>` block.

The optional headshot goes at `images/sam.jpg`, square. If it is absent the element removes itself
and the layout closes up.

## Preview

```sh
python3 -m http.server 8787 --bind 127.0.0.1
```

Then open http://127.0.0.1:8787/index.html

## Social card

```sh
python3 tools/make-og.py
```

Regenerates `og.png` (1200x630). Rerun it when the wordmark, headline, or heading font changes.

See `CLAUDE.md` for the content and copy rules the page has to hold to.
