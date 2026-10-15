"""Portable historical evidence bundles. No engine execution or current acceptance."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import time


FORMAT_VERSION = 1
MANIFEST = 'archive.json'
CLAIM = ('Historical bundle integrity only; current project acceptance, observation '
         'credibility and semantic correctness require separate assessment')
HEX = re.compile(r'^[0-9a-f]{64}$')


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _encoded(value):
    return _hash(json.dumps(value, sort_keys=True).encode())


def _absolute(value):
    """Validate a local path without resolving through symlinks."""
    path = Path(value).expanduser()
    if '..' in path.parts:
        raise ValueError('Path traversal is not permitted: ' + str(path))
    path = path.absolute()
    for component in reversed((path,) + tuple(path.parents)):
        if component.is_symlink():
            raise ValueError('Symlink is not permitted in evidence paths: ' + str(component))
    return path


def _read(path):
    path = _absolute(path)
    # Refuse special files and do not follow a replaced final symlink.
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Expected regular evidence file: ' + str(path))
    fd = os.open(str(path), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as stream:
        return stream.read()


def _json(path):
    value = json.loads(_read(path))
    if not isinstance(value, dict):
        raise ValueError('Expected JSON object: ' + str(path))
    return value


def _relative(value):
    if not isinstance(value, str) or '\\' in value:
        raise ValueError('Invalid portable reference')
    path = PurePosixPath(value)
    if not value or path.is_absolute() or '..' in path.parts or path.as_posix() != value or value == '.':
        raise ValueError('Invalid portable reference: ' + value)
    return path


def _manifest(value):
    if not isinstance(value, dict) or not isinstance(value.get('files'), dict):
        raise ValueError('Missing recorded source manifest')
    for name, sha in value['files'].items():
        _relative(name)
        if not isinstance(sha, str) or not HEX.fullmatch(sha):
            raise ValueError('Invalid recorded source hash: ' + name)
    if value.get('digest') != _encoded(value['files']):
        raise ValueError('Recorded source manifest digest differs from file inventory')
    return value


def _processes(record):
    for result in record['results'].values():
        yield from result.get('processes', [])
    if record.get('isolation', {}).get('process'):
        yield record['isolation']['process']


def _evidence(record):
    for process in _processes(record):
        yield process['log'], process['log_sha256']
    for result in record['results'].values():
        if 'report' in result:
            yield result['report'], result['report_sha256']


def _observation_evidence(record):
    for artifact in record.get('artifacts', []):
        yield artifact['path'], artifact['sha256']


def _validate_run(record):
    if record.get('format_version') != 1 or not isinstance(record.get('results'), dict) or not record['results']:
        raise ValueError('Missing/unsupported run record')
    if not record.get('run_id'):
        raise ValueError('Missing run identity')
    _manifest(record['source'])
    if record.get('variant_source'):
        _manifest(record['variant_source'])


def _validate_observation(record, run):
    if record.get('run_id') != run['run_id'] or record.get('source_digest') != run['source']['digest']:
        raise ValueError('Observation differs from its recorded run/source identity')
    if record.get('source_manifest') and record['source_manifest'] != run['source']:
        raise ValueError('Observation candidate manifest differs from run')
    if record.get('variant_source'):
        _manifest(record['variant_source'])
        if record['variant_source']['digest'] != record.get('variant_digest'):
            raise ValueError('Observation variant manifest differs from recorded digest')


class _Builder:
    def __init__(self, output, workflow):
        self.output = output
        self.workflow = workflow
        self.files = {}
        self.inputs = {}
        self.runs = {}
        self.observations = {}
        self.run_stack = set()
        self.observation_stack = set()

    def blob(self, path, expected=None):
        original = str(_absolute(path))
        data = _read(original)
        sha = _hash(data)
        if expected is not None and sha != expected:
            raise ValueError('Changed evidence file: ' + original)
        target = 'blobs/' + sha
        if target not in self.files:
            (self.output / target).write_bytes(data)
            self.files[target] = sha
        if original in self.inputs and self.inputs[original] != target:
            raise ValueError('Evidence changed during archival: ' + original)
        self.inputs[original] = target
        return target

    def snapshot(self, root, recorded=None, recorded_digest=None):
        if recorded is not None:
            _manifest(recorded)
            recorded_digest = recorded['digest']
        snapshot = {'original_root': str(root) if root else None,
                    'recorded_digest': recorded_digest, 'recorded_manifest': recorded,
                    'status': 'unavailable', 'files': {}}
        if not root:
            snapshot['reason'] = 'No source root recorded'
            return snapshot
        # A missing/changed source is a declared historical limitation, never an
        # invitation to substitute today's source for the recorded candidate.
        source = _absolute(root)
        if not source.is_dir():
            snapshot['reason'] = 'Historical source directory is unavailable'
            return snapshot
        # source_manifest hashes names itself. Reject special files first so a
        # stale historical tree containing a FIFO/device cannot block archival.
        for parent, dirs, names in os.walk(source, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in self.workflow.EXCLUDED)
            for name in dirs + sorted(names):
                if name in self.workflow.EXCLUDED:
                    continue
                path = _absolute(Path(parent) / name)
                mode = path.lstat().st_mode
                if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                    raise ValueError('Special source file is not permitted: ' + str(path))
        current = self.workflow.source_manifest(source)
        _manifest(current)
        if current['digest'] != recorded_digest or (recorded is not None and current['files'] != recorded['files']):
            snapshot['reason'] = 'Available source differs from recorded identity'
            return snapshot
        snapshot['recorded_manifest'] = recorded or current
        snapshot['status'] = 'retained'
        for name, sha in current['files'].items():
            snapshot['files'][name] = self.blob(source / name, sha)
        return snapshot

    def task(self, record):
        if not record.get('task_path'):
            return None
        value = {'original_path': record['task_path'], 'recorded_sha256': record['task_sha256'],
                 'status': 'unavailable', 'file': None}
        path = _absolute(record['task_path'])
        if path.is_file() and _hash(_read(path)) == record['task_sha256']:
            value.update(status='retained', file=self.blob(path, record['task_sha256']))
        else:
            if not isinstance(record.get('task'), dict):
                raise ValueError('Historical raw task unavailable without an embedded task')
            value['reason'] = 'Historical raw task bytes unavailable; embedded task and original hash retained in run record'
        return value

    def run(self, path, expected=None):
        path = str(_absolute(path))
        run_dir = Path(path).parent
        if self.output == run_dir or run_dir in self.output.parents:
            raise ValueError('Create the archive outside every historical run directory')
        if path in self.run_stack:
            raise ValueError('Cycle in attempt history')
        if path in self.runs:
            if expected is not None and self.files[self.runs[path]['record']] != expected:
                raise ValueError('Changed referenced acquisition run')
            return path
        self.run_stack.add(path)
        record_ref = self.blob(path, expected)
        record = _json(self.output / record_ref)
        _validate_run(record)
        source_root = _absolute(record['project'])
        if self.output == source_root or source_root in self.output.parents:
            raise ValueError('Create the archive outside every historical project directory')
        entry = {'original_path': path, 'record': record_ref, 'previous': None,
                 'observations': [], 'supplemental': [], 'snapshots': {}, 'raw_task': self.task(record)}
        self.runs[path] = entry
        for name, sha in _evidence(record):
            self.blob(name, sha)
        if record.get('previous_run'):
            entry['previous'] = self.run(record['previous_run'])
        entry['snapshots']['candidate'] = self.snapshot(record['project'], record['source'])
        if record.get('variant_source'):
            entry['snapshots']['checking_variant'] = self.snapshot(
                record.get('isolation', {}).get('scratch'), record['variant_source'])
        observations_dir = _absolute(Path(path).parent / 'observations')
        if observations_dir.exists():
            for observation in sorted(observations_dir.iterdir()):
                _absolute(observation)
                if observation.suffix == '.json':
                    entry['observations'].append(self.observation(observation, path))
        # Preserve acquisition logs and captures that were not attached to an
        # observation, without copying application binaries, caches or user data.
        run_dir = Path(path).parent
        supplemental = [Path(path)]
        for item in run_dir.iterdir():
            _absolute(item)
            if item.suffix in ('.log', '.xml', '.json') and not item.is_dir():
                supplemental.append(item)
        for dirname in ('captures', 'isolation-probe'):
            directory = _absolute(run_dir / dirname)
            if directory.exists():
                for parent, dirs, names in os.walk(directory, followlinks=False):
                    dirs[:] = sorted(d for d in dirs if d not in self.workflow.EXCLUDED)
                    for name in dirs + sorted(names):
                        _absolute(Path(parent) / name)
                    supplemental.extend(Path(parent) / n for n in sorted(names) if n not in self.workflow.EXCLUDED)
        for item in sorted(set(supplemental)):
            entry['supplemental'].append({'original_path': str(_absolute(item)), 'file': self.blob(item)})
        self.run_stack.remove(path)
        return path

    def observation(self, path, run_path, expected=None):
        path = str(_absolute(path))
        if path in self.observation_stack:
            raise ValueError('Cycle in observation reuse history')
        if path in self.observations:
            prior = self.observations[path]
            if prior['run'] != run_path or (expected is not None and self.files[prior['record']] != expected):
                raise ValueError('Changed referenced acquisition observation')
            return path
        self.observation_stack.add(path)
        record_ref = self.blob(path, expected)
        record = _json(self.output / record_ref)
        run = _json(self.output / self.runs[run_path]['record'])
        _validate_observation(record, run)
        entry = {'original_path': path, 'record': record_ref, 'run': run_path,
                 'derived_from': None, 'variant_snapshot': None}
        self.observations[path] = entry
        for name, sha in _observation_evidence(record):
            self.blob(name, sha)
        if record.get('variant_root'):
            entry['variant_snapshot'] = self.snapshot(record['variant_root'], record.get('variant_source'), record.get('variant_digest'))
        derived = record.get('derived_from')
        if derived:
            # A reused observation may depend on a run outside the rerun chain.
            source_run_path = str(_absolute(derived['run']))
            if source_run_path not in self.runs:
                self.run(source_run_path, derived['run_sha256'])
            elif self.files[self.runs[source_run_path]['record']] != derived['run_sha256']:
                raise ValueError('Changed referenced acquisition run')
            entry['derived_from'] = self.observation(derived['observation'], source_run_path, derived['observation_sha256'])
            source_run = _json(self.output / self.runs[source_run_path]['record'])
            if derived['source_digest'] != source_run['source']['digest'] or derived['helper_sha256'] != source_run.get('helper_sha256'):
                raise ValueError('Reused observation acquisition identities differ')
        self.observation_stack.remove(path)
        return path


def archive_run(run_path, output_dir, workflow_module):
    """Create a new bundle; reject changed required evidence and unsafe paths."""
    run_path = _absolute(run_path)
    output = _absolute(output_dir)
    if output.exists():
        raise ValueError('Archive output must be a new directory: ' + str(output))
    if not output.parent.is_dir():
        raise ValueError('Archive output parent must already exist')
    # In-project output could enter the source manifest while it is being read.
    first = _json(run_path)
    source = _absolute(first['project'])
    if output == source or source in output.parents or output == run_path.parent or run_path.parent in output.parents:
        raise ValueError('Create the archive outside the project and run directories')
    output.mkdir()
    try:
        (output / 'blobs').mkdir()
        builder = _Builder(output, workflow_module)
        root = builder.run(run_path)
        manifest = {'format_version': FORMAT_VERSION, 'kind': 'godot-workflow-historical-evidence',
                    'created_at': time.time(), 'root_run': root, 'runs': builder.runs,
                    'observations': builder.observations, 'inputs': builder.inputs,
                    'files': builder.files, 'claim': CLAIM, 'current_project_acceptance': False}
        (output / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
        return verify_archive(output)
    except Exception:
        shutil.rmtree(output)
        raise


def verify_archive(archive_dir, workflow_module=None):
    """Verify only retained bytes and recorded links; never read original roots."""
    root = _absolute(archive_dir)
    manifest = _json(root / MANIFEST)
    if manifest.get('format_version') != FORMAT_VERSION or manifest.get('kind') != 'godot-workflow-historical-evidence':
        raise ValueError('Unsupported historical archive format')
    if manifest.get('current_project_acceptance') is not False or manifest.get('claim') != CLAIM:
        raise ValueError('Archive must declare historical integrity limitations')
    files = manifest['files']
    actual = set()
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            path = _absolute(Path(parent) / name)
            mode = path.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError('Special archive file is not permitted: ' + str(path))
            if stat.S_ISREG(mode) and path != root / MANIFEST:
                actual.add(path.relative_to(root).as_posix())
    if actual != set(files):
        raise ValueError('Archive inventory differs from retained files')
    for name, sha in files.items():
        _relative(name)
        if not isinstance(sha, str) or not HEX.fullmatch(sha) or _hash(_read(root / name)) != sha:
            raise ValueError('Changed archived content: ' + str(name))
    for original, reference in manifest['inputs'].items():
        if not isinstance(original, str) or not Path(original).is_absolute() or '..' in Path(original).parts:
            raise ValueError('Invalid recorded input identity')
        _relative(reference)
        if reference not in files:
            raise ValueError('Missing portable input reference')
    if set(manifest['inputs'].values()) != set(files):
        raise ValueError('Retained files differ from original input inventory')

    def retained(reference, expected=None):
        _relative(reference)
        if reference not in files:
            raise ValueError('Missing portable evidence reference: ' + reference)
        if expected is not None and files[reference] != expected:
            raise ValueError('Archived evidence differs from recorded hash: ' + reference)
        return root / reference

    def input_ref(original, expected):
        # Original absolute names are identifiers only, never opened here.
        if original not in manifest['inputs']:
            raise ValueError('Missing archived input: ' + str(original))
        return retained(manifest['inputs'][original], expected)

    def snapshot(value, expected_manifest=None, expected_digest=None):
        if expected_manifest is not None:
            _manifest(expected_manifest)
            expected_digest = expected_manifest['digest']
            if value['recorded_manifest'] != expected_manifest:
                raise ValueError('Archived snapshot changed its recorded manifest')
        if value['recorded_digest'] != expected_digest:
            raise ValueError('Archived snapshot changed its recorded identity')
        recorded = value.get('recorded_manifest')
        if recorded is not None:
            _manifest(recorded)
            if recorded['digest'] != expected_digest:
                raise ValueError('Snapshot manifest differs from recorded digest')
        if value['status'] == 'unavailable':
            if value.get('files') or not value.get('reason'):
                raise ValueError('Unavailable snapshot must declare its limitation')
            return
        if value['status'] != 'retained' or recorded is None or set(value['files']) != set(recorded['files']):
            raise ValueError('Incomplete archived source snapshot')
        for name, sha in recorded['files'].items():
            _relative(name)
            retained(value['files'][name], sha)

    runs = manifest['runs']
    observations = manifest['observations']
    run_records = {}
    retained_observations = set()
    for key, entry in runs.items():
        if entry['original_path'] != key or manifest['inputs'].get(key) != entry['record']:
            raise ValueError('Run identity differs from portable index')
        r = _json(retained(entry['record']))
        _validate_run(r)
        run_records[key] = r
        if entry['previous'] != r.get('previous_run') or (entry['previous'] and entry['previous'] not in runs):
            raise ValueError('Incomplete or changed attempt history')
        for original, sha in _evidence(r):
            input_ref(original, sha)
        raw_task = entry.get('raw_task')
        if r.get('task_path'):
            if not raw_task or raw_task['original_path'] != r['task_path'] or raw_task['recorded_sha256'] != r['task_sha256']:
                raise ValueError('Missing or changed historical raw task identity')
            if raw_task['status'] == 'retained':
                retained(raw_task['file'], r['task_sha256'])
            elif raw_task['status'] != 'unavailable' or raw_task.get('file') or not raw_task.get('reason') or not isinstance(r.get('task'), dict):
                raise ValueError('Unavailable historical raw task lacks embedded task/limitation')
        elif raw_task is not None:
            raise ValueError('Invented historical raw task')
        for extra in entry['supplemental']:
            if manifest['inputs'].get(extra['original_path']) != extra['file']:
                raise ValueError('Supplemental input differs from portable index')
            retained(extra['file'])
        # The original input inventory is independent of the editable graph
        # indices. Every retained observation under this run must still be
        # visited, including failed observations omitted from a required list.
        run_dir = Path(key).parent
        observation_inputs = {original for original in manifest['inputs']
                              if Path(original).parent == run_dir / 'observations' and Path(original).suffix == '.json'}
        if len(entry['observations']) != len(set(entry['observations'])) or set(entry['observations']) != observation_inputs:
            raise ValueError('Retained observation inputs differ from run observation inventory')
        retained_observations.update(observation_inputs)
        supplemental_inputs = {key}
        for original in manifest['inputs']:
            candidate = Path(original)
            if ((candidate.parent == run_dir and candidate.suffix in ('.log', '.xml', '.json'))
                    or run_dir / 'captures' in candidate.parents
                    or run_dir / 'isolation-probe' in candidate.parents):
                supplemental_inputs.add(original)
        supplemental_originals = [extra['original_path'] for extra in entry['supplemental']]
        if len(supplemental_originals) != len(set(supplemental_originals)) or set(supplemental_originals) != supplemental_inputs:
            raise ValueError('Retained supplemental inputs differ from run inventory')
        if key not in supplemental_inputs:
            raise ValueError('Original run record missing from supplemental input inventory')
        snapshot(entry['snapshots']['candidate'], r['source'])
        if r.get('variant_source'):
            snapshot(entry['snapshots']['checking_variant'], r['variant_source'])

    if retained_observations != set(observations):
        raise ValueError('Retained observation inputs differ from observation graph')

    for key, entry in observations.items():
        if entry['original_path'] != key or manifest['inputs'].get(key) != entry['record'] or entry['run'] not in runs:
            raise ValueError('Observation identity differs from portable index')
        o = _json(retained(entry['record']))
        _validate_observation(o, run_records[entry['run']])
        for original, sha in _observation_evidence(o):
            input_ref(original, sha)
        if o.get('variant_root'):
            if not entry.get('variant_snapshot'):
                raise ValueError('Missing observation variant identity')
            snapshot(entry['variant_snapshot'], o.get('variant_source'), o.get('variant_digest'))
        derived = o.get('derived_from')
        if derived:
            if entry['derived_from'] != derived['observation'] or derived['run'] not in runs or entry['derived_from'] not in observations:
                raise ValueError('Missing observation acquisition history')
            input_ref(derived['run'], derived['run_sha256'])
            input_ref(derived['observation'], derived['observation_sha256'])
            prior_run = run_records[derived['run']]
            if observations[entry['derived_from']]['run'] != derived['run'] or derived['source_digest'] != prior_run['source']['digest'] or derived['helper_sha256'] != prior_run.get('helper_sha256'):
                raise ValueError('Changed observation acquisition identity')
        elif entry['derived_from'] is not None:
            raise ValueError('Invented observation acquisition history')

    checked_runs, active_runs, checked_obs, active_obs = set(), set(), set(), set()

    def check_observation_history(key):
        if key in active_obs:
            raise ValueError('Cycle in archived observation history')
        if key in checked_obs:
            return
        if key not in observations:
            raise ValueError('Missing archived observation')
        active_obs.add(key)
        entry = observations[key]
        if entry['derived_from']:
            check_observation_history(entry['derived_from'])
        active_obs.remove(key)
        checked_obs.add(key)

    def check_run_history(key):
        if key in active_runs:
            raise ValueError('Cycle in archived attempt history')
        if key in checked_runs:
            return
        if key not in runs:
            raise ValueError('Missing archived run')
        active_runs.add(key)
        if runs[key]['previous']:
            check_run_history(runs[key]['previous'])
        active_runs.remove(key)
        checked_runs.add(key)

    for key in runs:
        check_run_history(key)
    for key in observations:
        check_observation_history(key)

    visited_runs, visited_obs = set(), set()

    def visit_run(key):
        if key in visited_runs:
            return
        visited_runs.add(key)
        if runs[key]['previous']:
            visit_run(runs[key]['previous'])
        for obs_key in runs[key]['observations']:
            if observations.get(obs_key, {}).get('run') != key:
                raise ValueError('Observation assigned to the wrong archived run')
            visit_observation(obs_key)

    def visit_observation(key):
        if key in visited_obs:
            return
        visited_obs.add(key)
        entry = observations[key]
        visit_run(entry['run'])
        if entry['derived_from']:
            visit_observation(entry['derived_from'])

    visit_run(manifest['root_run'])
    if visited_runs != set(runs) or visited_obs != set(observations):
        raise ValueError('Unlinked records in historical archive')
    unavailable = []
    for key, entry in runs.items():
        unavailable.extend({'record': key, 'snapshot': name, 'reason': value['reason']}
                           for name, value in entry['snapshots'].items() if value['status'] == 'unavailable')
    unavailable.extend({'record': key, 'snapshot': 'observation_variant', 'reason': entry['variant_snapshot']['reason']}
                       for key, entry in observations.items() if (entry.get('variant_snapshot') or {}).get('status') == 'unavailable')
    unavailable_tasks = [{'record': key, 'original_path': entry['raw_task']['original_path'], 'reason': entry['raw_task']['reason']}
                         for key, entry in runs.items() if (entry.get('raw_task') or {}).get('status') == 'unavailable']
    return {'archive': str(root), 'outcome': 'pass', 'historical_integrity': 'verified',
            'current_project_acceptance': False, 'claim': CLAIM, 'runs': len(runs),
            'observations': len(observations), 'retained_files': len(files),
            'unavailable_source_snapshots': unavailable, 'unavailable_raw_tasks': unavailable_tasks}
