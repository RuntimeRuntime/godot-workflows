# Diagnose a Godot defect

Capture intended versus observed behavior, exact engine and scene, input/state
sequence, and frequency. Use native debugger, remote scene tree and collision or
navigation overlays when they resolve a concrete question. Read the relevant
[topic](topics/index.md) rather than guessing unfamiliar native behavior.
For disagreement between tool-driven interaction and engine-event tests, follow
the delivered-input diagnosis in [UI contracts](ui-contracts.md).

Test one falsifiable hypothesis with the cheapest useful observation. Preserve
the original failure. Declare relevant RNG seed/state/reset, physics/timing
conditions, awaited completion and deadline; a seed does not make all physics
deterministic. Use separate controlled attempts with retained logs and reasons.

After two unsuccessful repairs of the same finding without new diagnostic
evidence, change the investigation: acquire the missing observation, reduce the
case or identify the specific external decision. This is a configurable operating
default, not permission to abandon a solvable task. New evidence can justify more
work. A later green rerun alone does not resolve an intermittent failure.

Retest the original scenario and affected regressions after correction. Link the
diagnosis/correction to retained failed and passing attempts in the task handoff.
Use the game's existing generic diagnosis skill when available; this procedure
also stands alone.
