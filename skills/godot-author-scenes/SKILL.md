---
name: godot-author-scenes
description: Create or change editable Godot scenes, Resources, Inspector tuning, native level/animation/import workflows or persisted editor tools. Use for saved composition and public scene wiring. Arithmetic-only edits and transient runtime-only nodes need this skill only when saved authoring also changes.
---

# Author native Godot content

Read the game's instructions/profile and the affected saved files. Distinguish
fixed authored content, procedural runtime content and transient effects. Preserve
the game's engine pin and existing conventions.

For substantive composition, dependency or facility choices, use
[feature planning](references/feature-planning.md) and selected
[native topics](references/topics/index.md). Read the relevant topic's official
sources for the actual version. [Discovery](references/discovery.md) covers gaps
and conditional untrusted-content/protocol follow-up. Custom/procedural choices
remain legitimate when requirements justify them.

Save fixed hierarchy and editable data in native scenes/Resources where suitable.
Separate parentage from ownership and persistence; preserve nested instances.
Give public methods/signals explicit contracts and intentional types/dynamic
boundaries. Name a wiring owner, usually the common ancestor for siblings.
For shared mutable state or delayed work, read [state/lifetime](references/state.md).

Acquire [GT05 observations](references/verification.md): reopen the saved scene,
inspect assignments/exports/wiring, and establish selected tuning's gameplay
effect in a recorded disposable variant. Exercise changed editor automation in
both editor and game contexts and select configuration-feedback/recovery cases
independently. Record acquisition executor, actual observer, scene, source/variant
identity, expected/observed outcomes and supporting artifacts.

Run relevant import/parse/behavior checks with the bundled
`scripts/godot_workflow.py`; its `--help` describes the interface. A runtime-looking
scene does not establish saved authoring. Required unsupported observations remain
blocked. Finish with native artifact paths, decisions/exceptions and fresh evidence
or explicit gaps. [Review](references/review.md) supplies selective investigation.
