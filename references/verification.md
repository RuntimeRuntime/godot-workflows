# Verification and result limits

For a source-only assessment, use [source-only review](review.md#source-only-review).
The execution and result requirements here apply to the selected verification
scope; reading source alone does not create a verification run or acceptance.

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

A selected [cohesion review](cohesion.md) supplies its own disposition alongside
these results. The helper does not validate architectural judgments in task data;
a passing summary cannot supply a missing cohesion assessment.

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

## Contract examples

Select examples from the changed requirement before interpreting a generated
result as correct. An oracle is the assertion or observation that distinguishes
the intended outcome from its relevant failure. Choose applicable cases, not a
fixed test count or a requirement to exercise unrelated features.

| Changed contract | Useful oracle and boundary |
| --- | --- |
| Composite art or authored placement | Discover expected motifs/objects, then check complete footprints, caps and intended clearance. Inspect a real stamp at display scale; nonempty valid cells alone cannot establish art quality. |
| One-shot animation | Trace ordered poses labeled by animation/state through recovery when replay matters. One completion can still accompany an unwanted final rewind. Explicit loops/combos use their own contract. |
| Strike filtering | Prove active strike frames occurred with a target just outside the shape; pair with actual contact. A passive enemy outside its AI activation range does not test the strike guard. |
| Grace or buffering | Accept inside and reject outside the designed window; cover consumption/reset at declared physics timing. Assess feel separately. |
| Hit response | Cover surviving and fatal outcomes, once-only completion and affected pause/reset/independent-instance state. The chosen visual effects remain design choices. |
| Render order | Check the intended inherited Z/canvas relationship and observe actual overlap between representative actors and decoration/interactables. |

Record the test entry point: a direct damage method checks local response; an
engine event checks routing through the saved scene; device input adds delivery
evidence. Combine them when the requested contract spans those boundaries.
Collection-wide checks need expected nonempty discovery so missing objects cannot
make an empty loop pass. Before promoting a new oracle/example, use a targeted
known-bad case where useful; retain valid exceptions and the result's limits.

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
For changed bindings, follow the physical-event path in [input verification](topics/SH-03.md).
Agent observation requires demonstrated access; named human observation can cover
unsupported interactions. Missing required observation remains blocked.

When an acquired claim remains applicable to a new run, follow
[observation reuse](observation-reuse.md). Reuse retains original acquisition and
provenance, validates declared dependencies and failure history, and is counted
separately from newly acquired records. Before moving evidence or removing its
temporary roots, create and verify a [historical archive](evidence-archives.md).
Archive integrity is separate from current-project acceptance.

The summary can establish current selected evidence completeness, never semantic
correctness or independent enforcement. The task's outcome and acceptance remain
human/model judgments. An explicit owner accepted-risk record may accompany a
handoff; keep failed checks and GT09 failed and label `accepted_with_risk`.
This draft does not implement a waiver/approval engine. Missing required evidence
stays open. A scope change is recorded as a new task, not relabeled failed evidence.

At acceptance and reuse, distinguish original candidate hashes, the adapter's
normalized checking copy and controlled variants. Characterize native UID/settings
serialization differences separately from authored edits such as added terrain.
This comparison supplies judgment, not an automatic freshness exemption: use a
current check or valid linked reuse before a current acceptance claim. Keep an
older pass attached to its recorded source when present content has changed.

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
