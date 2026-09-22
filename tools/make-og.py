#!/usr/bin/env python3
"""Generate og.png, the 1200x630 social card for halsteadsystems.com.

Run from the repo root:  python3 tools/make-og.py
Writes og.png in the repo root.

The card is set in the page's heading font so the two match. Geist ships as a
variable font, so the weights come from named instances on the wght axis.
"""

import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = "#12161C"
INK = "#ECEEF0"
AMBER = "#E3A93E"
MUTED = "#8A929D"

MARGIN = 88

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/geist/Geist%5Bwght%5D.ttf"
FONT_FALLBACK = "/System/Library/Fonts/Supplemental/Arial.ttf"

CACHE = os.path.join(os.path.dirname(__file__), ".fonts")

WORDMARK = "Halstead Systems"
HEADLINE = "Cut waste from your AWS bill without disrupting production."
KICKER = "Free 20 minute AWS cost review"

HEADLINE_MAX = 72
HEADLINE_MIN = 46
HEADLINE_LINES = 2


def font_path():
    """Prefer the live page's heading font; fall back to its CSS fallback."""
    os.makedirs(CACHE, exist_ok=True)
    local = os.path.join(CACHE, "Geist[wght].ttf")
    if not os.path.exists(local):
        try:
            urllib.request.urlretrieve(FONT_URL, local)
        except Exception as exc:
            print("Geist fetch failed (%s), using Arial" % exc)
            return FONT_FALLBACK
    return local


def load(path, size, weight):
    """Load one instance of the variable font at a named weight."""
    font = ImageFont.truetype(path, size)
    try:
        font.set_variation_by_name(weight)
    except Exception:
        pass  # static fallback has no axes
    return font


def wrap(draw, text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_headline(draw, path, max_width):
    """Largest size that still sets the headline in HEADLINE_LINES lines.

    Geist SemiBold is much wider than the serif this card used to use, so the
    size cannot be hard coded without the headline overflowing.
    """
    for size in range(HEADLINE_MAX, HEADLINE_MIN - 1, -2):
        font = load(path, size, "SemiBold")
        lines = wrap(draw, HEADLINE, font, max_width)
        if len(lines) <= HEADLINE_LINES:
            return font, lines
    font = load(path, HEADLINE_MIN, "SemiBold")
    return font, wrap(draw, HEADLINE, font, max_width)


def main():
    path = font_path()
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    max_width = W - (MARGIN * 2)
    wordmark_font = load(path, 34, "SemiBold")
    kicker_font = load(path, 23, "Regular")
    headline_font, lines = fit_headline(draw, path, max_width)

    # Wordmark, top left.
    draw.text((MARGIN, MARGIN - 6), WORDMARK, font=wordmark_font, fill=INK)

    # Thin amber rule under the wordmark, the only ornament on the card.
    rule_y = MARGIN + 50
    draw.rectangle([MARGIN, rule_y, MARGIN + 104, rule_y + 3], fill=AMBER)

    # Headline, set to fill the lower two thirds.
    leading = round(headline_font.size * 1.2)
    block_h = leading * len(lines)
    y = H - MARGIN - 52 - block_h
    for line in lines:
        draw.text((MARGIN, y), line, font=headline_font, fill=INK)
        y += leading

    # Kicker, bottom left.
    draw.text((MARGIN, H - MARGIN - 18), KICKER, font=kicker_font, fill=MUTED)

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "og.png")
    img.save(out, "PNG", optimize=True)
    print("wrote %s %s  headline %dpx in %d lines" % (out, img.size, headline_font.size, len(lines)))


if __name__ == "__main__":
    main()
