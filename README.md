# Godot workflows

A reusable first draft for Godot 4/GDScript work with Codex: three focused skills,
practical workflows, native-feature references, selective reviews and a runnable
validation fixture. New policy starts advisory.

## How to use it

With the three skills enabled through your personal Skills repo, start a chat in
the game you are working on. Ordinary requests can select the relevant skills;
you can also name them explicitly:

- `$godot-author-scenes`: create editable scenes, Resources, tuning and authoring tools.
- `$godot-state-lifecycle`: own mutable state, Resource sharing and delayed work.
- `$godot-verify-behavior`: test the actual scene path and collect editor/play evidence.

For example: “Add a reusable enemy with editable health, independent state for
each instance, and verify its saved scene and gameplay.” You do not need to load
this entire repo or remember the native node class names.

| Home | Owns |
| --- | --- |
| This toolkit | Reusable skill/workflow sources, references, templates, tools and fixture |
| Personal Skills repo | Generated copies and personal activation; edit toolkit sources here |
| Each game | Engine pin, commands, conventions, chosen requirements and representative scenarios |
| Original godot-research project | Evidence packs and reviewed proposal; no runtime dependency |

For a new game adoption, read [adoption](references/adopt.md). Preview the small
profile/instruction addition, then apply when appropriate:

```sh
python3 tools/godot_workflow.py inspect --project /path/to/game --godot /path/to/Godot
python3 tools/godot_workflow.py init-project --project /path/to/game
python3 tools/godot_workflow.py init-project --project /path/to/game --apply
```

In an installed skill, the same helper is under `scripts/`. The game-owned
`godot-workflow.json` selects checks, test cases, observations and adopted rules.
Record existing test commands there; a GdUnit4 project keeps its runner. Set the
machine executable with `--godot` or `GODOT_BIN`. Existing profiles and unrelated
instructions are preserved. Adoption requires a real `project.godot`.

## References to reach when needed

- [Change workflow](references/change.md), [diagnosis](references/diagnose.md), [feature planning](references/feature-planning.md).
- [Native topic index](references/topics/index.md): all 51 researched decision groups, with selective briefs and primary sources.
- [Candidate policy](references/policy.md): all 50 treatments and exceptions; each game decides what to adopt.
- [Selective review](references/review.md): authored scenes, state/lifetime, behavior/test adequacy and changed contracts.
- [Verification](references/verification.md): exact result meanings, observation ownership, isolation and limits.
- [Provenance](provenance/README.md): source records and the original research fingerprints.

## Run the fixture and helper tests

Python 3.9+ and the pinned Godot 4.7.1 binary are needed. The fixture's GUT addon is
an ignored cache checked against its locked commit and content digest; ordinary games receive no addon.

```sh
python3 tools/bootstrap_fixture.py
python3 -m unittest discover -s tests
python3 tools/godot_workflow.py check --project validation/fixture
python3 tools/calibrate_fixture.py
```

The fixture check deliberately requires editor reopen, Inspector tuning and
visible pause/input observations. Headless checks alone leave its summary blocked.
The calibration command declares a separate machine-only scope and tests valid
and deliberately broken copies through the real CLI. It retains logs/reports
and removes only its owned OS user-data links and copied applications afterward.

Use `observe --help` to record a named actual observation against a declared
scenario. Use `summarize --run /path/to/run.json` to check freshness and completeness.
After observations finish, `cleanup-run --run /path/to/run.json` removes the owned
user-data link and retains the run's evidence. Full result semantics are in
[verification](references/verification.md).

The macOS adapter copies the complete app and places a self-contained marker
beside it. Runtime user data uses a unique owned OS link into the run. Restricted
hosts need permission for that specific link; without access, the run is blocked.
This isolates known fixture state, not arbitrary untrusted code. Keep real mods or
security-sensitive services behind their topic-specific research boundary.

## Package and update personal skills

```sh
python3 tools/package_skills.py build --output /tmp/godot-skills-new
python3 tools/package_skills.py install --packages /tmp/godot-skills-new --skills-repo /path/to/Skills
python3 tools/package_skills.py install --packages /tmp/godot-skills-new --skills-repo /path/to/Skills --apply
```

Then run the three printed `npm run enable -- local/...` commands in the Skills
repo. Its existing manager handles global links and preserves other enabled skills.
Each package contains its references, templates and helper. A source manifest
detects modified generated copies; reconcile edits before replacing them.
Updates are rebuilt here and installed through the same preview/apply path.

## First-draft limits

The [validation record](validation/README.md) distinguishes checks actually run,
selection-only trials and completed editor/play observations. The baseline fixture is
2D; representative 3D, networking, device and target work needs game-specific
validation. Alternative test runners remain supported by the workflows, while the
bundled report adapter currently understands GUT. Public-type correctness, scope
selection and observer credibility remain judgments.

No hooks, persistent reviewer configuration, CI, export certification, performance
adapter, game-local skill installer or automatic waiver engine is included. An
owner's explicit risk acceptance retains failed evidence; it never supplies missing
required observations. Local reports are inspectable evidence, not an independent
enforcement or tamper-proof boundary. The repository is local; no GitHub remote is
created.
