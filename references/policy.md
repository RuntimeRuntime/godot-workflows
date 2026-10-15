# Candidate Godot policy

All 50 research treatments are preserved. They are advisory until a game explicitly adopts a named requirement. Research strength labels are not installed policy.

## G01 — Save fixed game objects and UI hierarchy as native scenes.

Treatment: `specialist_judgment`. Fixed versus procedural intent needs saved-scene inspection; a .tscn or Node.new search cannot settle it.

Exception: Procedural or transient content can be constructed at runtime.

Evidence: GT05.reopen, GT05.inspectability. Sources: [pack:O02](https://docs.godotengine.org/en/stable/tutorials/best_practices/scenes_versus_scripts.html), [pack:P01](https://docs.godotengine.org/en/stable/tutorials/ui/gui_containers.html), [workflow:GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## G02 — Spawn authored PackedScenes for repeated gameplay objects.

Treatment: `specialist_judgment`. Repeated gameplay authoring should be inspected; trivial native helpers are legitimate without PackedScene.

Exception: Plain native nodes suffice for trivial helpers.

Evidence: GT05.inspectability, GT04.contracts. Sources: [pack:O18](https://docs.godotengine.org/en/stable/getting_started/step_by_step/instancing.html), [pack:O13](https://docs.godotengine.org/en/stable/classes/class_packedscene.html), [workflow:GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## G03 — Code-generated authoring output must survive editor reopen.

Treatment: `runtime_editor_evidence`. Compare intended generated descendants and properties after actual save and fresh reopen.

Exception: Runtime instances need no authoring persistence.

Evidence: GT05.reopen. Sources: [pack:O14](https://docs.godotengine.org/en/stable/tutorials/plugins/running_code_in_the_editor.html), [pack:O13](https://docs.godotengine.org/en/stable/classes/class_packedscene.html), [workflow:GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## G04 — Distinguish node parentage, scene ownership and saving.

Treatment: `runtime_editor_evidence`. Engine-loaded ownership and reopened composition distinguish parentage from persistence and nested boundaries.

Exception: Do not change ownership indiscriminately in instances.

Evidence: GT05.reopen, GT03.scene_scripts. Sources: [pack:O12](https://docs.godotengine.org/en/stable/classes/class_node.html), [pack:O13](https://docs.godotengine.org/en/stable/classes/class_packedscene.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html), [workflow:GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## G05 — Use existing native nodes before designing custom replacements.

Treatment: `advisory_guidance`. Native alternatives inform design; specialized requirements can justify a replacement without violating a syntactic rule.

Exception: Specialized gameplay may justify custom behavior.

Evidence: GT05.inspectability. Sources: [pack:A05](https://kidscancode.org/godot_recipes/4.x/games/first_2d/first_2d_02/index.html), [pack:O04](https://docs.godotengine.org/en/stable/tutorials/best_practices/node_alternatives.html).

## G06 — Give reusable scenes one coherent responsibility and a usable harness.

Treatment: `runtime_editor_evidence`. Harness exercises real dependency boundaries; coherence remains a design assessment rather than a passing fixture alone.

Exception: A harness can supply intentional external dependencies.

Evidence: GT04.contracts, GT05.inspectability. Sources: [pack:O01](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html), [pack:A01](https://kidscancode.org/godot_recipes/4.x/basics/node_communication), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html), [workflow:GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## G07 — Prefer explicit typed references over cross-scene path traversal.

Treatment: `runtime_editor_evidence`. Native typing and relocation/reparent fixtures expose some failures; scope and deliberate internal paths need review.

Exception: Short internal paths remain useful.

Evidence: GT03.parse, GT04.contracts. Sources: [pack:O10](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_exports.html), [pack:A01](https://kidscancode.org/godot_recipes/4.x/basics/node_communication), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html), [workflow:GD13](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/warning_system.html).

## G08 — Use unique node names within their documented scene scope.

Treatment: `runtime_editor_evidence`. Resolve names in actual nested instances and owner scopes; textual unique-name presence is insufficient.

Exception: Explicitly enter a nested scene before accessing its unique names.

Evidence: GT04.contracts, GT05.reopen. Sources: [pack:O07](https://docs.godotengine.org/en/stable/tutorials/scripting/scene_unique_nodes.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G09 — Expose reusable contracts through methods and semantic signals.

Treatment: `specialist_judgment`. Trace consumer meaning and public boundaries; small direct references can be the clearest contract.

Exception: A small local direct reference can be clearer.

Evidence: GT04.contracts, GT05.inspectability. Sources: [pack:O11](https://docs.godotengine.org/en/stable/getting_started/step_by_step/signals.html), [pack:A03](https://www.gdquest.com/library/signals_good_practices).

## G10 — Let a common ancestor wire sibling scenes.

Treatment: `specialist_judgment`. Assess wiring direction and reuse consequences against actual dependencies, allowing documented scoped providers.

Exception: A documented scoped provider can replace mediation.

Evidence: GT05.inspectability, GT04.contracts. Sources: [pack:O01](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html), [pack:A01](https://kidscancode.org/godot_recipes/4.x/basics/node_communication).

## G11 — Keep fixed signal wiring traceable in scenes or one setup function.

Treatment: `runtime_editor_evidence`. Inspect serialized/setup wiring and exercise duplicate or missing reactions across dynamic-instance lifetime.

Exception: Connect dynamic instances in code.

Evidence: GT05.reopen, GT04.lifecycle. Sources: [pack:O11](https://docs.godotengine.org/en/stable/getting_started/step_by_step/signals.html), [pack:A03](https://www.gdquest.com/library/signals_good_practices), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G12 — Introduce a global event bus only for justified distant events.

Treatment: `specialist_judgment`. Review distant event purpose, publishers, listeners and lifetime; bus existence/count cannot establish need.

Exception: Prefer local events for scene-local behavior.

Evidence: GT04.lifecycle. Sources: [pack:A10](https://www.gdquest.com/tutorial/godot/design-patterns/event-bus-singleton), [pack:C04](https://forum.godotengine.org/t/autoload-signal-bus-vs-in-scene-signal-connections/111185), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G13 — Restrict autoloads to narrow systems needing application lifetime.

Treatment: `specialist_judgment`. Review application lifetime and owned global state; a narrow justified service is valid.

Exception: A justified session or dialogue service is acceptable.

Evidence: GT04.lifecycle. Sources: [pack:O06](https://docs.godotengine.org/en/stable/tutorials/best_practices/autoloads_versus_regular_nodes.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G14 — Use groups for tags and collective operations.

Treatment: `runtime_editor_evidence`. Empty/multiple group fixtures test timing and cardinality; suitability for a required singleton remains judgment.

Exception: Required single dependencies should be explicit.

Evidence: GT04.contracts. Sources: [pack:O15](https://docs.godotengine.org/en/stable/tutorials/scripting/groups.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G15 — Expose tunable gameplay data as typed exports or custom Resources.

Treatment: `runtime_editor_evidence`. Inspect and change nominated tuning through normal Inspector use, save/reopen and verify its expected runtime effect in a recorded scratch variant; intended tunability remains a domain judgment.

Exception: Keep implementation details private by convention.

Evidence: GT05.inspectability, GT03.parse, GT05.tuning_effect. Sources: [pack:O10](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_exports.html), [pack:O05](https://docs.godotengine.org/en/stable/tutorials/scripting/resources.html), [workflow:GD11](https://docs.godotengine.org/en/stable/classes/class_resource.html).

## G16 — Declare whether mutable resource state is shared or per instance.

Treatment: `runtime_editor_evidence`. Two-instance mutation and identity observations establish declared isolation or deliberate immutable sharing for selected resources.

Exception: Shared definitions are useful when intentionally immutable.

Evidence: GT04.resource_isolation, GT05.inspectability. Sources: [pack:P09](https://docs.godotengine.org/en/stable/classes/class_resource.html), [pack:O05](https://docs.godotengine.org/en/stable/tutorials/scripting/resources.html), [workflow:GD11](https://docs.godotengine.org/en/stable/classes/class_resource.html).

## G17 — Verify nested resource duplication on the project engine version.

Treatment: `runtime_editor_evidence`. Nested container/subresource fixtures must match the actual engine and explicitly intended sharing.

Exception: Sharing large immutable subresources is acceptable.

Evidence: GT04.resource_isolation, GT00.versions. Sources: [pack:P09](https://docs.godotengine.org/en/stable/classes/class_resource.html), [workflow:GD11](https://docs.godotengine.org/en/stable/classes/class_resource.html).

## G18 — Separate content definitions from temporary actor and UI state.

Treatment: `specialist_judgment`. Trace definition versus live-state lifetime; two actors supply evidence but a prototype may use simpler data.

Exception: Small prototypes can start with simpler data.

Evidence: GT04.resource_isolation, GT04.contracts. Sources: [pack:video-02](https://www.youtube.com/watch?v=4vAkTHeoORk), [pack:R2-07](https://github.com/gdquest-demos/godot-4-procedural-generation/tree/master/godot4), [workflow:GD11](https://docs.godotengine.org/en/stable/classes/class_resource.html).

## G19 — Use static types for public APIs and stable gameplay data.

Treatment: `runtime_editor_evidence`. Native parsing checks validity and script inventory checks file scope; separate judgment reviews affected public declarations, stable gameplay data and justified Variant/dynamic boundaries under adopted policy.

Exception: Use Variant deliberately for genuinely dynamic interfaces.

Evidence: GT03.parse, GT03.inventory, GT03.public_types. Sources: [pack:O08](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/static_typing.html), [workflow:GD13](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/warning_system.html).

## G20 — Follow one GDScript style convention and formatter configuration.

Treatment: `deterministic_check`. Pinned selected-file formatting and configured style are decidable after suppressions/exceptions are explicit.

Exception: Record justified deviations instead of alternating styles.

Evidence: GT01.format, GT01.lint. Sources: [pack:O09](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html), [pack:T03](https://github.com/Scony/godot-gdscript-toolkit), [workflow:GD04](https://pypi.org/project/gdtoolkit/), [workflow:GD05](https://github.com/Scony/godot-gdscript-toolkit/wiki/3.-Linter).

## G21 — Keep scripts cohesive; extract behavior after a concrete need appears.

Treatment: `specialist_judgment`. Concrete change cost and responsibility matter; line/method metrics can reward harmful fragmentation.

Exception: No universal line limit or mandatory component count.

Evidence: GT04.adequacy, GT05.inspectability. Sources: [pack:VTXT02](https://www.gdquest.com/library/design_patterns_intro), [pack:C11](https://retroactive.me/devlog/tactics/postmortem), [workflow:GD05](https://github.com/Scony/godot-gdscript-toolkit/wiki/3.-Linter), [workflow:AW16](research-recommendations.md#aw16).

## G22 — Prefer composition for independent capabilities; use shallow meaningful inheritance.

Treatment: `specialist_judgment`. Assess capability changes and overrides; stable inherited variants are valid and no universal depth applies.

Exception: Inherited scenes can represent real stable variants.

Evidence: GT04.contracts, GT05.inspectability. Sources: [pack:A09](https://www.gdquest.com/library/pattern_entity_component), [pack:C12](https://www.reddit.com/r/godot/comments/13irfdo/inheritance_vs_composition_best_practices).

## G23 — Start simple state behavior with an enum; split states when complexity warrants it.

Treatment: `specialist_judgment`. Transition assertions reveal behavior errors; enum versus state objects/nodes remains an appropriate-complexity decision.

Exception: Node or object state implementations are valid alternatives.

Evidence: GT04.contracts. Sources: [pack:A02](https://www.gdquest.com/library/pattern_finite_state_machine), [pack:R2-01](https://github.com/godotengine/godot-demo-projects/tree/master/2d/finite_state_machine).

## G24 — Initialize dependencies according to enter-tree and ready ordering.

Treatment: `runtime_editor_evidence`. Exercise standalone, spawn and reentry order with explicit setup/deferred alternatives; callback text order is inadequate.

Exception: Use explicit setup or deferred initialization when needed.

Evidence: GT04.lifecycle. Sources: [pack:A07](https://kidscancode.org/godot_recipes/4.x/basics/tree_ready_order), [pack:O12](https://docs.godotengine.org/en/stable/classes/class_node.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G25 — Manage teardown for spawned nodes, subscriptions and delayed actions.

Treatment: `runtime_editor_evidence`. Repeat death/reload/restart, await settled cleanup and verify owners, late actions and duplicate reactions.

Exception: Retained session state must have an explicit owner.

Evidence: GT04.lifecycle, GT08.lifetime. Sources: [pack:T02](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/debugger_panel.html), [pack:T07](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/the_profiler.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html), [workflow:GD08](https://github.com/godot-gdunit-labs/gdUnit4/releases/tag/v6.2.2).

## G26 — Surface missing component configuration through editor warnings.

Treatment: `runtime_editor_evidence`. Remove selected required configuration and observe refreshed feedback; runtime-only failures use runtime diagnostics.

Exception: Use runtime diagnostics for failures unavailable in the editor.

Evidence: GT05.feedback_recovery. Sources: [pack:O14](https://docs.godotengine.org/en/stable/tutorials/plugins/running_code_in_the_editor.html), [pack:O01](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G27 — Make authoring automation reversible and separate editor behavior from runtime.

Treatment: `runtime_editor_evidence`. Exercise intended editor and game behavior, reject unintended editor-only mutations during play, and verify independent undo/recovery then saved reopen; preserve reviewed disposable-conversion exceptions.

Exception: A disposable one-off conversion can use a reviewed script.

Evidence: GT05.feedback_recovery, GT05.reopen, GT05.editor_runtime. Sources: [pack:T09](https://docs.godotengine.org/en/stable/tutorials/plugins/editor/making_plugins.html), [pack:O14](https://docs.godotengine.org/en/stable/tutorials/plugins/running_code_in_the_editor.html), [workflow:GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## G28 — Use native Controls, Containers and anchors for authored interface layout.

Treatment: `runtime_editor_evidence`. Inspect native layout and real resize/long-text/focus behavior; specialized drawing remains valid.

Exception: Custom drawing can serve specialized visuals.

Evidence: GT05.inspectability, GT06.presentation. Sources: [pack:P01](https://docs.godotengine.org/en/stable/tutorials/ui/gui_containers.html), [pack:R2-03](https://github.com/godotengine/godot-demo-projects/tree/master/gui/control_gallery), [workflow:AW02](research-recommendations.md#aw02).

## G29 — Centralize repeated styling in Theme resources and variations.

Treatment: `specialist_judgment`. Review repeated styling and shared theme edits; local variation may be intentional.

Exception: Local overrides can express intentional exceptions.

Evidence: GT05.inspectability, GT06.presentation. Sources: [pack:P02](https://docs.godotengine.org/en/stable/tutorials/ui/gui_skinning.html).

## G30 — Use semantic InputMap actions and document their bindings.

Treatment: `runtime_editor_evidence`. Reconcile action references/settings and exercise intended devices; semantic names and bindings need review.

Exception: Raw events may be necessary for remapping or text entry.

Evidence: GT04.contracts, GT06.play. Sources: [pack:P03](https://docs.godotengine.org/en/stable/tutorials/inputs/inputevent.html).

## G31 — Respect GUI consumption and gameplay input routing.

Treatment: `runtime_editor_evidence`. Exercise focused/hovered UI with gameplay and continuous polling modes; callback choice alone proves no consumption.

Exception: Continuous polling requires separate mode or focus gating.

Evidence: GT04.contracts, GT06.play. Sources: [pack:P03](https://docs.godotengine.org/en/stable/tutorials/inputs/inputevent.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G32 — Use native body movement APIs with correct timestep handling.

Treatment: `runtime_editor_evidence`. Collision and varied-rate fixtures test selected movement expectations; a delta/movement call regex cannot verify units.

Exception: Direct transforms are appropriate for nonphysical visuals.

Evidence: GT04.contracts, GT06.play. Sources: [pack:P04](https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html), [pack:R2-09](https://github.com/godotrecipes/characterbody3d_examples), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G33 — Name collision layers and keep layer/mask intent explicit.

Treatment: `runtime_editor_evidence`. Named settings plus positive and negative contact fixtures check project-specific layer/mask intent.

Exception: Use project-specific categories rather than a universal schema.

Evidence: GT05.inspectability, GT04.contracts. Sources: [pack:P04](https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html).

## G34 — Author reusable animations in native resources with a deliberate reset pose.

Treatment: `runtime_editor_evidence`. Preview interrupt/reload sequences and reset state; native track presence does not prove intended pose.

Exception: Tweens fit runtime-dependent transitions.

Evidence: GT05.inspectability, GT06.presentation, GT04.contracts. Sources: [pack:P05](https://docs.godotengine.org/en/stable/tutorials/animation/introduction.html).

## G35 — Separate animation-state playback from gameplay-state responsibility.

Treatment: `specialist_judgment`. Review state authority and transition outcomes; cohesive small scripts may legitimately combine responsibilities.

Exception: Small scenes may keep both in one cohesive script.

Evidence: GT04.contracts, GT06.presentation. Sources: [pack:VTXT01](https://kidscancode.org/godot_recipes/4.x/animation/using_animation_sm/index.html), [pack:A02](https://www.gdquest.com/library/pattern_finite_state_machine).

## G36 — Declare pause behavior through process modes and event handling.

Treatment: `runtime_editor_evidence`. Pause/menu/resume scenarios exercise process modes and still-active signals under actual routing.

Exception: Signals can still run while processing is paused.

Evidence: GT04.contracts, GT06.play. Sources: [pack:P08](https://docs.godotengine.org/en/stable/tutorials/scripting/pausing_games.html), [workflow:GD10](https://docs.godotengine.org/en/stable/classes/class_node.html).

## G37 — Separate save data, user preferences and live scene objects.

Treatment: `runtime_editor_evidence`. Round-trip, missing and invalid save fixtures test selected persistence boundaries; layout alone is insufficient.

Exception: Tutorial schemas need game-specific extension.

Evidence: GT04.contracts. Sources: [pack:P06](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html).

## G38 — Version persistent data and define recovery from incompatible saves.

Treatment: `runtime_editor_evidence`. Older and corrupt data need explicit recovery assertions; a version field is not migration correctness.

Exception: Disposable prototypes may not need migrations.

Evidence: GT04.contracts. Sources: [pack:P06](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html).

## G39 — Organize around coherent features and colocate closely related assets.

Treatment: `advisory_guidance`. Feature location/removal and dependency traces inform organization; folder naming is no coherence predicate.

Exception: Existing consistent structure may be preferable.

Evidence: GT09.findings. Sources: [pack:O03](https://docs.godotengine.org/en/stable/tutorials/best_practices/project_organization.html), [pack:C08](https://forum.godotengine.org/t/are-there-project-architecture-style-guides-beyond-the-official-docs/128299).

## G40 — Commit native source, import settings and required UID sidecars; ignore caches.

Treatment: `runtime_editor_evidence`. Tracked source/import/UID inspection plus cold load exposes selected missing-reference and cache masking problems.

Exception: Follow the exact engine version ignore rules.

Evidence: GT02.cold, GT02.import. Sources: [pack:O17](https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html), [pack:U01](https://godotengine.org/article/uid-changes-coming-to-godot-4-4), [workflow:GD02](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html).

## G41 — Preserve identity when moving assets and keep scene diffs focused.

Treatment: `runtime_editor_evidence`. Compare moved identities and load affected consumers; focused diffs and legitimate resave normalization need judgment.

Exception: Editor resaves can legitimately normalize fields.

Evidence: GT02.cold, GT03.scene_scripts, GT05.reopen. Sources: [pack:U01](https://godotengine.org/article/uid-changes-coming-to-godot-4-4), [pack:T08](https://docs.godotengine.org/en/4.6/engine_details/file_formats/tscn.html), [workflow:GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## G42 — Document public scene contracts and important architecture decisions.

Treatment: `advisory_guidance`. A new reader must locate accurate entry/extension contracts; document presence cannot establish usability.

Exception: Avoid comments that merely repeat code.

Evidence: GT09.findings. Sources: [pack:O16](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_documentation_comments.html), [pack:A06](https://www.gdquest.com/library/modular_game_architecture), [workflow:AW08](research-recommendations.md#aw08).

## G43 — Pin engine, export templates and relevant addon/tool versions.

Treatment: `deterministic_check`. Compare actual binary, tools, addon pins and required templates with adopted declarations; suitability remains separate.

Exception: Upgrades use a deliberate compatibility review.

Evidence: GT00.versions. Sources: [pack:T01](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html), [pack:T04](https://github.com/bitwes/Gut), [pack:T05](https://github.com/godot-gdunit-labs/gdUnit4), [workflow:GD02](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html), [workflow:GD06](https://github.com/bitwes/Gut), [workflow:GD08](https://github.com/godot-gdunit-labs/gdUnit4/releases/tag/v6.2.2).

## G44 — Run import, parse and relevant runtime checks as different gates.

Treatment: `runtime_editor_evidence`. Separate completed scoped evidence is required; command names or successful startup are not a project audit.

Exception: A successful startup is not a whole-project audit.

Evidence: GT02.import, GT03.inventory, GT03.parse, GT04.results, GT09.integrity. Sources: [pack:T01](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html), [workflow:GD02](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html), [workflow:GD03](https://raw.githubusercontent.com/godotengine/godot/4.7.2-stable/main/main.cpp).

## G45 — Choose one test framework and test valuable behavior boundaries.

Treatment: `specialist_judgment`. Review external expectations, assertions and real boundaries; counts/framework choice cannot establish test value.

Exception: Avoid brittle tests of private implementation details.

Evidence: GT04.adequacy, GT04.results. Sources: [pack:T04](https://github.com/bitwes/Gut), [pack:T05](https://github.com/godot-gdunit-labs/gdUnit4), [pack:video-03](https://www.youtube.com/watch?v=CreugthdgJ0), [workflow:GD06](https://github.com/bitwes/Gut), [workflow:GD07](https://gut.readthedocs.io/en/v9.7.1/Command-Line.html), [workflow:GD08](https://github.com/godot-gdunit-labs/gdUnit4/releases/tag/v6.2.2), [workflow:GD09](https://github.com/godot-gdunit-labs/gdunit4/blob/master/documentation/doc/_advanced_testing/cmd.md), [workflow:AW03](research-recommendations.md#aw03).

## G46 — Inspect authored scenes and visibly exercise the changed gameplay.

Treatment: `runtime_editor_evidence`. Saved authoring and visible changed-loop evidence answer different questions; absent GUI observation remains a declared gap.

Exception: Headless-only environments must report the missing evidence.

Evidence: GT05.reopen, GT06.play, GT06.presentation. Sources: [pack:T02](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/debugger_panel.html), [workflow:AW02](research-recommendations.md#aw02).

## G47 — Measure representative performance and lifetime behavior before optimizing.

Treatment: `runtime_editor_evidence`. Representative comparisons and repeated settled cleanup support bounded claims, not universal performance numbers.

Exception: A tiny game may only need targeted monitoring.

Evidence: GT08.measure, GT08.lifetime, GT08.representative. Sources: [pack:T07](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/the_profiler.html), [pack:A08](https://www.gdquest.com/library/optimization_measure), [workflow:GD14](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/the_profiler.html), [workflow:AW15](research-recommendations.md#aw15).

## G48 — Verify exported builds and resource inclusion on intended targets.

Treatment: `runtime_editor_evidence`. Launch the hashed target artifact and exercise packaging/dynamic loads; editor success cannot substitute.

Exception: Editor execution cannot substitute for platform execution.

Evidence: GT07.artifact, GT07.target_launch. Sources: [pack:P07](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html), [workflow:GD15](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html).

## G49 — Attach source, version, exception and acceptance evidence to each adopted rule.

Treatment: `specialist_judgment`. Provenance fields are mechanically checkable; source relevance, exception validity and policy soundness need judgment.

Exception: Personal conventions must be labeled as such.

Evidence: GT09.integrity, GT09.findings. Sources: [pack:VTXT02](https://www.gdquest.com/library/design_patterns_intro), [pack:C06](https://forum.godotengine.org/t/organization-of-scene-code-is-there-a-better-way/57868), [workflow:AW05](research-recommendations.md#aw05), [workflow:AW08](research-recommendations.md#aw08).

## G50 — Review MCP and agent actions through actual files, editor state and logs.

Treatment: `runtime_editor_evidence`. Compare claimed automation success with saved files, fresh editor/runtime observations and appropriate logs; MCP remains optional.

Exception: Automation integrations are optional workflow tools.

Evidence: GT05.reopen, GT06.play, GT09.integrity. Sources: [pack:T13](https://github.com/Coding-Solo/godot-mcp), [pack:T14](https://github.com/tugcantopaloglu/godot-mcp), [pack:C01](https://www.reddit.com/r/godot/comments/1v2a6x7/claude_models_prefer_programmatical_nodes_over), [workflow:GD17](https://github.com/satelliteoflove/godot-mcp/blob/main/docs/tools/README.md).
