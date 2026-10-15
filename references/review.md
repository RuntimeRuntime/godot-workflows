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

| Lens | Investigate |
| --- | --- |
| Authored scenes | Reopened hierarchy, ownership, assignments, Inspector usability, tuning effect, editor/runtime separation and selected recovery cases |
| State/lifetime | Mutable Resource identity, nested sharing/aliases, initialization/reentry, callbacks, pause, cancellation and settled teardown |
| Behavior/test adequacy | Real scene path, meaningful assertions, expected case discovery, visible interactions and acceptance examples |
| Conditional contracts | Changed public APIs/signals/types and consumers, autoload/InputMap/shared resources, moved assets and target-specific dependencies |

Each finding names requirement/rule, concrete trigger, consequence, location,
supporting evidence, severity and proposed disposition. A reviewer may return no
findings. Consolidate duplicate root causes. A preference, metric threshold or
`Node.new()` search alone is not a consequential defect; preserve valid procedural,
dynamic and sharing exceptions. Public typing is a judgment separate from parse.

The implementer verifies and repairs supported findings. Recheck the changed
behavior and affected regressions. Retain withdrawn/unresolved findings and
accepted exceptions with their reasons. An explicit authorized owner decision may
accept a demonstrated residual risk; it cannot manufacture a missing observation.
