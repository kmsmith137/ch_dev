---
name: ch-artifact
description: Publish a file as a claude.ai artifact and put the link in the chat, so it can be read in a browser (typically a phone). Markdown is rendered to HTML with native MathML and an embedded math font, so equations render without a browser plugin. Use when asked to publish, share, or "let me see" a plan, note, or doc.
argument-hint: [file to publish, e.g. "plans/foo.md" or "the plan you just created"]
---

Publish a file as an artifact and give me the link. I am usually reading on a phone, so
the reply should be short and the link easy to tap.

## What to publish

    $ARGUMENTS

Resolve that to exactly one file:

- **A path** (`plans/foo.md`, `foo.md`, `notes/bar.md`) -- use it. If it is a bare
  filename, search for it; `plans/` is the usual home, but do not assume.
- **A reference to our conversation** ("the plan you just created", "that doc", "it") --
  resolve it from context. Say which file you picked in your reply, so I can correct you.
- **Empty, or ambiguous with more than one plausible match** -- ask, and list the
  candidates. Do not guess: publishing the wrong file wastes a round trip, and from a
  phone that is expensive.

Before rendering, check the file exists and is non-empty. If I named something that is
not there, say so rather than publishing a stale copy of something else.

## Rendering

For **markdown**, run the bundled renderer:

    python3 .claude/skills/ch-artifact/render_md.py <input.md> <output.html> --title "<Title>"

Write the HTML to a scratch path, not into the repo. The renderer needs `pandoc`; if it
is missing, say so and stop -- do not fall back to publishing the raw `.md`, because
claude.ai's markdown renderer does not typeset math and the equations will come out as
raw LaTeX.

For **HTML**, publish the file as-is.

For **anything else** (`.py`, `.tex`, `.yml`, ...), do not invent a rendering. Say what
the file is and ask whether I want it fenced inside a markdown page, or just sent with
SendUserFile.

### Choosing the title

The title names the artifact in the browser tab and in my artifact gallery, so it has to
be recognizable among many. Use a short noun phrase specific to the subject -- "Brute-force
variance map", not "Plan" and not "Implementation plan for the brute-force variance map
(CPU and GPU)". Derive it from the document's H1 rather than the filename when they
differ. Keep it stable across republishes of the same document.

## Publishing

**Check for an existing artifact first.** I will re-run this on the same document as it
changes, and each publish of a new file path mints a new URL -- so without this I end up
with five links to the same plan and no idea which is current.

    Artifact({action: "list"})

If a row matches the document (same or near-same title), pass its URL:

    Artifact({file_path: "...", url: "<that url>", favicon: "...", description: "..."})

Otherwise publish fresh. Within one conversation, republishing the *same file path*
keeps the URL automatically, so the list check matters most when resuming later.

Pick a favicon that suits the subject, and **keep it identical when updating** -- I find
the tab by its icon, so a changed emoji reads as a different page. Only change it if the
document's subject genuinely changed.

Give `description` a one-sentence summary; it becomes the gallery card's subtitle and is
how I tell two similar plans apart.

## Replying

Lead with the link on its own line, then at most a few lines:

- which file was published (so I can catch a wrong guess),
- whether it replaced an existing artifact or is new,
- anything genuinely worth knowing -- the doc is stale relative to something, the math
  did not render, the file was much bigger than expected.

Do not narrate the pipeline, list the validation you ran, or explain MathML. If
everything worked, the link and one line is the whole reply.

## Notes on the rendering, for when something looks wrong

- Math is **MathML**, rendered natively by the browser. No JavaScript, no CDN, nothing
  for the artifact CSP to block, and no dependence on a MathJax browser extension.
- The math font is Latin Modern Math (Computer Modern), subsetted and embedded as a
  data URI. Embedding is load-bearing: the page renders in *my* browser, so a font that
  is merely installed on the server does nothing. If it goes missing the page still
  works, but stretchy delimiters stop stretching -- big parentheses and norm bars come
  out at base size around tall expressions.
- The font block is inserted *after* `</title>` on purpose. It is ~100 KB of base64 and
  the publisher only scans the first 8 KB for a title, so prepending it silently costs
  the page its name.
- Prose is capped at a readable measure while tables and code blocks break out into the
  full window width, so widening the window retires their scrollbars.
- The page has a contents rail, and light and dark are both designed. Do not add
  external resources; a strict CSP blocks them and the page will look broken.

If you change `template.html`, re-check three things before publishing: no
`<!doctype>`/`<html>`/`<head>`/`<body>` tags of its own (the publisher supplies them), no
`src=`/`href=` to an external host, and `<title>` inside the first 8 KB.
