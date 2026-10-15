# Start using the toolkit in a game

Find the actual `project.godot` root and read existing instructions, tests and pins.
Do not manufacture a game in a research-only folder. Run the bundled helper's
`inspect` command with the chosen engine executable to discover actual capabilities.

Use `init-project` to preview the project profile and short AGENTS pointer, then
`--apply` to create them when adopting. Existing profiles/instructions are preserved;
merge an existing profile deliberately. Record the exact engine version, existing
test framework/command, representative scenes and adopted rules. Keep executable
paths in `--godot` or `GODOT_BIN`, rather than a shared machine-specific path.

Start with import/parse and representative behavior cases. New candidate rules
are advisory. Keep the game's existing acceptance requirements. A deliberate
engine upgrade is a separate change; research's newer documentation does not
authorize upgrading a game.

Personal skills are installed once through the Skills repo. Games own their
profiles and conventions. This draft does not install a second copy of the skills
into each game, configure hooks/agents or supply a release pipeline.

Godot 4/GDScript is the implementation target. For 3D, networking, mobile, XR or
addons, add representative scenarios and the required tool/target evidence.
Passing the small 2D fixture certifies only the mechanisms it actually exercises.
