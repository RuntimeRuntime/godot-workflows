# Verification and result limits

## Select evidence

| Family | First-draft support |
| --- | --- |
| GT00 environment/identity | Helper inventories source, exact engine/build and profile/task/tool hashes |
| GT01 format/lint | Use the game's existing configured tools; no bundled style gate |
| GT02 import | Cold isolated source copy, native import and diagnostic inspection |
| GT03 parse | Explicit project-owned script inventory plus loading saved scene/resource files; public-type review stays judgment |
| GT04 behavior | Pinned GUT/JUnit adapter; existing alternative runners remain usable outside this adapter |
| GT05 authored inspection | Named editor observations: reopen, inspectability, tuning effect, selected editor/runtime and feedback/recovery cases |
| GT06 visible play | Named observer, exact scene/revision, real interaction sequence and expected/actual outcomes |
| GT07 target export | Project-specific future adapter; required release evidence cannot be inferred from import/tests |
| GT08 measurement | Project-specific future adapter; lifecycle assertions can already run under GT04 |
| GT09 closure | Mechanical freshness/completeness summary; judgment and owner acceptance remain separate |

Run the bundled `scripts/godot_workflow.py` in an installed skill, or the toolkit's
`tools/godot_workflow.py`. Use `--help` for exact command options. Inspect first,
then select `check` operations. Supply a task JSON for declared acceptance and
required observations; the profile supplies defaults. An explicit narrowed check
selection cannot silently remove task-required checks. `summarize` reconciles them.

The profile is game-owned. `--godot`, `GODOT_BIN`, then discovered executables
select the machine binary; a declared engine pin must match. GUT is installed only
in the fixture by its bootstrap helper, never injected into adopted games.
For GdUnit4/another runner preserve the game's commands and evaluate its reports
deliberately; selecting the unsupported GUT adapter reports a blocker.

For editor/play acquisition, read [the demonstrated observation procedure](editor-observations.md).

## What records establish

Records use `pass`, `fail`, `error`, `blocked` or justified `not_applicable`.
Fail is observed violated behavior; error is unreliable execution/reporting;
blocked is required evidence unavailable/absent/stale. A timeout is error. Zero
tests fails the discovery expectation; required pending/skipped/missing cases
cannot pass even when the runner returns zero. Raw exit status stays visible.

Each run retains source file hashes (including dirty/untracked input), tool and
profile/task hashes, exact commands, deadlines, logs, reports and artifact hashes.
Closure checks the isolation-probe log as well as check-process logs. Unresolved
infrastructure errors remain open across every linked rerun until an evidenced
resolution is recorded.
Default attempts have no automatic retries. Link diagnostic reruns to the previous
run and record why; all outcomes remain available. A later pass alone does not
resolve an intermittent failure. Use `--resolution` only for an evidenced
diagnosis/correction or infrastructure resolution with affected retest.

`observe` records a named observer's conclusion and interaction sequence against a
declared scenario and source. It hashes attached captures; it does not prove that
the observer is truthful or that a screenshot establishes timing/audio/feel.
Record artifact provenance, the actual observed scene and any controlled variant.
Agent observation requires demonstrated access; named human observation can cover
unsupported interactions. Missing required observation remains blocked.

The summary can establish current selected evidence completeness, never semantic
correctness or independent enforcement. The task's outcome and acceptance remain
human/model judgments. An explicit owner accepted-risk record may accompany a
handoff; keep failed checks and GT09 failed and label `accepted_with_risk`.
This draft does not implement a waiver/approval engine. Missing required evidence
stays open. A scope change is recorded as a new task, not relabeled failed evidence.

## Isolation and compatibility

Engine operations use a disposable source copy and copied application/binary with
self-contained editor mode. On the calibrated Godot 4.7.1 macOS build, runtime
`user://` still uses the OS data path. The helper exclusively creates a unique
`godot-workflow-<run>` symlink there pointing into the run's data directory;
existing directories are never replaced. This needs write access to the OS data
parent. `cleanup-run` removes only that owned link after observations finish.
A clean probe uses Godot's native ConfigFile parser to normalize every base
application-name spelling, including root and section aliases, and establishes
the resolved `user://` path under the run before executing project scripts/plugins.
The checking copy enables stdout/stderr, including feature overrides, so project
settings cannot hide native diagnostics. These transformations are recorded.
Symlinked sources are blocked by this first adapter rather than followed outside
the declared source. Cache/editor/runtime state belongs to the run. The actual
editor and visible-game observation must identify that transformed copy.

This macOS/Linux editor-binary adapter does not provide exported-game isolation or
arbitrary-code containment. Custom user-data-directory settings, feature-specific application paths, binary
project settings and separate settings-override files/selectors block this adapter.
Configured file logs must stay under `user://` or `res://` without traversal or
backslash paths; external log paths need a project-specific adapter. Unsupported
platforms also block this adapter. Identity-sensitive behavior needs separate project
evidence. Process groups have external wall-clock deadlines; Godot's quit-after
iterations are not seconds. Runtime/resource loads may miss computed dependencies;
the inventory and unresolved dynamic dependencies remain review obligations.

Native CLI: [Godot 4.7](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html).
Isolation: [Godot data paths](https://docs.godotengine.org/en/4.7/tutorials/io/data_paths.html).
Runner: [GUT CLI](https://gut.readthedocs.io/en/v9.7.1/Command-Line.html)
(its version-addressed page currently displays an older heading; calibrate the pin).
