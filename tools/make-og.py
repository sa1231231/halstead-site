#!/usr/bin/env python3
"""Generate og.png, the 1200x630 social card for halsteadsystems.com.

Run from the repo root:  python3 tools/make-og.py
Writes og.png in the repo root.
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

SERIF_URL = (
    "https://github.com/google/fonts/raw/main/ofl/instrumentserif/"
    "InstrumentSerif-Regular.ttf"
)
SERIF_FALLBACK = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS_FALLBACK = "/System/Library/Fonts/Supplemental/Arial.ttf"

CACHE = os.path.join(os.path.dirname(__file__), ".fonts")

WORDMARK = "Halstead Systems"
HEADLINE = "Cut waste from your AWS bill without disrupting production."
KICKER = "Fixed-scope AWS cost assessment"


def serif_path():
    """Prefer the live page's heading font; fall back to its CSS fallback."""
    os.makedirs(CACHE, exist_ok=True)
    local = os.path.join(CACHE, "InstrumentSerif-Regular.ttf")
    if not os.path.exists(local):
        try:
            urllib.request.urlretrieve(SERIF_URL, local)
        except Exception as exc:
            print("Instrument Serif fetch failed (%s), using Georgia" % exc)
            return SERIF_FALLBACK
    return local


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


def main():
    serif = serif_path()
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    wordmark_font = ImageFont.truetype(serif, 38)
    headline_font = ImageFont.truetype(serif, 76)
    kicker_font = ImageFont.truetype(SANS_FALLBACK, 24)

    # Wordmark, top left.
    draw.text((MARGIN, MARGIN - 10), WORDMARK, font=wordmark_font, fill=INK)

    # Thin amber rule under the wordmark, the only ornament on the card.
    rule_y = MARGIN + 52
    draw.rectangle([MARGIN, rule_y, MARGIN + 104, rule_y + 3], fill=AMBER)

    # Headline, set to fill the lower two thirds.
    max_width = W - (MARGIN * 2)
    lines = wrap(draw, HEADLINE, headline_font, max_width)
    leading = 94
    block_h = leading * len(lines)
    y = H - MARGIN - 52 - block_h
    for line in lines:
        draw.text((MARGIN, y), line, font=headline_font, fill=INK)
        y += leading

    # Kicker, bottom left.
    draw.text((MARGIN, H - MARGIN - 18), KICKER, font=kicker_font, fill=MUTED)

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "og.png")
    img.save(out, "PNG", optimize=True)
    print("wrote %s %s" % (out, img.size))


if __name__ == "__main__":
    main()
