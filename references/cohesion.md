# Review scene and controller cohesion

Apply when creating a scene/controller, substantially expanding its
responsibilities, reviewing its composition, or when a change exposes consequential
coupling. Review the affected module and its consumers; a label, spacing or
arithmetic-only edit does not require a new architecture review unless it changes
a dependency contract or reveals such coupling.

The question is whether responsibilities can change safely through small,
intentional interfaces. A Main scene can contain UI and coordinate siblings.
Scene hierarchy size, script length and number of scene files do not answer that
question. Scene assets and behavioral modules are related but distinct.

## Trace a change, then decide

1. Name the affected owners of game rules/state, presentation, input requests and
   orchestration/lifetime. Several roles may share one owner. Include dependencies
   on child internals and consumers that rely on them.
2. Trace one plausible change grounded in the request or existing code: for
   example, change recruit price, change damage resolution, or rearrange a panel.
   Identify the actual files, methods and consumers that would need coordinated
   changes, and what could become inconsistent. Unrelated hypothetical expansion
   is not evidence that the present design needs extraction.
3. Assess the consequence. Independently changing rules mixed with presentation,
   duplicated policy values, UI state used as gameplay authority, external path
   assumptions, or incompatible lifetimes can justify a finding. Cite the actual
   coupling and change cost. Whole-scene integration tests are legitimate; needing
   UI to isolate a rule can be a clue, not a defect by itself.
4. Record one disposition:
   - **Keep combined:** explain why the traced change stays local and the shared
     context/lifetime is appropriate. Record any concrete limitation or revisit
     trigger. A small project can justify a compact controller; the word
     "prototype" alone does not establish coherence.
   - **Extract or correct:** name the responsibility and smallest change that
     removes the demonstrated cost. Consolidating duplicated data may suffice.
     If extracting, move responsibility behind typed methods/signals and name
     the wiring/state owner. A scene, Resource or lightweight script may fit.
     Moving nodes to another `.tscn` while the controller still knows their
     internals does not establish separation.
   - **Unassessed:** identify the missing source, consumer or expectation that
     prevents a supported decision. Keep that limit visible in the handoff.

A paragraph is enough for a small change. For a larger task, the optional
`cohesion_review` task field can hold owners, change trace, disposition, rationale
and revisit trigger. The CLI stores task data but does not evaluate this field.
An empty field is not a completed selected review. Preserve a small-project
exception when its traced change supports it; a finding should not prescribe
splitting every HUD, shop or button into its own scene.

## Check the selected result

After implementation, repeat the trace against the actual saved scene and
scripts. Confirm any extracted interface hides the dependency and the changed
contract has appropriate behavior/editor evidence. If keeping the design, verify
the reason still holds after the final change. Use an existing relevant review
lens; this check does not require another agent or standing committee.

Classify a demonstrated broken behavior or adopted requirement separately from
an advisory maintainability improvement. Fix material required defects under the
normal change workflow; an optional extraction does not become mandatory because
a reviewer prefers more scene files. Machine import, tests and GT09 completeness
do not establish cohesion. Report the selected disposition alongside those
results, without converting a judgment into an automatic gate.

## Examples and research basis

- A one-screen game owns a saved layout, nested reusable cards and one run-local
  controller. A price comes from one definition and presentation consumes that
  value. Native controls and coordinated lifetime can support **keep combined**.
- A short controller charges one price but separately hard-codes price text in
  several places. Trace a price change: consolidating the policy value is a
  concrete improvement; a separate shop scene is not automatically necessary.
- A damage method reads health from a formatted UI label. Changing the label for
  localization changes rule behavior. Separate gameplay authority from display;
  this can be corrected within the same scene when that remains cohesive.

This operationalizes [G06, G09–G11 and G21–G22](policy.md), preserving their
exceptions. The primary [Godot scene-organization guidance](https://docs.godotengine.org/en/4.7/tutorials/best_practices/scene_organization.html)
supports focused responsibilities, local dependencies and ancestor wiring; its
Main/World/GUI hierarchy is an example. [GDQuest's pattern guidance](https://www.gdquest.com/library/design_patterns_intro/)
explains the cost of abstractions and extracting after concrete needs appear.
These sources support the decision criteria, not a numerical overload threshold.
