#!/usr/bin/env python3
"""Render a markdown file to a self-contained HTML page, for publishing as an Artifact.

Math is converted to MathML by pandoc, which Chrome renders natively -- no JavaScript, no
CDN, and so nothing for the Artifact CSP to block. This is why the published page needs
neither a MathJax browser plugin nor an inlined KaTeX bundle, and why it renders the same
for anyone you share the link with.

Glyph quality comes from Latin Modern Math (the Computer Modern face of a LaTeX document),
subsetted and embedded as a WOFF2 data URI. Embedding is the load-bearing part: the page
renders in the READER's browser, so a font that is merely installed on this machine does
nothing. If the font or fontTools is unavailable the page still works, falling back to
whatever math font the reader happens to have -- which on many machines has no OpenType
MATH table, so stretchy delimiters stop stretching.

Usage:  render_md.py <input.md> <output.html> [--title TITLE] [--no-math-font]
"""

import base64
import io
import re
import subprocess
import sys
import time
from pathlib import Path

TEMPLATE = Path(__file__).with_name('template.html')

# texlive ships this; it is the only font on a normal box with a real MATH table.
MATHFONT = Path('/usr/share/texmf/fonts/opentype/public/lm-math/latinmodern-math.otf')

# Codepoints kept in the subset beyond those the document actually uses. Without this the
# subset tracks one document exactly, and a doc that later grows a \lfloor renders tofu.
# The insurance costs ~60 KB. Note pandoc emits \| as U+2225 (not U+2016), which is why
# the 0x2200-0x22ff range matters more than it looks.
PAD_RANGES = [(0x20, 0x7f), (0x391, 0x3d7), (0x2190, 0x21ff), (0x2200, 0x22ff),
              (0x2308, 0x230c), (0x27e6, 0x27f0), (0x2980, 0x2999)]
PAD_SINGLES = [0x2016, 0x2044, 0x221a, 0x2211, 0x220f, 0x2113]


def math_font_css(html):
    """Returns a <style> block embedding a Latin Modern Math subset covering the math in
    'html', or '' if the font or fontTools is unavailable (a cosmetic loss, not a broken
    page)."""

    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        return ''
    if not MATHFONT.exists():
        return ''

    used = set()
    for block in re.findall(r'<math\b.*?</math>', html, re.S):
        for text in re.findall(r'>([^<>]+)<', block):
            used.update(ord(c) for c in text if ord(c) > 32)
    for lo, hi in PAD_RANGES:
        used.update(range(lo, hi))
    used.update(PAD_SINGLES)

    font = TTFont(MATHFONT)
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = '*'      # keep MATH; dropping it loses stretchy delimiters
    opts.glyph_names = False
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=used)
    sub.subset(font)

    buf = io.BytesIO()
    font.flavor = 'woff2'
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')

    return ('\n<style>\n'
            '@font-face { font-family: "LM Math"; font-display: swap;\n'
            f'  src: url(data:font/woff2;base64,{b64}) format("woff2"); }}\n'
            'math { font-family: "LM Math", "Latin Modern Math", math; }\n'
            '</style>\n')


def render(src, dst, title=None, embed_font=True):
    src, dst = Path(src), Path(dst)
    title = title or src.stem.replace('_', ' ')
    stamp = (f"{src.name} -- rendered {time.strftime('%Y-%m-%d %H:%M')} -- "
             "regenerate with the ch-artifact skill; the markdown file is the source of truth")

    html = subprocess.run(
        ['pandoc',
         '--from=markdown+tex_math_dollars+pipe_tables+backtick_code_blocks',
         '--to=html5',
         '--mathml',                  # native MathML, not a JS typesetter
         '--standalone',
         f'--template={TEMPLATE}',
         '--toc', '--toc-depth=2',
         '--metadata', f'title={title}',
         '--metadata', f'stamp={stamp}',
         str(src)],
        check=True, capture_output=True, text=True).stdout

    # Pandoc emits bare <table>; wrap each so wide tables scroll inside their own
    # container and the page body never scrolls sideways.
    html = re.sub(r'<table\b', '<div class="tablewrap"><table', html)
    html = html.replace('</table>', '</table></div>')

    if embed_font:
        css = math_font_css(html)
        if css:
            # The font block MUST land after </title>. It is ~100 KB of base64, and the
            # Artifact publisher only scans the first 8 KB of the file for a <title> --
            # prepending it silently costs the page its name.
            i = html.find('</title>')
            i = (i + len('</title>')) if (i >= 0) else 0
            html = html[:i] + css + html[i:]

    dst.write_text(html)
    return html


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('input', help='markdown file to render')
    p.add_argument('output', help='HTML file to write')
    p.add_argument('--title', default=None,
                   help='artifact title (default: the input filename stem)')
    p.add_argument('--no-math-font', action='store_true',
                   help='skip the embedded math font (leaves math to the reader system font)')
    a = p.parse_args()

    out = render(a.input, a.output, title=a.title, embed_font=not a.no_math_font)
    print(f"wrote {a.output}: {len(out):,} bytes, {out.count('<math')} math elements, "
          f"{out.count('<table')} tables, "
          f"font {'embedded' if '@font-face' in out else 'MISSING (reader system font)'}")
