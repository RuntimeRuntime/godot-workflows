# Validation record

This draft's reports distinguish machine checks from editor/game observations.
All checks use disposable copies, and deliberate faults stay outside the authored
fixture. The fixture's own required observations remain part of its default scope.

## Demonstrated during implementation

- Godot `4.7.1.stable.official.a13da4feb` and GUT `9.7.1`, locked at
  `aeb5d4f3f7f0a6c9b5e178876d6c99b791fda605`.
- Native cold import, explicit project-owned script checks and saved-resource loads.
- Eight real-scene tests: saved children, tuning effect, instance state, intentional
  definition sharing, reentry/callbacks, settled teardown, pause/resume and ownership.
- Helper regressions for reports, freshness, missing observations, retained failed
  attempts, timeout/diagnostics, packaging conflicts and standalone operation.
- A fresh independent agent exercised eight natural-language requests against the
  packaged descriptions and reference branches. Its selection/guidance report is
  retained in `selection-trials.json`. This is not a measured productivity benefit
  or proof of automatic discovery by a newly started desktop chat.

`tools/calibrate_fixture.py` runs known-good/fault variants through the actual
checking command. Its machine-readable results and tool hashes are saved under
the root ignored `.godot-workflow-artifacts/` directory. A compact implementation
snapshot is retained in `implementation-results.json` after the completed run.

## Editor and visible-play observations

All three declared observations passed after native control became available.
The [observation results](observation-results.json) retain methods, outcomes and
capture links; [exact source identities and transformations](evidence/transformations.json)
identify the baseline and separate controlled tuning variant.

| Case | Observed outcome |
| --- | --- |
| Editor reopen | Saved enemy children, Health 3, state and definition assignments survived a fresh editor reopen |
| Inspector tuning | Left Health changed 3 to 5 through the Inspector, survived save/reopen and changed defeat from the third hit to the fifth; right stayed 3 |
| Visible pause/input | One real left click affected only left; Pause/Resume added no hit; an explicit subsequent hit worked |

The original [blocked acquisition attempt](editor-play-attempt.json) remains as
history. It was an access failure, not an observed gameplay defect. The completed
observations used the copied editor/application, native accessibility and real
mouse input, with screenshots and Inspector accessibility text retained. Only the
copied editor's accessibility setting was changed.

The archived implementation run passed GT09 with all eight scene tests and all
three observations under its recorded helper identity. Review subsequently changed
the helper; its freshness check now correctly blocks that old run. The captures
remain evidence of the observed fixture behavior, rather than new observations of
the reviewed adapter. A fresh full fixture claim would require new observations.
The reviewed helper has separate current machine-only calibration below. The
Starfall Courier real-game pilot subsequently ran; its bounded results are below.

## Draft review

The complete initial draft was reviewed against the empty-tree baseline, using the
agreed first-draft scope and this repository's documented contracts. The focused
follow-up found no remaining issue in the reviewed fixes. Detailed outcomes and
tool identities are retained in [draft-review.json](draft-review.json).

### Standards

Five findings were fixed:

- Native application-setting syntax and override layers could escape the intended
  user-data mapping. The adapter now normalizes complete native setting identities
  and blocks unsupported override layers before candidate code runs.
- Configured file logs could write outside the disposable run. Unsafe log paths
  and their feature variants now block preflight.
- Project settings could hide native errors even when Godot returned zero. The
  checking copy now enables both diagnostic streams and their feature variants.
- Unresolved infrastructure errors could disappear after two reruns. Their state
  now propagates through the complete linked history.
- An existing GUT cache could bypass the pin. Bootstrap and calibration now verify
  its exact content digest, derived from the clean locked checkout.

### Spec

One finding was fixed: a changed or missing isolation-probe log could still allow
closure. Its path/hash now receive the same freshness checks as other process logs.

The reviewed helper passes 30 regression tests. Native calibration covers 34
good, faulty, unsupported and valid-exception scenarios, including actual candidate
user-data paths for alternate name spellings. The first review calibration retained
a timeout mismatch in preflight; the declared hung-case process allowance was raised
from four to ten seconds, and the complete expanded suite passed. All attempts are
retained locally; no earlier result was relabeled.

## Valid exceptions and unresolved scope

Intentional shared definitions, procedural transient content and a justified
Variant boundary remain valid. Public declaration typing needs contract review;
parsing alone does not enforce it. The 2D fixture does not certify 3D, networking,
XR, exports, renderer performance or arbitrary-code safety. Starfall Courier adopts a game-owned acceptance profile while leaving the toolkit
candidate rules advisory.


## Starfall Courier pilot and high-priority follow-up

The local `godot-workflow-pilot` game exercised the installed skills on Godot
4.7.1. Ten final real-scene tests passed, with saved-scene reopen, Inspector target
8 → 2 tuning and actual keyboard/mouse observations at 960×640 and 1200×800. The
pilot first exposed unsafe physics-callback shutdown, cross-instance pickups and
incorrect arrow bindings. Failed attempts remain evidence rather than being
relabelled as successful runs.

The 0.2 follow-up adds physical-event guidance/calibration, native Unicode
parsing diagnostics, linked observation reuse and portable historical archives.
The native Unicode fixture deliberately returns zero with passing GUT assertions;
the diagnostic must still fail the checking result. A reversed-arrow fixture must
fail its physical-input assertion. Reuse tests cover dependencies, timestamps,
legacy records and retained failures. Archive tests include relocation after
original temporary roots are deleted, missing/tampered evidence and unsafe paths.

Current calibration, independent-review and installed-pilot results are recorded
in `high-priority-results.json` after this validation completes. Historical pilot
bundles explicitly report source snapshots/raw task bytes that are no longer
available; preserved manifests and embedded task records do not reconstruct missing
bytes. Observation reuse across helper identities is an explicit reviewed decision,
not a new UI acquisition. This remains an advisory 2D/macOS pilot, with no measured
productivity baseline or export, 3D, audio, controller or gameplay-feel certification.

## Shape Company follow-up: cohesion and UI contracts

The second pilot in the research workspace exposed mismatched enemy previews,
gesture tests that bypassed native drag initiation, and malformed native-tool
drag events. A subsequent architecture review identified a workflow gap: G06/G21
criteria existed, but normal construction/closure did not explicitly retain a
cohesion decision. Guidance 0.2.1 adds that decision and targeted UI-contract
branches, preserving small-project exceptions and existing result semantics.

`cohesion-ui-cases.json` contains authored positive and negative review examples
and a manual application to the actual pilot. These are explicit decision oracles
and source-reading exercises, not an independent model forward-test or automated
cohesion detector. `cohesion-ui-results.json` records package, frontmatter and
existing helper-suite validation separately. No engine adapter or game behavior
changed, so this guidance update does not claim new runtime calibration.

Evidence origin: the human/agent pilot report at
`godot-research/pilots/02-shape-company-report.md`, final candidate digest
`be811d7f72f504b3a27439ac7232e96f29d4ff447ffe9653567db6244e2752ea`.
The installed packages remain standalone and do not depend on that research path.

## Independent Sol review of two projects

The 16 October 2026 forward-test is recorded in
`sol-forward-test-results.json`. A fresh GPT-6 Sol reviewer received complete
workflow 0.2.1 packages and neutral source snapshots for Shape Company and the
small two-target fixture, without prior reviews or expected dispositions. Input
hashes remained unchanged. It traced duplicated recruit-price presentation in the
pilot while retaining that scene arrangement, and retained the fixture's compact
Main/Enemy split. The parent compared its findings with six criteria sealed before
dispatch; this pair met those criteria.

The reviewer found an ambiguity in source-only review routing and reported fresh
runtime/editor/device evidence unavailable rather than inventing passing results.
That ambiguity is recorded as a follow-up; no guidance or game code changed in
this evaluation. Its extra background-click concern is conditional on intended
controls, not a demonstrated fixture defect.

The original report, independent JSON, input snapshots and parent comparison are
retained under `godot-research/workflow-forward-tests/2026-10-16-sol/`. This was a
source-review experiment, not new native certification. Packaged teaching examples
remained present, so the pilot is a regression case. One reviewer and two projects
do not establish general reliability or sensitivity to every overloaded controller.


## Source-only review clarification

Guidance 0.2.2 adds an explicit source-only assessment branch in `review.md`,
reached early from all three skill entrypoints and the verification reference.
It distinguishes test declarations, inspected historical results, fresh checks
and actual observations. Source review can close with evidence limits; it cannot
supply behavioral acceptance or waive a change task's required evidence.

`source-review-results.json` records the update and fresh independent GPT-6 Sol
check. The three regenerated skills were installed and their active bytes checked
before dispatch. Package/frontmatter validation and all 72 existing helper tests
passed. The reviewer applied the installed guidance to two separate requests over
the pilot and small fixture: source-only composition/test review and a current
behavior-acceptance assessment. It completed the source reviews, retained compact
composition, withheld behavior acceptance from incomplete evidence, and reported
no consequential instruction conflict. All 792 input hashes and sealed criteria
remained unchanged. Extra fixture concerns are qualified in the parent comparison.

The complete report and evaluation packet remain under
`godot-research/workflow-forward-tests/2026-10-16-source-review/`. This is a bounded
scope-routing regression with one reviewer and two previously used projects; no
new native behavior certification or game change is implied. Historical packet
omissions do not invalidate the original pilot observations.
