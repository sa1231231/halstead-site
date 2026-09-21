# CLAUDE.md

Landing page for Halstead Systems (halsteadsystems.com). Static HTML, no build step,
deployed on Vercel from `main`.

## Workflow

Changes go straight to `main`. Do not open pull requests.

Trying alternate fonts or layouts is the one exception: put each on its own branch so
Vercel builds a preview for it, compare, then merge the winner into `main` directly and
delete the rest. The heading font was settled this way and those branches are gone.

## What the page is for

One job: get a qualified visitor to book the 20-minute AWS cost review at
https://cal.com/sam-e/aws-cost-review

The buyer is a CTO, VP of Engineering, or technical founder at a SaaS or software company
spending $10,000+/month on AWS with nobody owning cloud cost full time. They are skeptical,
technical, and allergic to marketing language. Specificity and restraint earn the click.

## Content rules

These are hard constraints. Check them before every push.

- No email address or phone number anywhere on the page. The cal.com link is the only contact path.
- Every number on the page has to be true and traceable to an actual engagement. Figures from
  the work are welcome and specific is better than vague, but nothing illustrative, rounded for
  effect, or invented to fill a slot.
- The hero's right panel is proof, not a sample. It leads with the $68K/month figure and the
  30% share it represents on one engagement, then lists what was actually done. Keep it tied to
  work that happened; it is the first thing a skeptical visitor reads.
- No specific federal agency or employer names. "Federal" stays generic.
- No savings guarantee. The only guarantee is the delivery one in the How it works callout.
- The client quotes in the "Who does the work" band come from automation and software projects
  outside AWS, and the page says so directly. Do not drop that framing: unexplained quotes from
  unrelated businesses read as padding to the buyer this page is written for.

## Copy style

- No em dashes.
- No "not X but Y" or "rather than" contrast constructions.
- Never the word "real".
- Sentence case for headings and buttons.
- No arrows on buttons.

Run the checks:

```sh
grep -nE 'mailto:|tel:|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' index.html   # expect none
grep -n '—\|–' index.html                                                           # expect none
grep -niE '\breal\b|rather than|\bnot [a-z]+,? but\b' index.html                    # expect none
grep -oE '\$[0-9][0-9,.]*[KkMm]?(/month)?' index.html | sort -u                     # every figure traceable to real work
```

## Page order

Hero, who it's for, where the money goes, how it works, what's included, questions, who does the
work, closing call to action. Sections alternate base and raised backgrounds strictly, so
inserting or moving one means re-checking the whole run of `band--raised`.

Qualification sits high on purpose: a visitor who is not a fit should find that out before
reading the offer. The person and the client quotes sit last, immediately before the closing
call to action, so the page asks for the booking right after the reason to trust him.

## Design constraints

- Dark palette with amber accent. Both are CSS variables at the top of the `<style>` block.
- The page uses one family, Geist, for both headings and body. `--serif` and `--sans` hold
  the same stack; the names are historical, from when headings were set in a serif. Heading
  weight and tracking are `--h-weight` / `--h-track` / `--h1-track`, so a font change is a
  change to those variables and the Google Fonts link, nothing else.
- `og.png` is set in the heading font, so a font change means regenerating it. See below.
- Body copy 18px, line length under 70 characters.
- Sections alternate between `--bg` and `--raised` via `.band` / `.band--raised`.
- Buttons: 6px radius, solid amber primary, outlined secondary in the header.
- One page-load fade on the hero only. Nothing else animates on its own.
  `prefers-reduced-motion: reduce` disables all animation and transition.
- The headshot at `/images/sam.jpg` is optional. Its `onerror` handler adds `is-photoless` to
  `.about` and then removes the image. Both halves matter: without the class the text drops into
  the 176px photo column and sets as a narrow ribbon down the left.
- Must hold up at 375px wide. The waste grid, the hero proof panel, and the proof figures are
  the three things that break first.
- The headline figure in the hero is a hero number and the bar under it is a meter, which is the
  right form for one ratio against a whole. Do not turn it into a chart: a two-slice pie or a
  one-bar bar chart says less and takes more room. The meter fill is amber on a dim step of the
  same amber, so it reads as one scale.

## Local preview

Chrome's headless mode clamps its window to a 500px minimum, so a `--window-size=375` screenshot
is a crop of a 500px layout, not a 375px one. To test mobile for true, load the page in an iframe
that is 375px wide and measure inside it.

```sh
python3 -m http.server 8787 --bind 127.0.0.1    # then open http://127.0.0.1:8787/index.html
```

## Social card

`og.png` is generated, not hand-made. Regenerate it with:

```sh
python3 tools/make-og.py
```

It downloads Geist into `tools/.fonts/` (gitignored) and writes a 1200x630 `og.png` at the
repo root. Rerun it whenever the wordmark, headline, or heading font changes.

Geist is a variable font, so the script pulls its SemiBold instance off the `wght` axis to
match the page. The headline size is not hard coded: the script steps down from 72px until
the line breaks into two, because a weight or wording change moves that threshold.
