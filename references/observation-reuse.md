# Reuse an acquired observation

Use `reuse-observation` when a new checking run needs an observation whose actual
acquisition still supports the same claim. Keep the acquired record and captures;
reuse creates a linked record rather than presenting another acquisition.

## Record the claim's dependencies

`observe` defaults to all candidate source files. This conservative scope rejects
reuse after any source addition, removal or change. For a bounded claim, nominate
its source files with repeated `--dependency <project-relative-file>` arguments at
acquisition. Include the scene, scripts, Resources, assets and consumers that can
affect the claim. Project settings and the game profile are always included.
Computed dependencies or uncertain behavioral reach justify the default full scope.
The helper checks the nominated hashes; dependency completeness remains judgment.

A controlled Inspector variant retains its own source manifest, digest and stated
transformation. It does not establish unrelated behavior that differs from the
candidate. Changing a nominated dependency requires a new observation; a free-text
reason does not waive this requirement. Even a native formatting change to project
settings invalidates reuse under this first adapter. Complete routine import/native
save work before acquiring evidence when possible.

`observe --acquired-at` can retain a known Unix acquisition timestamp. Otherwise
acquisition time defaults to recording time and is labelled accordingly. The
helper does not infer the time of an interaction from a screenshot or claim that
recording time proves when the interaction occurred.

## Reconcile a current run

Run the current required checks first, then select an original passing observation:

```sh
python3 tools/godot_workflow.py reuse-observation \
  --run /path/to/current/run.json \
  --from-run /path/to/original/run.json \
  --observation /path/to/original/observations/record.json \
  --reviewer "Actual reviewing observer" \
  --reason "Explain why the unchanged dependencies still support this claim"
```

In an installed skill, the helper is under `scripts/`. See `--help` for options.

Reuse requires the same declared scenario, engine version/build and project
profile, successful required checks, unchanged claim dependencies, and intact
original records, captures and variant sources. Unresolved failures/errors in
sibling observations or originating attempt history block reuse. A passing record
cannot remove a failure by being copied to another run. Original failures keep
the existing diagnosis/resolution contract; this command creates no waiver.

A helper identity change also blocks reuse by default. After reviewing the helper
change against the observed contract and completing current checks/calibration,
`--allow-helper-change` records that explicit reviewer decision. It does not allow
an engine, profile, dependency or scenario change, and supplies no missing evidence.

The new record preserves the original observer, method, inputs, expected/actual
outcome, captures and acquisition time. It records the reviewer/reason, exact
changed-file inventory, current candidate identity and hashes of its immediate
original run/observation. Transitive references remain intact. Legacy records use
full-source scope and retain their original recording timestamp with the explicit
`legacy_recording_time` basis; no earlier acquisition time is invented.

`summarize` validates the linked records and reports acquired and reused record
counts separately. Later changes to an original record, capture, variant or
originating failure history block closure. Keep these live references until an
[historical evidence archive](evidence-archives.md) has been verified. An archive
preserves historical integrity; it does not turn old observations into current
acceptance.
