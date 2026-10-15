---
name: godot-verify-behavior
description: Verify or diagnose changed Godot behavior through native import/parsing, real-scene tests, editor observations and visible gameplay. Use for acceptance evidence and test adequacy; prose-only edits without behavioral impact do not need gameplay verification.
---

# Establish intended Godot behavior

Read the requested outcome, game instructions/profile and affected native files.
Define concrete acceptance examples before interpreting generated behavior as
correct. Follow [verification](references/verification.md) for check scope,
evidence outcomes, source freshness, observation ownership and isolation.

Use `scripts/godot_workflow.py inspect --project <game> --godot <binary>`, then
`check` for the selected import/parse/test operations. Existing compatible tools
win; this first adapter understands GUT reports and does not replace other runners.
Use a task record for required checks/cases and editor/play scenarios. Public
typing, test adequacy and source-selection completeness still need judgment.

Test meaningful behavior through the actual scene path. Include independent
instances, repeated transitions, pause/input and failure cases when affected.
Declare relevant randomness/reset, timing, completion and deadlines. Reconcile
case IDs and report counts rather than trusting only an exit code. Preserve every
attempt; no automatic reruns erase a failure.

Acquire required editor/play evidence with a named actual observer and demonstrated
access. Record exact scene/revision, real inputs, expected/actual results and
captures using `observe`. Inspector tuning variants retain their transformation
and identity. Screenshots alone do not establish interaction, audio or feel.
Missing required observation remains blocked.

Use `summarize` to recheck freshness and required coverage. Inspect selective
[review findings](references/review.md), supported exceptions and unresolved
attempts before the final bounded claim. Explicit accepted-risk closure keeps
failed evidence failed. [Diagnosis](references/diagnose.md) and selected
[native topics](references/topics/index.md) resolve unfamiliar failures;
[discovery](references/discovery.md) preserves specialist follow-up boundaries.
