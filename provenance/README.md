# Research provenance

The separate `godot-research` project retains the research packs and reviewed
proposal. This toolkit distills their findings; it is the authoritative home for
the reusable implementation. Game policy remains authoritative within each game.

`manifest.json` records the original relative paths, research date and SHA-256
fingerprints. `feature-sources.json` and `rule-sources.json` retain the source
registries and limitations. Topic briefs link primary sources directly. All 50
rule treatments preserve original exceptions and distinguish checks, observations,
judgment and advice. Source strength labels do not adopt a policy for a game.

To deliberately refresh the derived topic/rule references, run:

```sh
python3 tools/import_research.py /path/to/godot-research
```

Review the resulting diff and affected calibration. This rewrites derived
references, not the research project. Edit other workflow/skill guidance here.
The installed packages contain their references and helper; they never need the
research checkout at runtime. Generated copies in the Skills repo are outputs.

`topic-refinements.json` owns maintained post-research additions and the preserved
physical-input clarification. The importer applies these to the original topic
data; edit that file and regenerate instead of editing generated topic prose.
The pilot-three refinements distinguish missing examples from already applicable
principles. Composite footprints, active-strike negatives and temporal traces are
selected examples; game-specific art, generosity and feedback exceptions remain.

Implementation calibration corrected one proposed assumption: on the installed
4.7.1 macOS editor binary, self-contained editor mode does not redirect runtime
`user://`. The implemented adapter uses an exclusively created unique user-data
link into its run and confirms its resolved path with a clean pre-scenario probe.
The copied application bundle preserves the executable's macOS launch context.
The source app and existing player data remain untouched.

Primary cross-checks:

- [OS user-data resolution](https://github.com/godotengine/godot/blob/4.7-stable/core/os/os.cpp)
- [Unix user-data path join](https://github.com/godotengine/godot/blob/4.7-stable/drivers/unix/os_unix.cpp)
- [macOS data path](https://github.com/godotengine/godot/blob/4.7-stable/platform/macos/os_macos.mm)
- [Self-contained editor paths](https://github.com/godotengine/godot/blob/4.7-stable/editor/file_system/editor_paths.cpp)
- [GUT 9.7.1](https://github.com/bitwes/Gut/releases/tag/v9.7.1), locked by commit in the fixture dependency file

The source cross-checks explain mechanisms; the exact local binary and adapter
are established by the fixture's actual probe/logs and calibration results.
