# Acquire editor and visible-play observations

Use a current checking run and its identified isolated sources. Read the run's
`isolation` record for the copied application, source directory and owned user-data
mapping. Keep the original candidate intact. Required observations are declared by
the task/profile; [verification](verification.md) owns their result semantics.

## Demonstrated macOS path

The Godot 4.7.1 fixture demonstrated launching the copied application through the
macOS application launcher, then binding the native-control tool to that exact
application path. Several copies share Godot's bundle identifier, so a bundle ID
alone can be ambiguous.

```sh
open -n /absolute/path/to/copied/Godot.app --args --editor --path /absolute/path/to/isolated/project res://enemy.tscn
open -n /absolute/path/to/copied/Godot.app --args --path /absolute/path/to/isolated/project --scene res://main.tscn
```

When the editor exposes only native menus to an accessibility controller, the
copied editor's `interface/accessibility/accessibility_support = 1` setting enables
Always Active support. On the calibrated pin, the editor setting overrode the
`--accessibility always` startup flag. Change only the disposable copied editor's
`editor_data/editor_settings-*.tres` while it is closed, then reopen. This supplies
named Inspector properties and settable controls without changing personal editor
or OS settings. Record the setting and actual control method with the observation.

Other hosts/controllers need their own demonstrated acquisition path or a named
human observer. A tool listing alone establishes no observation capability.

## Acquire the selected cases

- **Reopen:** save through the editor, close it, open a fresh editor process and
  inspect the intended scene's descendants, assignments and nominated exports.
  Capture the actual reopened state, not just a successful import.
- **Tuning effect:** prepare a separate controlled source variant with its own
  established isolation. Change the nominated value through normal Inspector
  controls, save, close/reopen and confirm persistence. Run that same variant and
  compare the expected gameplay effect with the baseline. Preserve source hashes,
  the exact saved diff and the actual UI value. A native accessibility value is
  Inspector evidence when clearly identified as such.
- **Visible play:** launch the identified scene as a game, perform real inputs and
  reconcile expected/observed states. For the fixture: baseline left/right health
  is three; one left hit changes only left; Pause/Resume adds no hit; the next
  explicit hit works. A separate left-health-five variant survives four hits and
  defeats on the fifth while right remains three.

Confirm each capture actually depicts the intended scene/state before attaching
it. Save accessibility text when it establishes a property more accurately than
pixels. Interaction claims need the actual sequence and intermediate outcomes;
audio, timing and feel need their corresponding observation.

Use the helper's `observe` command to record the actual named observer, method,
sequence, expected/actual outcomes, captures and controlled variant/transformation.
Run `summarize` against the unchanged candidate after all required evidence is
recorded. Close only the task-created application processes, then `cleanup-run`
removes the owned user-data links while preserving logs, captures and source copies.

The implementation's [Godot editor setting documentation](https://docs.godotengine.org/en/latest/classes/class_editorsettings.html#class-editorsettings-property-interface-accessibility-accessibility-support)
explains Always Active support. The source is a rolling version; the exact local
setting, Inspector interaction and runtime effect were also exercised on the pinned
4.7.1 fixture. These observations establish the shared 2D mechanism, not target or
3D certification.
