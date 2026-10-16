# Selective Godot review

Select relevant responsibilities for consequential changes. Usually one lens is
enough; at most two simultaneous responsibilities is an adjustable starting
default. A small documentation correction normally needs no gameplay review.
These are review guides, not installed custom agents or a mandatory committee.

Give a reviewer the outcome, acceptance examples, adopted policy/exceptions,
candidate identity, relevant native files and raw evidence. Avoid presenting the
author's rationale or previous verdict as the answer. Inspect existing evidence
first and request targeted recapture only for a concrete gap. Review does not
automatically grant editing permission or acceptance.

## Source-only review

When the request is a source-only assessment, inspect the relevant scenes,
scripts, Resources, consumers, tests and supplied evidence without automatically
running native checks or acquiring editor/play observations. Apply the selected
lenses to what those artifacts can establish. For cohesion, retain a concrete
change trace and keep/extract/unassessed disposition. Missing source or an unknown
contract may leave a specific judgment unassessed.

Label evidence by origin: source/test declarations, inspected historical results
(with source identity and applicability limits), checks executed during this
review, and editor/device observations actually acquired. Reading a test does
not establish a pass; inspecting a prior result does not make it a fresh run.
Report runtime/editor/device behavior outside the review scope as not assessed,
rather than failing or blocking the source review solely because execution was
not requested. Finish with supported findings, dispositions and evidence limits.

This branch does not grant behavioral acceptance or waive required evidence for
an implementation or behavior-verification task. If the request includes those
outcomes, follow [verification](verification.md) for that scope; missing required
checks/observations remain blocked. Do not narrow an existing task or relabel
failed evidence to obtain source-only closure.

## Review lenses and findings

| Lens | Investigate |
| --- | --- |
| Authored scenes | Reopened hierarchy, ownership, assignments, Inspector usability, tuning effect, editor/runtime separation and selected recovery cases |
| Scene/controller cohesion | Apply the [cohesion review](cohesion.md) to selected new/expanded modules: trace an actual change and justify keeping or separating responsibilities |
| State/lifetime | Mutable Resource identity, nested sharing/aliases, initialization/reentry, callbacks, pause, cancellation and settled teardown |
| Behavior/test adequacy | Real scene path, meaningful assertions, expected case discovery, visible interactions and acceptance examples |
| Conditional contracts | Changed public APIs/signals/types and consumers, autoload/InputMap/shared resources, moved assets and target-specific dependencies |

For changed gestures or stat previews, include the selected
[UI contract](ui-contracts.md); handler success alone does not establish the
native gesture or displayed/gameplay agreement.

For test adequacy, use the selected [contract examples](verification.md#contract-examples).
Trace the entry point and prove a negative reaches the guard it claims to test;
inspect temporal order when a final state or event count can miss a replay.
Distinguish a missing sensitivity case from a demonstrated implementation defect.

Each finding names requirement/rule, concrete trigger, consequence, location,
supporting evidence, severity and proposed disposition. A reviewer may return no
findings. Consolidate duplicate root causes. A preference, metric threshold or
`Node.new()` search alone is not a consequential defect; preserve valid procedural,
dynamic and sharing exceptions. Public typing is a judgment separate from parse.

The implementer verifies and repairs supported findings. Recheck the changed
behavior and affected regressions. Retain withdrawn/unresolved findings and
accepted exceptions with their reasons. An explicit authorized owner decision may
accept a demonstrated residual risk; it cannot manufacture a missing observation.
