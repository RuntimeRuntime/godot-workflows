# Portable historical evidence

Before cleaning temporary runs or handing evidence to another machine, use the
helper's `archive --run <run.json> --output <new-directory>` command. Select a new
directory outside the game and its run directories. Check the bundle with
`verify-archive --archive <directory>` after copying or moving it.

The bundle retains the complete previous-run chain and any observation acquisition
chains, including acquisitions outside that rerun history. Original run and
observation JSON bytes, commands, timestamps and recorded source/tool identities
remain unchanged. The portable index maps their original path identifiers to
content-addressed files inside the bundle. It retains referenced process logs,
JUnit reports and captures, plus supplemental run logs, captures and isolation
probe files. Engine/application copies, caches and runtime user data are omitted.

Source snapshots are retained only when an available tree exactly matches its
recorded manifest or digest. A newer tree never stands in for historical source.
When the old tree is gone or changed, the bundle preserves the recorded manifest
or digest and reports the snapshot as unavailable. A legacy observation that has
only a variant digest can gain a full snapshot when the available variant still
matches that digest. New observations record the full variant manifest directly.
If old external task bytes changed or disappeared, the embedded historical task
and original raw task hash remain, and the unavailable raw bytes are reported.
Archive promptly when exact source reconstruction matters; a later bundle cannot
recover bytes that were never retained.

Missing or changed required logs, reports, captures, acquisition records and run
history reject creation. Symlinks, traversal paths and cyclic histories reject
creation or verification. Output must be a new directory; a failed creation
removes only that newly created bundle. Records are copied as data: neither
command strings nor original engine/project paths are executed during archival.

`verify-archive` reads only the bundle. It checks retained content hashes, portable
references, source inventories and history links after the original roots are
removed or the bundle moves. Its `historical_integrity: verified` result establishes
that the retained evidence is internally intact. `current_project_acceptance`
stays false, even when the old run passed. It does not refresh observations,
re-evaluate recorded outcomes under a newer classifier, establish observer
credibility, or establish that a current project matches the old candidate.
Use current checks and `summarize` for current acceptance.

The manifest and its hashes provide corruption detection, not a signature or an
independent authenticity guarantee. Keep a trusted copy or external digest when
the origin of a bundle needs to be established. Review unavailable source/raw-task
entries alongside the historical records when deciding whether the bundle is
sufficient for a handoff.
