# Native Godot topic index

Match user intent, then open only relevant briefs. This is a discovery index, not a required feature checklist. Use [official discovery](../discovery.md) for gaps and research boundaries.

| Topic | User-visible trigger |
| --- | --- |
| [D2-01 — Grid worlds: TileSet, atlas and TileMapLayer](D2-01.md) | Author or change a fixed grid-based level, repeated tile world, isometric/hex map, or tile layer. |
| [D2-02 — Tile terrains, alternatives and per-tile properties](D2-02.md) | Need automatic terrain edges/corners, rotated or varied tile variants, tile-specific collision/navigation/occlusion, or authored gameplay metadata. |
| [D2-03 — PackedScene scene tiles for rich grid objects](D2-03.md) | Place repeated interactive objects, ambient sound emitters, particle effects or other node-rich objects at tile-aligned positions. |
| [D2-04 — 2D image import, filtering and pixel-art quality](D2-04.md) | Import or reuse 2D art, pixel art, sprite sheets, zoomed textures, or shared images also used in 3D. |
| [D2-05 — Sprite sheets and frame-based animation](D2-05.md) | Animate a 2D character/object from separate frame images or a sprite sheet. |
| [D2-06 — AnimationPlayer, AnimationTree and authored transitions](D2-06.md) | Coordinate multiple animated properties, blend clips, represent state transitions, or layer/interrupt animations. |
| [D2-07 — 2D cutout rigs and skeletal deformation](D2-07.md) | Animate a character built from articulated body pieces or deform a textured polygon around a 2D bone rig. |
| [D2-08 — Choose physics body and movement authority](D2-08.md) | Author a controllable character, simulated object, fixed obstacle, moving platform, door or projectile with collisions. |
| [D2-09 — Overlap sensors and collision filtering](D2-09.md) | Detect a player entering a pickup, hurtbox, trigger, proximity radius, gravity zone or other non-blocking region. |
| [D2-10 — RayCast2D, ShapeCast2D and direct physics queries](D2-10.md) | Need a line-of-sight, ground probe, aim hit, swept volume, instantaneous query or gameplay decision from collision geometry. |
| [D2-11 — Camera, coordinates, parallax and 2D draw ordering](D2-11.md) | Add camera following/limits/smoothing, convert pointer/world coordinates, scroll backgrounds, sort top-down overlap or compose layered 2D scenes. |
| [D2-12 — 2D lights, shadows and occlusion](D2-12.md) | Add real-time 2D light, ambient darkening, cast shadows, normal-map depth or tile/particle occlusion. |
| [D2-13 — 2D particle effects](D2-13.md) | Create sparks, smoke, rain, magic, debris, trails, ambient motion or other many-instance visual effects. |
| [D2-14 — 2D pathfinding: grid A* or navigation mesh](D2-14.md) | Implement NPC routes, tile-grid movement, continuous-area pathfinding, avoidance, navigation links or obstacles. |
| [D3-01 — Imported 3D scenes and reimport-safe composition](D3-01.md) | External 3D asset carries hierarchy, animation, skin, or multiple authored objects. |
| [D3-02 — Mesh resources and material ownership](D3-02.md) | A scene needs ordinary reusable visible 3D geometry or per-surface appearance. |
| [D3-03 — GridMap and MeshLibrary for 3D tile-based levels](D3-03.md) | Level pieces align to fixed-size cells and are drawn from a modular mesh set. |
| [D3-04 — MultiMesh for dense repeated geometry](D3-04.md) | Many nearby copies of one mesh are needed, such as foliage or repeated props. |
| [D3-05 — Physics body role and collision-shape composition](D3-05.md) | An object needs collision, overlap detection, physical influence, or physical motion. |
| [D3-06 — Ray, shape, and direct-space queries](D3-06.md) | Gameplay needs sensing, picking, ground probing, line of sight, or swept-volume detection. |
| [D3-07 — Code-driven character movement](D3-07.md) | A player or NPC has explicit game-authored movement and collision-response rules. |
| [D3-08 — Physics-simulated rigid objects](D3-08.md) | Forces, impacts, gravity, rotation and contact response should determine motion. |
| [D3-09 — Kinematic moving mechanisms and platforms](D3-09.md) | A platform, door, or collider is moved by code/animation and must affect bodies it touches. |
| [D3-10 — Camera3D and collision-aware third-person rig](D3-10.md) | A 3D viewport needs an active camera; third-person camera can be obstructed by world geometry. |
| [D3-11 — Imported skeletal animation and layered control](D3-11.md) | A character or object uses imported skeletal clips, blending, state transitions, IK, retargeting, or bone constraints. |
| [D3-12 — 3D navigation: path, actor motion, avoidance and links](D3-12.md) | Actors need routes across baked walkable surfaces, discrete point graphs, local avoidance, or special traversal connections. |
| [D3-13 — Lighting, Environment and renderer-aware GI](D3-13.md) | A scene needs an authored runtime sky/ambient environment, lights/shadows, post-processing, or indirect illumination. |
| [D3-14 — GPU and CPU particle effects](D3-14.md) | An authored visual effect needs many transient particles, emitter shapes, turbulence, collision, trails, or sub-emitters. |
| [D3-15 — 3D performance visibility: LOD, HLOD and occlusion](D3-15.md) | Profiling identifies rendering cost and scene layout has distance or occlusion opportunities. |
| [SH-01 — Responsive UI layout and theming](SH-01.md) | Authoring a menu, HUD, settings screen, inventory, dialog, or interactive overlay. |
| [SH-02 — UI focus and input routing](SH-02.md) | Keyboard/controller UI, modal/menu input, or custom Control input handling. |
| [SH-03 — InputMap actions, devices, and remapping](SH-03.md) | Adding controls, multiple input devices, per-player bindings, or runtime key remapping. |
| [SH-04 — Pause, process modes, time, timers, and tweens](SH-04.md) | Pause, cooldown, delay, time scaling, periodic work, or script-driven interpolation. |
| [SH-05 — Audio buses and positional playback](SH-05.md) | Music/SFX/UI mixing, category volume settings, spatial audio, or room effects. |
| [SH-06 — Localization pipeline](SH-06.md) | Player-facing text/assets must support locale changes or the task affects locale-sensitive UI. |
| [SH-07 — Accessibility-aware Control behavior](SH-07.md) | Accessibility requirements include screen reader, keyboard/controller use, scaling, or existing access settings. |
| [SH-08 — Preferences and progression persistence](SH-08.md) | Saving player settings/remaps or game progression across scenes/sessions. |
| [SH-09 — Project Resources versus external runtime files](SH-09.md) | Imported project assets, user-generated files, mods, downloads, or custom runtime-loaded media. |
| [SH-10 — Threaded resource loading and scene-tree safety](SH-10.md) | Measured load stalls, streamed content, or background scene/resource work. |
| [SH-11 — High-level multiplayer replication](SH-11.md) | Remote peers, gameplay RPCs, replicated properties, network-spawned scenes. |
| [SH-12 — HTTP services versus gameplay networking](SH-12.md) | Backend calls, HTTP downloads/uploads, or service APIs; multiplayer gameplay is handled separately. |
| [SH-13 — SubViewport render surfaces](SH-13.md) | Split-screen, minimaps, camera feeds, render-to-texture, or mixing 2D/3D/UI worlds. |
| [SH-14 — Autoloads and global services](SH-14.md) | State or service must survive scene changes and be available across unrelated scenes. |
| [SH-15 — Export presets and platform feature checks](SH-15.md) | Exporting, OS-specific APIs, non-resource assets, platform-specific input/audio/network/accessibility, or renderer/format constraints. |
| [DOC-01 — Discover unfamiliar native features before designing replacements](DOC-01.md) | A requested capability is unfamiliar, absent from this catalogue, or about to become a substantial custom subsystem. |
| [ED-01 — Editor extensions, Inspector integration and undo history](ED-01.md) | Repeated authoring operations or specialized editable content need a native editor workflow. |
| [ED-02 — Custom import and export pipeline hooks](ED-02.md) | An unsupported source format or target-specific resource transformation needs pipeline integration. |
| [ED-03 — Native runtime inspection and debugging aids](ED-03.md) | Collision, pathing, scene state or target behavior is unclear during diagnosis. |
| [ED-04 — Shader and material extension points](ED-04.md) | A visual effect exceeds native material or animation settings. |
| [XR-01 — XR discovery and device-specific adoption boundary](XR-01.md) | The game targets a headset or tracked controllers. |
| [MATH-01 — Native vectors, coordinate spaces and transforms](MATH-01.md) | Movement, aiming, camera, parenting or animation mixes directions, positions or rotations. |
