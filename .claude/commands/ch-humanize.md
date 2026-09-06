---
description: Re-explain or revise text (in chat or a markdown file) to make it human-readable: self-contained, concise, and free of agent-oriented shorthand
---

Agents often write text that is difficult for humans to understand. This
command asks you to re-explain or revise something so that a HUMAN can follow
it. Here are some guidelines.

It is critical for human-friendly text to be SELF-CONTAINED. Humans are deep
thinkers but slow readers, and -- unlike you -- they do not have the details of
the source files in their context. This creates friction between humans and
agents. For example, an agent might write a paragraph containing identifiers
(function names, variable names, etc.) from different, scattered parts of the
code, without saying where those identifiers can be found. That is good style
if the audience is another agent: it is precise and unambiguous. For a human it
is cryptic and disorienting.

Here is another way of phrasing it. Agents tend to write as though the audience
already has all the background material in context, so the text's job is to
convey additional, detailed information. Humans usually want the reverse: the
text's job is to let the reader AVOID rereading the background material (which
is time-consuming for a human), by summarizing the key information and
stripping away irrelevant details.

At the same time, humans prefer concise explanations. This is what makes the
task hard -- self-contained, fully informative, and concise all pull against
each other. The resolution is usually to STRIP AWAY IRRELEVANT DETAILS while
CLEARLY EXPLAINING THE CORE, CONCEPTUAL ISSUE. Do not buy concision by becoming
cryptic, by making the text denser, or by reaching for pedagogical
anti-patterns such as undefined jargon. Equally, do not buy it by sweeping
important issues under the rug.

One thing this command does NOT license: a humanize pass rewrites the
EXPLANATION, not the CONCLUSIONS. Don't quietly soften a finding, drop a
caveat, or promote a "probably" to a "definitely" because it reads better. If
revisiting the material convinces you the original was actually WRONG, say so
explicitly instead of silently correcting it.

## Writing tips

A running list, each motivated by a real case where an agent wrote text I found
hard to understand. Expect it to grow.

  - **Qualify the identifiers, and cut the mechanism.** An agent once described
    a race condition at length: what the code did, which fields were touched,
    and exactly what goes wrong when two threads reach them at once. The
    essential content was two sentences:

        SomeClass::some_method() accesses SomeClass::_some_member without
        holding SomeClass::mutex. This creates a race condition with
        SomeClass::another_method().

    Every identifier is qualified, so the reader knows where to look, and the
    mechanism of the race is omitted, because a reader who wants it can now go
    find it. The long version buried both of those under detail.

  - **Block-quote the source when a change is small and local.** Quoting a few
    lines of a file is wasteful if the reader is an agent, which has the file
    in context anyway. For a human it is often the cheapest possible
    explanation, since it saves opening the file and reorienting to it. Prefer
    a short quote over a bare file:line reference whenever the reader's obvious
    next move would be to go and look at exactly those lines.

## Scope and output

What to explain: the argument. It may name a revision target ("rewrite section
3 of the plan"), or simply a topic ("explain the existing Kalman flake, and
some possible courses of action") -- in which case the explanation may be new
text rather than a rewrite. Either way it is judged by the guidelines above.

Invoked with NO argument, this means "re-explain the contents of your last
message in the chat".

If the argument is ambiguous -- which plan, which section, which of two things
we discussed -- ASK me rather than guessing.

Where the result goes: if the text lives in a file, edit that file in place
(note that `plans/*.md` are gitignored -- don't git-add them). If you are
re-explaining something from the chat, just answer in the chat; don't create a
file for it unless I ask.
