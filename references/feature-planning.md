# Plan affected Godot features

For substantive scene, dependency or state changes:

For rule IDs adopted by the game, read the affected sections of [candidate policy](policy.md).
The complete treatments, exceptions and primary source links remain available
there; unadopted rules remain advisory.

1. Match the user-visible task to [native topics](topics/index.md). Read only the
   relevant briefs and project-version official sources. Choose native, existing
   or custom facilities for a concrete requirement; valid custom work stays valid.
2. Choose saved scene boundaries, public methods/signals and intended types. Name
   consumers and justified Variant/dynamic boundaries. Parsing does not review
   public-declaration policy.
3. Give dependency wiring a clear owner, normally the common ancestor for sibling
   scenes. Keep internal paths local; record a justified scoped alternative.
4. Name mutable state, intentional sharing and delayed-work owners, including
   initialization, reentry, pause and teardown behavior.
5. State acceptance examples and relevant checks/editor/play observations. Record
   native candidate, chosen approach, reason, source version and uncertainty.

If a capability is unfamiliar or unlisted, follow [official discovery](discovery.md).
For untrusted runtime content or security-sensitive networking/services, follow
the conditional research boundary there even when a topic already matches.

## Reusable enemy example

An enemy scene owns fixed visuals and collision, exposes Inspector health, and
presents `take_damage(amount: int) -> void` plus `defeated`. The level wires
siblings/UI. Each enemy owns current health; an immutable definition may be shared.
Enemy-owned delayed work ends or is cancelled during teardown.

Baseline health is three, damage is one. In a disposable variant change health to
five through Inspector, save/reopen and verify defeat occurs once on the fifth hit.
Record the transformation and both source identities. Damage one of two enemies
without changing the other, then exercise spawn/removal/reentry and teardown.
Short internal paths, procedural transient effects and intentional sharing remain
valid. This is an example, not a required enemy architecture.
