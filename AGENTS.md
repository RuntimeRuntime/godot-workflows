# Godot workflow toolkit

Reusable authoring sources live here. Generated skill packages and the copies in
the personal Skills repo are outputs; edit the sources and regenerate them.

For skill or instruction changes, use skill-creator and writing-for-agents.
Read `references/verification.md` before changing result semantics or execution.
Read `provenance/README.md` before refreshing research-derived guidance.

Run `python3 -m unittest discover -s tests` for helper changes. Run the actual
fixture calibration for engine/test adapters; mocked processes alone cannot
establish compatibility. Use `python3 tools/package_skills.py build` to check
package links and create standalone skills.

The fixture is a disposable calibration project. Preserve known failures and
valid exceptions. Record editor/play observations separately from headless tests.
Keep new policy advisory until a game explicitly adopts it.
