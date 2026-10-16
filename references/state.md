# State and lifetime decisions

Resource identity and value equality answer different questions. Declare immutable
shared definitions, instance-owned mutable state and intentional aliases. Test two
independently instantiated scenes plus nested Resources/containers. `duplicate`
and local-to-scene behavior depend on the engine pin and nested data; establish the
actual graph instead of assuming a blanket deep copy is correct.

Choose a Resource for authored/serialized data, RefCounted for lightweight owned
logic/data, and Node when tree lifecycle/process/input responsibilities are needed.
Keep state near its owner. Autoloads suit actual cross-scene services/state; an
autoload is not the automatic home for every mutable value.

Declare initialization order and reentry behavior. `_ready` normally runs once
per node, and requesting readiness on a parent does not automatically rearm every
child. Connect once at the intended lifetime and disconnect/cancel according to
the source/receiver/work owner. Queued deletion is deferred: observe cleanup after
it settles rather than reporting an immediate orphan as a leak.

Timers, tweens, awaits and callbacks need an owner, pause behavior, cancellation
or a stale-completion guard when their scene is removed/restarted. Exercise repeated
cycles, not just the first happy path. Simple enum state is often adequate; add
state abstractions for concrete transition/ownership complexity.

For actor hit response, trace both surviving and fatal branches before early
returns or processing disablement. A per-actor flash uniform, reaction motion and
emitter can share that actor's reset/pause boundary while shader definitions stay
immutable and shared. Check independent actors, once-only defeat, response
completion and affected pause/reset. Flash, recoil, particles and hit-stop are
optional design choices; a shared service needs a concrete cross-actor lifetime.

Consult selected SH-04/SH-10/SH-14 and physics/navigation/input topics in
[the index](topics/index.md), then the exact engine's official class documentation.
Security-sensitive SH-09/SH-11/SH-12 work also follows [discovery](discovery.md).
