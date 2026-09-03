---
description: After implementing a plan, write plans/<topic>_report.md so a zero-context agent can pick the work up
---

You've just finished implementing a plan. Please write an implementation
report to `plans/<topic>_report.md`, alongside the plan it belongs to.

Assume the reader has ALREADY read the plan, and can read the code, the diff,
and the git log for themselves. So the report is not a summary of what the plan
said or of what the diff shows -- it is the place to record what is currently
only in YOUR context and would otherwise be lost when this session ends.

The report doesn't need to be long. Prefer one page of specifics over three
pages of prose.

What is worth recording (skip any that don't apply -- don't pad):

  - **Deviations and judgment calls.** Anywhere you did something other than
    what the plan said, and why. This is the single most valuable section.

  - **Places the plan was wrong.** A step whose premise didn't hold, an
    instruction that couldn't be followed as written, a tolerance or bound
    that turned out to be unachievable, a risk that was overstated or
    understated. Say what's actually true. If the plan is now misleading
    enough that a reader should distrust part of it, say which part.

  - **Validation actually run.** The exact commands and the actual NUMBERS --
    iteration counts, tolerances, worst-case differences, timings. "Green" is
    not a result; "worst relative difference 3.34e-07 over 8 iterations" is.
    If you recorded a baseline before starting, give both, so a re-run can be
    compared. If a test is randomized, say how much of the new code path it
    actually covered.

  - **Evidence that new tests have teeth.** If you deliberately broke
    something to confirm a new test catches it, record the mutation and the
    failure output. That's expensive to redo and easy to never think of.

  - **Harness and environment gotchas** discovered along the way: default
    flags that make a test run far too long, a build step that breaks a
    running process, a command that must be run from a particular directory.

  - **Facts you confirmed by searching**, whose value is that nobody has to
    search again: "X is the only caller of Y", "nothing in Z reads this",
    "this config is unchanged". Cite file:line, and re-check the line numbers
    before you write them -- your own edits will have shifted them.

  - **What is still open**: deliberately out of scope, left failing (and with
    exactly what error), or newly stale as a result of this work -- including
    other plans in `plans/` that this change has invalidated.

What to leave out:

  - A restatement of the plan's design or rationale.
  - A file-by-file walk through the diff.
  - A chronological narrative of the session ("first I did X, then Y").
  - Anything `git log` or `git diff` gives for free.

Follow the repo's markdown conventions (see CLAUDE.md): ASCII only in plans.
Plans are gitignored -- write the file, don't add it to git. Mention the
commit hash if the work has been committed, and say so if it hasn't.

Which plan: usually this is clear from context (we just implemented it
together, or it's named in the command arguments). If it isn't, ASK me
rather than guessing.
