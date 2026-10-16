---
name: godot-state-lifecycle
description: Design, change or diagnose Godot mutable state, Resource sharing, initialization/reentry, signals, async work, pause, scene transitions or teardown. Use when ownership or lifetime affects behavior; unchanged ownership and presentation-only edits do not need this skill.
---

# Own state and work over time

For a source-only assessment, follow [source-only review](references/review.md#source-only-review).
The implementation and execution steps below apply to changes or requested
behavior verification.

Read the game profile and actual scenes/scripts/Resources plus their consumers.
Use [feature planning](references/feature-planning.md) for substantive changes.
Identify who owns mutable values, shared definitions and delayed work. Read
[state/lifetime guidance](references/state.md) for the affected branches.
When this work adds or expands controller responsibilities, apply the
[cohesion review](references/cohesion.md).

Check two independent instances, nested Resource/container identity and intended
aliases. Choose duplication/local-to-scene/explicit construction according to the
declared sharing contract; indiscriminate deep copying can break valid sharing.
Choose Resource, RefCounted or Node from serialization, editability and lifecycle
needs, using the selected [topic](references/topics/index.md) and official sources.

Exercise initialization, spawn/reentry, once-per-node readiness, pause, cancellation
and teardown after deferred cleanup settles. Assign connections and delayed work
to explicit owners so a restart/removal does not leave duplicate or late responses.
Simple enum state and scoped dynamic boundaries remain legitimate.

Turn the changed contract into real-scene assertions and relevant visible
scenarios using [verification](references/verification.md). Run the bundled
`scripts/godot_workflow.py` for supported checks. Preserve seed/reset/timing and
attempt history; use [diagnosis](references/diagnose.md) when repairs lack new
evidence. Security-sensitive networking/services and untrusted runtime content
also follow [conditional research](references/discovery.md).

Finish with state/work ownership decisions, supported sharing exceptions,
affected-scene results and unresolved evidence. Select the state/lifetime
[review lens](references/review.md) for consequential uncertainty.
