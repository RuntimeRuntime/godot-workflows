# Verify UI interaction and presentation contracts

Read the applicable branch for changed pointer gestures, UI previews of computed
gameplay values, or disagreement between automated input and visible play.

## Pointer gestures

A call to a merge/drop handler, a valid drag dictionary, a button's `pressed`
signal, or `force_drag()` proves a narrower contract than the player's gesture.
Keep those checks when useful and pair them with the actual event path when
gesture behavior is in scope.

For native Control drag/drop, exercise the saved scene with mouse position,
left-button press, motion with the held-button mask and nonzero relative movement
beyond the drag threshold, then release at the destination. Use the intended
Viewport's event path, allow frames for layout/event delivery, assert that the
native drag starts, and assert the actual resulting state. Release injected
buttons and restore input/focus after the scenario, including failed attempts.
Include a rejected/cancelled drop when the change affects validation or cleanup.

Keep nominated real-device/window observation separate. Engine-injected events
establish engine routing; they do not establish OS delivery or native-control
tool behavior. A click alternative can be useful but does not cover a required
drag gesture. Record the observer and exact interaction through
[verification](verification.md).

## Preview and gameplay agreement

When UI advertises computed stats, cost, health or outcomes, select a meaningful
case where live values differ from authored defaults: an upgrade, enemy scaling,
discount, damage or reset. Establish an expected result from the requirement;
verify that the displayed value and the value actually used by the game agree.
Check the relevant maximum/current values together when a health bar or similar
ratio is involved. Re-reading the same incorrect label is not an independent
oracle.

Prefer presentation consuming the authoritative live value or shared calculation
instead of duplicating policy constants and formulas. Separate saved-editor
placeholders from the runtime claim. A correct default preview does not establish
the overridden case. Keep the check proportional to the changed contract rather
than adding a test for every unchanged label.

## Tool input versus game behavior

If visible automation disagrees with the engine-event test, inspect the delivered
events/state in a controlled diagnostic copy before changing gameplay. Record the
event fields and expected protocol, exact transformation, source identity and
which route succeeded. Malformed tool input is an acquisition limitation, not by
itself proof that gameplay is broken. Do not add a game workaround solely to make
the tool's invalid gesture succeed.

Retain the failed attempt and supported diagnosis through
[diagnosis](diagnose.md). A passing injected test does not close a required
real-device observation; acquire valid input or a named human observation, or
leave the corresponding evidence blocked. A screenshot taken during later play
must be labeled with that actual state, not as the instant of an earlier gesture.

## Basis and limits

The shape auto-battler pilot exposed both mismatched enemy previews and a drop
test that bypassed native drag initiation. Its native automation supplied zero
relative motion and no held-button mask; valid engine events passed, and a human
subsequently confirmed the actual drag. These are bounded host observations, not
a claim about every control tool or device.

Native mechanisms: [Control drag/drop](https://docs.godotengine.org/en/4.7/classes/class_control.html),
[Viewport input delivery](https://docs.godotengine.org/en/4.7/classes/class_viewport.html#class-viewport-method-push-input),
[mouse motion fields](https://docs.godotengine.org/en/4.7/classes/class_inputeventmousemotion.html),
and [Godot's drag implementation](https://github.com/godotengine/godot/blob/4.7/scene/main/viewport.cpp).
Use the game's engine pin; these checks do not replace target-device evidence.
