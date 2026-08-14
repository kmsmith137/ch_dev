# High-level file schema

Template for `research/HIGH_LEVEL.md` (at the worktree root), the human-facing
file of the `/ch-research` workflow (see `SKILL.md`, alongside this file).

There are two files, and the split is by *audience*, not by importance:

- `HIGH_LEVEL.md` (this one) is **for the human**. It answers "where are we?"
  and "what is waiting on me?". It is short, entirely living (every section is
  rewritten in place), and it should be readable on a phone.
- `JOURNAL.md` is **for the toplevel agent**. It is the campaign's memory: the
  full restatement of the question, the research questions, and the append-only
  per-subagent entries.

Rules of thumb for what goes where:

- If only the human can act on it, it belongs here.
- If it is a fact the campaign discovered, it belongs in `JOURNAL.md`.
- Nothing is mirrored between the two files. A suggestion lives here and only
  here; its *status* is tracked here and nowhere else. A journal entry may say
  that a subagent made suggestions, but must not track whether they are done.

## File layout

    # <campaign name>: high level

    **Question**: <one line -- the full restatement lives in JOURNAL.md>
    **Status**: <one short paragraph, dated. See below.>

    ## Questions for the human

    ## Pending suggestions

## Status

One short paragraph, rewritten in place whenever the picture changes
materially (in practice: after any experiment that changes the plan, and
always before you stop). Date it. It should answer, for someone who has read
nothing else:

- what the current best answer to the campaign's question is, in numbers;
- what is being worked on right now;
- what, if anything, is blocked.

Keep it to a few sentences. This is the summary, not the report -- if it is
growing past a paragraph, the detail belongs in `JOURNAL.md`.

**Also record here anything that supersedes a published result**, in one line,
with a pointer to the journal entry whose epilogue has the detail. A subagent
that reads an old `RESULTS.md` will otherwise act on a claim we know to be
wrong.

## Questions for the human

Decisions only the human can make. Numbered so they can be referred to in chat
("go ahead on Q2"), dated, and self-contained -- a question that cannot be
understood without reading the journal will not get answered.

    ## Questions for the human

    - [ ] Q3 (2026-08-03): agent012 found that X saturates at rank 40. Worth
      chasing, or is Y more interesting to you?
      *Meanwhile*: proceeding with Y, so this is not blocking.

    - [x] Q2 (2026-08-01): should we optimize for rank or for apply cost?
      **answer** (2026-08-02): apply cost. Rank is a proxy we no longer need.

Conventions:

- Always say what you are doing in the meantime, so the human knows the cost of
  a slow reply.
- When the human answers in chat, write the answer in here and tick the box
  *before* acting on it. The answer has to survive a compaction just as the
  question does.
- If a question genuinely blocks all progress, do not queue it: stop and say so
  (see "When to stop" in `SKILL.md`).
- Ask sparingly, and batch related questions into one.

## Pending suggestions

Actions only the human can take. Subagents cannot modify tracked code, install
software, change the build, or edit this skill, so these accumulate here until
a human acts on them.

Format, in every bucket:

    - [ ] S<n> (YYYY-MM-DD, from agentNNN): <what to do>.
      <why it matters, in one or two lines -- what it unblocks or costs.>
      **blocks**: RQ-<x>            <- only when it does block a research question

Number them (`S1`, `S2`, ...) so the human can reply "do S3 and S7". Never
renumber; a completed suggestion keeps its number and gets ticked.

**Mark the blockers.** If a suggestion is the only thing standing between the
campaign and a research question it cannot otherwise settle, say so with a
`blocks:` line and mention it in chat. This is the single most valuable signal
in the file: it converts "here is a wish list" into "here is what to do next".

### The buckets

Use these headings, in this order. **Omit a bucket that is empty** -- the file
should stay short. If something genuinely fits none of them, use "Other"
rather than inventing a bucket.

- **Code changes** -- edits to the tracked repos (`pirate/`, `ksgpu/`,
  `pipmake/`). The common case.

- **Build, kernels, and environment** -- things that are not source edits but
  change what can be run: compiling an additional kernel variant into the
  registry, adding a build target, changing an environment variable or a
  container limit. Frequently a blocker, because a missing compiled variant can
  make a whole region of parameter space unmeasurable.

- **Software to install** -- packages or tools that are not present. Agents
  cannot install anything (the egress proxy blocks it), so this is always a
  request. Say what the agent tried to do without it.

- **Network egress allowlist** -- a domain an agent needed and could not reach.
  Per `CLAUDE.md` the agent must surface the exact domain, the URL or command,
  and why it was needed; the human runs `sbox-net allow <domain>`. Never work
  around a block.

- **Documentation and notes** -- corrections or additions to the tex notes,
  markdown docs, or docstrings. Includes "the notes say X, and we have measured
  that X is wrong", which is a genuinely valuable output of a campaign.

- **ch-research skill / workflow** -- changes to this skill. A subagent whose
  `PROMPT.md` was ambiguous, or which hit a rule that got in the way, or a
  convention that turned out badly. This is how the workflow improves between
  campaigns; do not suppress such a suggestion because it feels off-topic.

- **Resources and reference material** -- disk, GPUs, machine time, or source
  trees to add under `extern/` (`CLAUDE.md` explicitly invites the last of
  these). Also the place to flag when `research/` has grown large enough that
  the human may want to prune it, and what would break if they did.

- **Other** -- anything that fits none of the above.
