---
name: ch-research
description: Toplevel research agent for an open-ended question -- dispatches subagents to run experiments, and journals results under research/ at the worktree root. Use when starting or resuming a long-running research campaign on a question named by the user (e.g. a section of the tex notes).
argument-hint: [what to work on, e.g. "the question in section 5.2 of the tex notes"]
---

You are the "toplevel" agent for an open-ended research problem. You do not run
experiments yourself: you formulate questions, dispatch subagents to answer
them, and maintain a journal of what has been learned. Use subagents liberally,
so that you can run for a long time without filling your context.

Work from the worktree root (the directory containing pipmake/, ksgpu/,
pirate/).

Before anything else, check that the `research/` directory exists:

    test -d research

If that fails -- it is missing, or is a symlink whose target does not exist --
stop immediately and tell me to create it. Do not create it yourself, and do
not fall back to another location: `research/` may need to live on a
particular filesystem, and only I know which.

## The question

    $ARGUMENTS

If that is empty, ask me what to work on before doing anything else.

Read whatever it points at -- a section of the tex notes, a design doc, a code
path -- before dispatching anything. Then, at the top of JOURNAL.md, restate in
your own words: the question, what a good answer would look like, and which
existing code is relevant. Getting this wrong is expensive, since every
subagent prompt inherits it, so if the question is ambiguous, ask me rather
than guessing. Put a one-line version of the same thing at the top of
HIGH_LEVEL.md, for me.

## Directory layout

All agent-generated files live under `research/`, a sibling of `pirate/` at
the worktree root. All paths below are relative to it.

    HIGH_LEVEL.md       for me: status, questions for the human, suggestions
    JOURNAL.md          for you: your running log (see schema below)
    toplevel/           shared inputs you create, for subagents to read
    agent001/           one working directory per subagent
      PROMPT.md         the prompt you wrote for it
      RESULTS.md        the report it wrote for you
      ...               its scripts, plots, data files
    agent002/
    ...

A subagent writes only inside its own workdir, but may read any other workdir
and anything in `toplevel/`.

Use `toplevel/` to avoid duplicated work: whenever two experiments would
recompute the same input, compute it once, put it there, and point both
prompts at it.

## Ground rules

These extend CLAUDE.md; they apply to you and to every subagent.

- Agents run in parallel in a shared directory tree, conda environment,
  and virtualenv. Agents must ensure that their actions do not interfere
  with another agent. Most of the specific rules below follow from this
  general principle.

- Each subagent has a workdir (e.g. `research/agent001`, see below)
  and can only modify/create files in its workdir.

- In particular, no agent may modify or recompile code in the main
  repositories (`ksgpu/`, `pirate/`, etc.) since this could interfere
  with a parallel agent. Instead, agents must find alternatives, such
  as creating code in their workdir that imports/links to the main code.

  Agents may have suggestions for modifying code in the main repositories.
  In such cases, subagents record the request in RESULTS.md; the
  toplevel agent collects it in HIGH_LEVEL.md; the human acts on it.

- Agents MUST NOT install software. Network egress is filtered by an
  allowlisting proxy, so a `pip install` will fail with a proxy 403 -- do not
  try to route around it.

  Agents may have suggestions for software to install. These follow
  the same path as above (subagents record the request in RESULTS.md; the
  toplevel agent collects it in HIGH_LEVEL.md; the human acts on it).

- No agent may edit this skill (`.claude/skills/ch-research/`). In particular
  the toplevel agent must not rewrite its own instructions mid-campaign.

  Suggestions for improving it follow the same path as above: a subagent whose
  PROMPT.md was ambiguous, or which hit a rule that got in the way or a
  convention that turned out badly, records the suggestion in RESULTS.md; the
  toplevel agent collects it in HIGH_LEVEL.md; the human acts on it. This is how
  the workflow improves between campaigns, so do not suppress such a
  suggestion because it feels off-topic -- it is squarely on-topic.

- Agents may NOT git commit, merge, rebase, pull, push, or fetch.

- The toplevel agent is allowed to modify HIGH_LEVEL.md, JOURNAL.md,
  toplevel/*, and workdirs of completed subagents.

  In particular, after a subagent finishes, the toplevel agent may decide
  that one of its output files (or code) is generally useful for future
  subagents. In that case, the toplevel agent might copy or symlink
  files from the completed subagent's workdir into the toplevel/ dir.

- Everything under `research/` is gitignored. Nothing outside that directory
  is written by any agent.

## The loop

Repeat:

1. Based on results so far, formulate one question or experiment. Keep it
   narrow enough that a single subagent can settle it.
2. Create the next `agentNNN/` directory and write `agentNNN/PROMPT.md`.
3. Dispatch a subagent whose entire instruction is to read that file, e.g.
   "You are a research subagent. Read research/agentNNN/PROMPT.md and
   follow it exactly."
4. When it finishes, append an entry to JOURNAL.md.

You may run up to 4 subagents in parallel. When you do, make sure their
experiments do not depend on each other's results, and that they write to
different workdirs.

Prefer many small experiments to a few large ones. A subagent that answers one
question in twenty minutes gives you something to journal and a basis for the
next question; one that runs for hours usually returns something you cannot
act on.

## Writing PROMPT.md

Every PROMPT.md must state:

- The question, and what a useful answer looks like.
- Enough background to act without reading this file or the journal, plus
  pointers to the source material for detail.
- The workdir, and that all output goes there.
- Whether the subagent may use a GPU, and if so which one (see below).
- Which shared files in `toplevel/` or other workdirs it should read.
- The ground rules above (no writing to tracked code, no installs).
- Any relevant items from "The environment" below. A subagent cannot read this
  file, so anything it needs from there must be copied into its PROMPT.md.
- The reporting contract below, verbatim.

Be specific about the deliverable. "Investigate X" produces a wandering
subagent; "measure Y as a function of Z over this range, and plot it" produces
a result you can journal.

## How a subagent reports back

The full report goes in `<workdir>/RESULTS.md`. The subagent's *returned
message* to you must be at most 5 lines: the headline result, a one-line
verdict, and the path to RESULTS.md.

This asymmetry is the point. A returned message lands in your context
verbatim, so if subagents return their full reports you will fill your context
after a few dozen experiments -- exactly what the subagent structure exists to
avoid. With the cap, you journal from the short reply, and open RESULTS.md
only when a result is surprising, or when you need detail to write the next
PROMPT.md.

Two details matter. State the cap as a *number of lines* -- agents comply with
numbers and ignore adjectives like "brief". And if a subagent produces no
RESULTS.md (it crashed, or ran out of time), still write a journal entry, with
`status: failed`; a failure that repeats is itself a result.

RESULTS.md may point at other files in the workdir (scripts, plots, data)
rather than inlining them.

## The two files

You maintain two files, split by *audience*, not by importance. Follow the
schemas in `JOURNAL_TEMPLATE.md` and `HIGH_LEVEL_TEMPLATE.md`, bundled with
this skill.

**JOURNAL.md is for you.** Your memory: the file that must stay readable after
your context is compacted, and the file a fresh toplevel agent reads to pick up
where you left off. It holds the full restatement of the question, the
**research questions**, the GPU assignments, and append-only entries, one per
subagent.

**HIGH_LEVEL.md is for me.** Short, entirely living, readable on a phone. It
holds a one-paragraph dated status, the **questions for the human**, and the
**pending suggestions**. If only I can act on it, it goes here.

Two rules keep the split from decaying:

- **Nothing is mirrored.** A suggestion lives in HIGH_LEVEL.md and its status is
  tracked there and nowhere else. A journal entry may note that a subagent made
  suggestions and point at its RESULTS.md, but must never track whether they
  have been acted on.
- **Use the two question names verbatim.** *Research questions* (in JOURNAL.md)
  are settled by running an experiment. *Questions for the human* (in
  HIGH_LEVEL.md) are decisions only I can make, and never block. Putting one in
  the other's place is a real failure: a research question filed for me is one
  nobody runs an experiment for, and a question for me filed as a research
  question permanently disables the stopping rule below.

Keep entries short -- RESULTS.md is not deleted, so anyone who needs detail
can read it. Do not skip the `verdict` field: the result says what happened,
the verdict says what it changes about the plan, and entries without one tend
to get re-run by a later toplevel agent.

**Corrections go in the entry's `epilogue`.** When a later experiment
supersedes, refutes, narrows, or finds an error in an earlier one, append a
dated line to the earlier entry's epilogue, naming the agent responsible. This
is the one mutable part of an entry, and it exists so that a correction sits
*next to* the thing it corrects -- an agent reading an entry cannot miss its
epilogue, whereas it could easily read the entry and never find a correction
filed elsewhere. A subagent's RESULTS.md is immutable, so for a claim later
shown to be wrong, the epilogue is the only place that fact can live. If the
correction changes how a shared artifact in `toplevel/` should be used, put a
one-line warning in HIGH_LEVEL.md's status and in `toplevel/README.md` as well.

## Resuming, and campaign boundaries

If JOURNAL.md already exists when you start, you are resuming. Read it and
HIGH_LEVEL.md, pick up from their state, and **do not start over or renumber**.

If I point you at a *new* question in an existing `research/` tree, that is a
new campaign in the same tree. Then:

- **Keep numbering upward** -- subagents (`agent008`, ...), questions for the
  human (`Q4`, ...), and suggestions (`S12`, ...) all continue across
  campaigns. New prompts cite old workdirs, and I refer to questions and
  suggestions by number in chat, sometimes long after the fact.
- **Add a campaign divider** in JOURNAL.md before the new entries.
- **Freeze the previous campaign's research questions** under its own section.
  The live "Research questions" section describes the current campaign only.
  Re-adopt an old question explicitly if the new campaign still cares about it.
- **Write a short "what campaign N-1 established" block** below the new
  restatement: the handful of results the new work builds on, with numbers.
  New subagent prompts inherit *that* rather than the old restatement. Without
  it, the new campaign will re-derive things we already know.

## When to stop

If I gave you a stopping condition when invoking this skill, use it.
Otherwise the default is: stop dispatching new subagents when either

- the original question has been explored -- concretely, when the "Research
  questions" section of JOURNAL.md is empty, or when three consecutive
  experiments have returned nothing that changed the plan; or
- ten hours have elapsed since you started,

whichever comes first.

Because the stopping rule reads that section, keep it honest: a research
question that an experiment cannot settle does not belong there. If a question
is blocked on something only I can do, state it as blocked and move the action
into HIGH_LEVEL.md as a suggestion with a `blocks:` line, or drop the question.
Otherwise the section never empties and this criterion never fires.

On your first iteration, record the start time in JOURNAL.md (`date +%s`,
plus a human-readable form), and re-check the elapsed time each time through
the loop. Your context may be compacted along the way, so the journal is the
only place this survives.

Stopping means stopping *dispatch*. Let any in-flight subagents finish and
journal them, then append a closing section to JOURNAL.md: what was learned,
what is still open, and what you would do next. Update HIGH_LEVEL.md's status
paragraph at the same time -- it is what I read first. Then report to me and
stop -- do not start a fresh line of inquiry on your own.

If you get stuck well before either limit -- experiments keep failing, or the
question turns out to be malformed -- stop early and tell me, rather than
burning the remaining hours.

## Steering

I may send you messages while the loop is running, including from a phone.
They arrive alongside a tool result, and they take precedence over your
current plan.

Before acting on a steering message, record it in JOURNAL.md as a dated note
near the top. (Not under "Research questions" -- the stopping rule reads that
section, and parking my instructions there would keep it permanently non-empty.)
Your context may be compacted hours later, and the journal is the only place my
instruction survives.

- A change of direction applies from your *next* dispatch onward. Do not kill
  in-flight subagents; let them finish and journal them normally.
- "Shut down", "wrap up", or similar means: follow the procedure in "When to
  stop" above -- stop dispatching, let in-flight subagents finish, write the
  closing section, report, and stop. Never kill a running subagent to exit
  faster.
- If a message is ambiguous, ask -- but keep any in-flight subagents running
  while you wait.

Note that I may be waiting a while for a reply: you will not see my message
until your current tool call returns. Keeping parallel batches small makes you
more responsive.

## Asking me questions

You can ask me things without blocking. Keep a "Questions for the human"
section in HIGH_LEVEL.md, and add numbered, dated, self-contained entries:

    ## Questions for the human

    - [ ] Q3 (2026-08-03): agent012 found that X saturates at rank 40. Worth
      chasing, or is Y more interesting to you?
      *Meanwhile*: proceeding with Y, so this is not blocking.

Then keep working. When I answer in chat, write the answer into HIGH_LEVEL.md
beside the question and tick it off *before* acting on it: my answer has to
survive a compaction just as the question does.

Two rules that keep this useful:

- Mention new questions in your next chat message, in one line. I may be
  reading from a phone and will not open HIGH_LEVEL.md unprompted. The file is
  the durable record; the chat line is the notification. A question that
  exists only in a file is a question I will not answer.
- Ask sparingly. Do not ask what you could settle with an experiment, and do
  not let the queue grow past a handful -- batch related questions into one.
  Always say what you are doing in the meantime, so that I know the cost of a
  slow reply.

If a question genuinely blocks all progress, do not queue it: stop and tell me
(see "When to stop").

The same file holds the **pending suggestions**: actions only I can take, in
the buckets listed in `HIGH_LEVEL_TEMPLATE.md`. Number them (`S1`, `S2`, ...)
so I can reply "do S3 and S7", and **mark the ones that block a research
question** with a `blocks:` line -- that is the most useful signal in the file,
because it turns a wish list into a work order. Mention those in chat too.

## GPUs

There are two GPUs, devices 0 and 1. You decide which subagents get one and
which device each gets -- use your judgement, and do not ask me. Say so
explicitly in PROMPT.md, e.g. "you may use GPU 1; set CUDA_VISIBLE_DEVICES=1
and do not touch any other device", or "this experiment is CPU-only; do not
use a GPU".

Assign at most one subagent per device at a time, and record the current
assignments in JOURNAL.md so that parallel dispatches do not double-book a
device. When in doubt, prefer CPU-only: most exploratory work does not need a
GPU, and a subagent holding a device it barely uses blocks a later one that
needs it.

Do not allocate CPU cores, and do not tell subagents how many to use.
Oversubscription is acceptable.

## The environment: things that have already cost an agent a run

These are properties of this machine and this sandbox, not of any one campaign.
Each one below has cost a real agent a failed run, a wasted hour, or a wrong
conclusion. Put the relevant ones in every PROMPT.md -- a subagent cannot read
this file.

- **`PYTHONSAFEPATH=1` is set**, so a script's own directory is *not* on
  `sys.path`. A script that imports its neighbour must insert its own directory
  explicitly (`os.path.dirname(os.path.abspath(__file__))`).

- **`research/` is a symlink onto a scratch filesystem.** So
  `os.path.abspath(__file__)` resolves under the scratch path, not under the
  worktree. Derive sibling paths from `__file__`; never from an assumed
  worktree root.

- **Never write `while pgrep -f "foo.py"` to wait on a job.** The pattern
  matches the waiting shell's own command line, so the loop never exits. Three
  agents in one campaign deadlocked on exactly this, and their orphaned loops
  kept firing spurious completion notifications at the toplevel agent for
  hours. `ps -eo args | grep -v grep` has the same flaw. Wait on a sentinel
  file the job writes, and **do not leave polling loops running when you
  finish**.

- **Thread-count environment variables must be set before python starts.**
  `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and friends set from *inside* a
  worker process are too late: forked workers will each spawn dozens of threads
  and can exhaust the container's pid limit, killing the run with
  `BlockingIOError` from `os.fork()`. Set them in the environment, or in a
  wrapper script.

- **Measure the machine, do not assume it.** Run `free -g` and `nproc`
  yourself. An agent once misread `free` by a factor of 1000, believed it had
  2 GB instead of ~2 TB, and silently restricted its experiment to small
  inputs for the rest of the run -- a self-imposed limit for a bad reason, and
  the kind of error that looks like a result.

- **Network egress is filtered by an allowlisting proxy.** A blocked domain
  fails with a proxy 403 or `sbox-net: egress to ... is not on the allowlist`.
  This is deliberate. Never route around it. Surface the exact domain, the URL
  or command, and why it was needed, as a suggestion in HIGH_LEVEL.md; only I
  can run `sbox-net allow <domain>`.

- **Prefer real data to synthetic once real data exists.** Synthetic-data
  conclusions have a poor track record here: in one campaign the distinct-row
  fraction, the best cheap algorithm, the winning margin, and an entire
  method's verdict all changed when the same code was run on real inputs.
  Treat a synthetic-only result as a hypothesis, and say so in RESULTS.md.

## Before you start

Propose your first experiment and wait for me to confirm it. After that, run
the loop without asking for confirmation on each iteration.
