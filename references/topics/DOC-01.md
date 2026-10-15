# DOC-01 — Discover unfamiliar native features before designing replacements

When: A requested capability is unfamiliar, absent from this catalogue, or about to become a substantial custom subsystem.

Native candidates: `Official tutorial index`, `Official class reference`, `Official feature inventory`.

## Approach

Use topic indexes to discover candidate facilities, then read the matching versioned tutorial and actual class/resource references. Record the selected native option or concrete reason for a custom approach.

A finite local checklist becoming the boundary of what an agent believes Godot can do.

## Pitfalls

- Index presence does not establish API semantics or platform support.
- A versioned page can contain stale wording or a WIP warning.
- The catalogue is a discovery aid; an absent topic is not evidence that Godot lacks support.

## Verify

- A natural-language task reaches a relevant official topic even without class names.
- An intentionally unlisted task invokes the official-lookup fallback.
- A stale/WIP page keeps an explicit uncertainty and requests pin-specific confirmation.

## Version and limits

4.7 indexes inspected; feature list includes historical web/import wording. Use it only for breadth discovery; dedicated current topic/class docs own detailed claims.

## Primary sources


- [FD01: Tutorials topic index](https://docs.godotengine.org/en/4.7/tutorials/index.html). Scope/limits: Topic inventory only; not a source for detailed feature semantics.

- [FD02: All classes](https://docs.godotengine.org/en/4.7/classes/index.html). Scope/limits: Class-name/relationship discovery only; individual API behavior requires class pages.

- [FD03: List of features](https://docs.godotengine.org/en/4.7/about/list_of_features.html). Scope/limits: Breadth inventory; historical web/export/import wording observed. Do not use as current platform certification.
