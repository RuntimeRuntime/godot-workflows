# Discover native capabilities and research boundaries

Start with the task trigger in [the topic index](topics/index.md), then read the
matching brief. The catalogue is finite and is not a feature checklist. Consult
the project's engine-version tutorial and class pages before relying on exact API
behavior. WIP, stale, platform-specific and deprecated guidance retains its limits;
use a class/source cross-check or a pin-specific experiment where necessary.

For unmatched or unfamiliar capabilities, use the version-matched equivalents of
the [tutorial index](https://docs.godotengine.org/en/4.7/tutorials/index.html),
[class index](https://docs.godotengine.org/en/4.7/classes/index.html) and
[feature inventory](https://docs.godotengine.org/en/4.7/about/list_of_features.html).
Find the relevant primary topic/class sources. Record candidate, chosen approach,
concrete reason and uncertainty. Missing catalogue coverage does not imply missing
engine support. An adequate existing project solution may be retained.

## Conditional research boundary

Untrusted mods, downloads or user-provided runtime files require threat-specific
follow-up before claiming safe loading/deserialization. Record the trust boundary,
allowed formats/operations, authoritative follow-up and unresolved evidence.
Security-sensitive RPCs, replication or HTTP services require protocol/authority,
authentication and service-specific follow-up. Native API selection alone proves
none of these properties. Apply this branch to matched SH-09/SH-11/SH-12 tasks too.
Ordinary trusted project-authored assets do not automatically require this branch.

C#/GDExtension, XR comfort/device profiles, server/compute simulations, specialist
physics, consoles and third-party addons have discovery-level coverage here.
Use their primary integration/target documentation and representative experiments
before behavior or platform claims. The original survey limitations are retained
in `coverage-limitations.json` beside this document.
