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
