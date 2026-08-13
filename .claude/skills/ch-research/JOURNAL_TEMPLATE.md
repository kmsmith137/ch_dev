# Journal schema

Template for `research/JOURNAL.md` (at the worktree root), the running log
kept by the toplevel agent of the `/ch-research` workflow (see `SKILL.md`,
alongside this file).

The journal is the toplevel agent's memory. It is the one file that must stay
readable after that agent's context has been compacted, and the one file a
fresh toplevel agent reads to pick up where the last one left off. So: one entry
per subagent, appended in chronological order, never rewritten. Keep each entry
short -- the subagent's `<workdir>/RESULTS.md` is not deleted, and is where the
detail lives.

The top of the file should also restate the question being worked on, in the
toplevel agent's own words, before the sections below.

## File layout

    # Journal

    <the three header sections below>

    ## Experiments

    <entries, oldest first>

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
    - **suggestions**: code changes, packages, or ch-research skill changes
      the subagent asked for, or "none". These are requests to the human --
      no agent acts on them.
    - **files**: `agentNNN/RESULTS.md`, plus anything notable
      (plots, `.npy` data, scripts worth reusing).

## Notes on the fields

**status.** `failed` means the subagent crashed, ran out of time, or wrote no
`RESULTS.md`; record it anyway, since a failure that repeats is itself a result.
`superseded` is set later, by a subsequent entry, when a result is overturned --
edit the status field of the old entry but leave its text alone.

**result.** Prefer numbers to prose. "rank 96, D = 0.081, 4 min" beats "worked
well". If the experiment produced a rank/accuracy frontier rather than a point,
put the frontier in `RESULTS.md` and quote one representative point here.

**verdict.** This is the field that makes the journal worth re-reading. The
result says what happened; the verdict says what to do about it. An entry whose
verdict is missing tends to get re-run by a later toplevel agent.

**suggestions.** Also mirror these into the "Pending suggestions" section at the
top of the file, so they are visible without scanning every entry. Subagents
cannot modify git-controlled code, install software, or edit the ch-research
skill, so these accumulate until a human acts on them.

## Header sections

Three short living sections at the top of the file, rewritten in place as the
picture changes (unlike the entries, which are append-only):

    ## Open questions

    - <question> (raised by agentNNN)

    ## Pending suggestions

    - [ ] <code change, package, or skill change> (from agentNNN)

    ## Questions for me

    - [ ] Q<n> (YYYY-MM-DD): <question>. <what you are doing meanwhile>
    - [x] Q<n> (YYYY-MM-DD): <question>
          **answer** (YYYY-MM-DD): <what the human said>

The three are distinct. "Open questions" are research questions for the
campaign to settle by experiment; "Pending suggestions" are actions only the
human can take (code changes, installs, skill edits); "Questions for me" are
decisions the human is being asked to make, which do not block. Answers are
written back into the entry, not just acted on, so they survive a compaction.

## Example entry

Illustrative only -- the domain will differ.

    ### agent007 -- SVD of dense A at rank 10, no detrender

    - **date**: 2026-08-03
    - **status**: done
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
