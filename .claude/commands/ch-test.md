---
description: Full test sweep (rebuild, ksgpu + pirate unit tests, toy + production quickstart searches with offline dedispersion); ~90 min
---

Please run the full test sweep for the ch repos. Work from the worktree
root (the directory containing ksgpu/, pirate/, pipmake/). Total expected
runtime is roughly 90 minutes; most of it is steps 5 and 6. Run the steps IN
ORDER -- each one gates the next. If a step fails, diagnose and fix it (see
"Bugs" below), then rerun that step before moving on.

Ground rules (these mirror CLAUDE.md; they apply throughout):

- Build with `make -j 32`, never plain `make`.
- Do NOT git commit, merge, rebase, pull, or push.
- Never bypass the network egress proxy.
- Set PYTHONUNBUFFERED=1 in the environment of every long-running process
  whose stdout you redirect to a file: python block-buffers redirected
  stdout, so log lines (including the readiness markers below) otherwise sit
  invisible in the buffer. C++ output flushes itself; python output does not.
- Keep all scratch files (logs, pid files, config copies) in an untracked
  location: the session scratch dir, /tmp, or pirate/plans/ (plans are
  never git-added).

## Step 1: rebuild both repos (fast if up to date)

The user may have merged or rebased since the last build. Rebuild ksgpu
FIRST (pirate links against it), then pirate:

    make -C ksgpu -j 32
    make -C pirate -j 32

Both must exit 0. After a merge/rebase an INCREMENTAL build occasionally
fails on stale objects; if a build fails with errors that look like
stale-state (missing generated files, undefined symbols that clearly exist),
run `make clean` in that repo and rebuild before treating it as a real
compile error.

## Step 2: ksgpu unit tests (~3 min)

    ksgpu test

(equivalently `python -m ksgpu test`). Every test must report pass and the
command must exit 0.

## Step 3: pirate quick unit tests (~3 min)

    cd pirate && pirate_frb test -n 10

Must exit 0 with all tests passing.

## Step 4: toy quickstart search (~10 min)

Run the "toy search" end-to-end: fake X-engine -> FRB search server ->
grouper -> sifter, plus RPC monitoring, streaming to disk, a random-write
RPC, a clean shutdown-cascade check, and an offline-dedisperser pass over
the acquired data.

Before starting:

- Read pirate/notes/quick_start.md ("Running a toy search" and "Running an
  offline dedisperser"). It is the authoritative list of commands, ports,
  and flags -- do NOT rely on command lines memorized from this file, since
  the details may have changed. If anything is unclear, read the source of
  the command in question (pirate_frb/__main__.py and the run_*.py modules).
- Run every pirate_frb command from the pirate/ directory: the config
  files are passed by relative path.
- Check that the ports named in the configs are free and that no stale
  pirate_frb processes are running.

Launching the persistent processes (sifter, grouper, server, fake X-engine,
rpc_status -- each runs until interrupted):

- Launch each as a background process, stdout+stderr redirected to a
  per-process log file, and record its PID (you will SIGINT one process
  later and verify that each one exited).
- Launch order is downstream-first: sifter, grouper, server, fake X-engine,
  then rpc_status. Before launching each command, wait until the downstream
  command has settled into its wait-loop, then wait 1 more second. Do not
  use blind sleeps; poll the downstream log for its readiness line.
  Readiness markers as of this writing (re-derive from the source if they
  have changed):
    - sifter:        "waiting for grouper(s) to connect"
    - grouper:       "waiting for FrbServer to connect"
    - server:        "All N server(s) started"  (the RPC port is not bound
                     until this line; toy init takes a few seconds)
    - fake X-engine: "FakeXEngine(s) running"
    - rpc_status:    "Running get_status"
- While waiting on a readiness marker, also watch every log for
  Traceback/RuntimeError/ERROR so a startup failure is detected instead of
  hanging your poll loop.

Streaming:

- Start a stream with rpc_start_stream, using the flags from
  quick_start.md. Save the printed acqdir name; the directory is created
  under the server's nfs_dir (printed at server startup).
- Poll rpc_show_streams every few seconds until the stream has written 2000
  files (the "files: ... written = N" line). This takes ~30-40 seconds
  (the toy runs ~16x faster than real time). If the count stops growing,
  investigate.
- Note: with fpga_seq_start=0 ("start asap"), the acqdir's first time-chunk
  index is wherever the ring buffer currently is, NOT t=0. Expected.

Random-write RPC (while the stream is still active):

- Run rpc_rand_write (see quick_start.md). Verify it exits 0 and prints the
  filenames it wrote, that the same filenames are reported as received by
  the running rpc_status process, and that the files exist on disk in a
  rand_write_{date}_{time} acqdir under the NFS dir. ("metadata not yet
  available" here would be a real failure -- data is already flowing.)

Cancel + shutdown cascade:

- End the stream with rpc_cancel_stream (by stream name), then verify via
  rpc_show_streams: status "inactive (cancelled)", files queued == written,
  errored == 0.
- Send SIGINT to the sifter (the END of the pipeline) and verify the
  shutdown cascades: within a few seconds ALL five processes must exit.
  Expected per-process behavior (these error messages are the documented
  "errors cascade backwards" path, not failures):
    - sifter: "interrupted; shutting down", exit 0
    - grouper: RuntimeError, sifter event not delivered
    - server: RuntimeError, grouper Session stream closed unexpectedly
    - fake X-engine: RuntimeError (MonitorRingbuf stream closed, or its own
      sifter send failing -- either is a valid cascade edge)
    - rpc_status: subscribe_files error, then "RPC client(s) stopped"
  Verify by PID that nothing lingers for more than ~10 seconds. (If you
  check for leftovers with pgrep -f, beware matching your own watcher's
  command line.)

Offline dedisperser:

- Run run_offline_dedisperser on the stream's acqdir, with the SAME
  dedispersion config the toy server used (see quick_start.md). It must
  enumerate the beam(s), process every chunk, and exit 0.

What "looks reasonable" means -- check ALL of these in the logs, not just
exit codes:

- server: per-chunk lines advance steadily, each well-formed and
  newline-terminated (including the FIRST per-chunk line).
- grouper: per-chunk coarse_snr_max baseline roughly 5-9, spikes near the
  injected SNR when an FRB is present; nevents 0 on baseline chunks,
  >= 1 on spike chunks.
- fake X-engine: "injected FRB" lines with sane beam_id/dm/fpga_timestamp/
  snr fields, spaced by the configured gap.
- sifter: BOTH event streams arrive -- FROM_SIMULATOR (truth) and search
  events (grouper) -- and search detections correspond to earlier truth
  injections with similar beam_id and DM. (A truth message's fpga window
  can trail its events' timestamps; events are reported when scheduled.)
- rpc_status: ring-buffer counters advance monotonically; streamed
  filenames are reported; no errors before the deliberate SIGINT.
- rpc_show_streams: written grows, errored stays 0.
- rpc_rand_write: filenames in its output, in rpc_status, and on disk.
- offline dedisperser: baseline snr_max roughly 5, and a spike (near the
  injected SNR) for EVERY truth FRB on the streamed beam inside the
  acquired chunk range -- check this explicitly, don't eyeball it.
  Cross-check recipe: grep the fake X-engine log for
  "injected FRB: beam_id=B" lines; tci = fpga_timestamp / seqs_per_chunk,
  where seqs_per_chunk = time_samples_per_chunk * seq_per_frb_time_sample
  (both printed at fake X-engine startup). Expect a spike within a few
  chunks of each truth tci. Adjacent-chunk echoes are expected (rudimentary
  peak-finding), as are spikes BEFORE high-DM events (early-trigger trees).
- Scan every log for unexpected errors/warnings from before the SIGINT.

## Step 5: production quickstart search (~45-60 min)

Repeat the whole step-4 exercise using the "Running a production search
(cf00/cf05)" section of quick_start.md, with these deviations:

- Run EVERYTHING on the same node, including the fake X-engine (ignore the
  "MUST BE ON CF00" note).
- Environment check FIRST. Read the production frb_server config and
  verify: the check_mountpoints directories are actually mountpoints
  (os.path.ismount), the ssd_dirs exist and are writable, the nfs_dir
  parent is writable and $USER is set (its {user} interpolation), free
  hugepages >= num_servers * host_memory_per_server (grep HugePages
  /proc/meminfo), and all GPUs are visible and idle (nvidia-smi). If
  anything is missing -- e.g. the sandbox was launched without the
  production storage mounts -- STOP and ask the user; the sandbox can only
  be changed from outside.
- The production config assumes the node's physical 10.x.x.x data NICs,
  which are not visible inside the sandbox (private network namespace).
  Copy the config to an UNTRACKED file (do not edit the tracked config)
  and rewrite the network addresses to loopback: every data_ip_addrs entry
  becomes 127.0.0.1 with a UNIQUE port (all receivers now share one IP --
  e.g. 5000, 5001, 5002, 5003). Check that the rpc_ip_addrs globs resolve
  in the sandbox (the sandbox mirrors the host's default interface, so
  e.g. '10.222.3.*' usually resolves); if not, rewrite them to loopback
  too and use those addresses in all rpc_* commands. Leave everything else
  (memory sizes, dedispersion config, ssd/nfs dirs, check_mountpoints, MTU
  minimums) unchanged -- loopback's MTU 65536 passes min_data_mtu. Pass
  the rewritten filename to run_server in place of the tracked one.
- The production server takes on the order of a minute to initialize
  (async allocation of very large memory pools). Do NOT start the fake
  X-engine before the "All N server(s) started" line.
- There are multiple servers and groupers (one per GPU). Given multiple
  addresses, run_toy_grouper runs each grouper in a child subprocess; wait
  for BOTH "waiting for FrbServer" lines before starting the server, and
  remember the cascade must take down the children too.
- Poll until the stream has written 1000 files (not 2000). IMPORTANT:
  choose the stream duration so it cannot expire early. -d is in seconds
  of DATA time; a stream writes one file per time chunk per streamed beam,
  and a chunk lasts time_samples_per_chunk * time_sample_ms (~2 s at
  production scale) -- so quick_start's example '-d 1000' yields only ~490
  files and then deactivates naturally. For 1000 files use e.g. '-d 2500'.
  If a stream DOES expire naturally, that is not an error: verify its
  status is "inactive" WITHOUT "(cancelled)", then start a longer one.
- Expect ~25-30 minutes of streaming for the 1000 files: the production
  pipeline runs at only ~1.3-1.5x real time.
- rpc_rand_write, cancel, cascade: as in step 4.
- Offline dedisperser: run on the 1000-file acqdir with the dedispersion
  config quick_start.md specifies for production acquisitions (NOTE: it
  differs from the config the server was started with). Expect a few
  minutes (~3 chunks/s at production scale).
- Truth cross-check as in step 4, with two production-specific allowances:
  a high-DM pulse sweeps MANY chunks (sweep_seconds =
  4148.8 * DM * (f_lo_MHz^-2 - f_hi_MHz^-2); accept a spike anywhere from
  a few chunks before the truth tci out to truth tci + sweep), and a truth
  event within the first few chunks of the acquisition may legitimately
  have NO spike (dedisperser warmup -- the documented "boundary effects
  near the beginning of the acquisition").
- Diagnostic note: if an rpc command to the host's own IP fails with
  "HTTP proxy returned response code 403", the sandbox launcher predates
  the NO_PROXY node-local exemption in sbox-common.sh; report it (the user
  must relaunch the sandbox) rather than working around the proxy.

## Step 6: pirate full unit tests (~30 min)

    cd pirate && pirate_frb test

(the default is 100 iterations). Must exit 0 with all tests passing. Run
this AFTER the searches so a mid-sweep failure surfaces in the cheaper
steps first, and make sure no pipeline processes are still running (the
tests need the GPUs).

## Bugs

If a step fails, it is possible the bug is in the test procedure, not the
code being tested; you may also find errors in the documentation or the
config files. Fix such bugs/errors as appropriate: fix, rebuild, and rerun
the failed step to verify. Do NOT git-commit anything -- summarize every
fix at the end so the user can review with `git diff`. If a failure
requires a judgment call or design decision, pause and ask the user.

## Final report

Finish with a complete report containing ALL of the following:

- Pass/fail for each of the six steps.
- The timings you observed: build time, per-step durations, server init
  time, files/sec while streaming, offline chunks/sec.
- The acquisition inventory table (see below).
- Every fix you made, with file references, so the user can review with
  `git diff`.
- Anything you skipped, worked around, or that needs the user's judgment.

### Acquisition inventory

The sweep writes tens of GB, so end the report with a table of everything
it created on disk -- one row per directory: path, size (`du -sh`), and a
short note on the contents (file count and chunk range for an acqdir).
Sweep BOTH nfs_dirs, and include the incidental directories (rand_write_*,
any cancelled or naturally-expired stream), not just the two main acqdirs:

    du -sh ~/pirate_toy/*/ /mnt/cs00/data/$USER/*/

Format:

    | Path                                            | Size | Contents                    |
    |-------------------------------------------------|------|-----------------------------|
    | /mnt/cs00/data/{user}/prod_stream_{date}_{time}  | 28G  | 1014 files, chunks 29-1042  |
    | ~/pirate_toy/toy_stream_{date}_{time}            | 337M | 3913 files, chunks 2435-6347|
    | ~/pirate_toy/rand_write_{date}_{time}            | 180K | 2 files                     |

Do NOT delete any of it -- the user decides what to keep. But DO mark the
rows that are throwaway scratch (e.g. acqdirs from a debugging experiment
rather than from steps 4 and 5) so the user can clean up selectively.
