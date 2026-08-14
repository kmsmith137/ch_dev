# Journal schema

Template for `research/JOURNAL.md` (at the worktree root), the running log
kept by the toplevel agent of the `/ch-research` workflow (see `SKILL.md`,
alongside this file).

The journal is the toplevel agent's memory. It is the file that must stay
readable after that agent's context has been compacted, and the file a fresh
toplevel agent reads to pick up where the last one left off.

It is paired with `research/HIGH_LEVEL.md`, the human-facing file (see
`HIGH_LEVEL_TEMPLATE.md`). The split is by audience:

- **`JOURNAL.md` (this one) is for the agent**: the full restatement of the
  question, the research questions, and the per-subagent entries.
- **`HIGH_LEVEL.md` is for the human**: status, questions for the human, and
  pending suggestions.

**Nothing is mirrored between the two.** In particular, suggestions live in
`HIGH_LEVEL.md` and their status is tracked there and nowhere else. An entry
here may note that a subagent *made* suggestions, but must never track whether
they have been acted on -- that would be a second source of truth, and it
would drift.

## Two kinds of question, named consistently

- **Research questions** live here. They are questions the campaign settles by
  running an experiment. The stopping rule reads this section.
- **Questions for the human** live in `HIGH_LEVEL.md`. They are decisions only
  the human can make, and they never block.

Use these two names verbatim, everywhere. They are easy to confuse and the
consequences differ: a research question in the wrong file is a question nobody
will run an experiment for, and a question for the human in the wrong file both
goes unanswered and permanently disables the stopping rule.

## File layout

    # Journal: <campaign name>

    <full restatement of the question -- see below>

    ## Research questions

    ## GPU assignments

    ## Experiments

    <entries, oldest first>

**The full restatement of the question goes here**, at the top, in the toplevel
agent's own words: the question, what a good answer would look like, and which
existing code is relevant. Every subagent prompt inherits it, so it is worth
getting right. (`HIGH_LEVEL.md` carries a one-line version of the same thing,
for the human.)

## Research questions

The live list for the **current campaign**, rewritten in place:

    ## Research questions

    - RQ-A: <question> (raised by agentNNN)
    - RQ-B: ~~<question>~~ **settled by agentNNN**: <the answer, in one line>

Settled questions may be struck through and kept for a while -- the answer is
often what a later prompt needs -- but the section must genuinely empty out as
the campaign converges, because **the stopping rule reads it**. Two corollaries:

- Never park anything here that an experiment cannot settle. A question that
  depends on the human belongs in `HIGH_LEVEL.md`; a steering note belongs in
  its own dated note near the top of this file.
- A question that is blocked on a human action (a code change, a kernel build)
  is not a live research question. Either state it as blocked and move the
  action into `HIGH_LEVEL.md` as a suggestion with a `blocks:` line, or drop it.

## Campaigns

A campaign is one invocation of the skill against one question. When a new
campaign starts in an existing `research/` tree, do not start over and do not
renumber:

- **Keep numbering subagents upward** (`agent008`, ...). New prompts routinely
  cite old workdirs, and reusing a number would make those citations ambiguous.
- **Keep numbering questions and suggestions upward too**, across campaigns
  (`Q4`, `S12`, ...). The human refers to these by number in chat, sometimes
  long after the fact.
- **Add a divider** before the new campaign's entries:

      # Campaign 2: <name>  (started YYYY-MM-DD)

- **Freeze the previous campaign's research questions** under its own section.
  The live "Research questions" section describes the current campaign only.
  If the new campaign still cares about an old question, re-adopt it explicitly
  by restating it in the live list.
- **Write a short "what campaign N-1 established" block** below the new
  campaign's restatement: the handful of results the new work builds on, with
  numbers. New subagent prompts inherit *this* rather than the previous
  campaign's restatement, which is how the new campaign avoids re-deriving
  settled results.

## Entry schema

One `###` block per subagent. Fields in this order; omit a field only if it is
genuinely not applicable.

    ### agentNNN -- <one-line title>

    - **date**: YYYY-MM-DD
    - **status**: done | failed | superseded
    - **question**: the one thing this experiment was meant to settle.
    - **setup**: config (rank, nfreq, subbands, Detrender2d params), which code
      was used, seed. Enough to re-run.
    - **result**: the headline number(s). Rank achieved, D value, wall-clock.
      Say "inconclusive" if it was.
    - **verdict**: what this changes about the plan. Pursue / drop / needs
      follow-up, and why.
    - **suggestions**: a one-line note that the subagent made suggestions, and
      where they are (`agentNNN/RESULTS.md` section N), or "none". Do NOT track
      their status here -- that lives in `HIGH_LEVEL.md`.
    - **files**: `agentNNN/RESULTS.md`, plus anything notable
      (plots, `.npy` data, scripts worth reusing).
    - **epilogue**: added later, and updated as often as needed. See below.

## Notes on the fields

**status.** `failed` means the subagent crashed, ran out of time, or wrote no
`RESULTS.md`; record it anyway, since a failure that repeats is itself a result.
`superseded` is set later, when a result is overturned -- change the status
field, leave the original text alone, and explain in the epilogue.

**result.** Prefer numbers to prose. "rank 96, D = 0.081, 4 min" beats "worked
well". If the experiment produced a rank/accuracy frontier rather than a point,
put the frontier in `RESULTS.md` and quote one representative point here.

**verdict.** This is the field that makes the journal worth re-reading. The
result says what happened; the verdict says what to do about it. An entry whose
verdict is missing tends to get re-run by a later toplevel agent.

**epilogue.** The one mutable part of an entry. Everything above it is written
once and left alone; the epilogue is appended to and rewritten by the toplevel
agent at any later time. Use it for anything that changes how the entry should
be read:

- a result **superseded or refuted** by a later experiment;
- an **error found after the fact** (a wrong number, a misread units, a
  premise that turned out false);
- a later experiment that **sharpened or narrowed** the claim (the result holds
  but only in a regime the entry did not state);
- a **caveat discovered later** that a reader of this entry needs.

Date each addition and name the agent that caused it:

    - **epilogue**:
      - (2026-08-05, agent014) The SVD verdict here is too broad. It holds for
        the detrended case only; with no detrender a rank-16 SVD reaches
        D ~ 1e-6. See `agent014/RESULTS.md` section 5.
      - (2026-08-06) The "2 GB of RAM" claim is a units misread; the machine
        has ~2 TB. No result depends on it, but the coverage limits stated
        above were self-imposed for a bad reason.

The epilogue exists so corrections stay **next to** the thing they correct.
That is deliberate: an agent reading an entry cannot miss its epilogue, whereas
it could easily read the entry and never read a correction filed elsewhere.

**A correction is not optional, and it is not rude.** A subagent's `RESULTS.md`
is immutable, so if it contains a claim later shown to be wrong, the epilogue on
its journal entry is the only place that fact can live. Write it plainly.

If the correction also affects how someone should *use* a shared artifact --
a promoted module in `toplevel/`, a published baseline number -- put a one-line
warning in `HIGH_LEVEL.md`'s status paragraph and in `toplevel/README.md` too.
The epilogue is the record; those are the places an agent will trip over it.

## Example entry

Illustrative only -- the domain will differ.

    ### agent007 -- SVD of dense A at rank 10, no detrender

    - **date**: 2026-08-03
    - **status**: superseded
    - **question**: is a truncated SVD ever admissible under D?
    - **setup**: rank-10 tree, 400 channels, no subbands, no Detrender2d,
      seed 42; dense A from PfAvarExact, SVD via numpy. 8 cores, no GPU.
    - **result**: spectrum falls off fast -- 64 singular values capture the
      matrix to D = 0.03; rank 32 gives D = 0.21. Dense A took 6 min.
    - **verdict**: confirms the no-detrender case is easy, and gives a baseline
      frontier to compare against once a Detrender2d is switched on. Next: rerun
      with W = 0 and W = 4 and see how the spectrum degrades.
    - **suggestions**: none.
    - **files**: `agent007/RESULTS.md`, `agent007/spectrum.png`,
      `agent007/A_dense.npy`
    - **epilogue**:
      - (2026-08-05, agent014) Superseded. These numbers are from a synthetic
        matrix with many near-duplicate rows; on real maps the same code gives
        D = 0.21 at rank 64, not 32. The qualitative conclusion survives, the
        numbers do not. Do not quote this entry's frontier.
