#!/usr/bin/env python3
"""Bounded Godot checks and observation records. Python 3.9+, standard library only."""
import argparse
import fnmatch
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

VERSION = '0.2.0'
PROFILE = 'godot-workflow.json'
CHECKS = {'import': 'GT02', 'parse': 'GT03', 'tests': 'GT04'}
OUTCOMES = {'pass', 'fail', 'error', 'blocked', 'not_applicable'}
EXCLUDED = {'.git', '.godot', '.godot-workflow-artifacts', '__pycache__', '.DS_Store'}
DIAGNOSTIC = re.compile(r'(?mi)^\s*(?:(?:SCRIPT ERROR|ERROR|Parse Error):|Unicode parsing error[:,])[^\r\n]*')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def encoded_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def load(path):
    return json.loads(Path(path).read_text())


def source_manifest(project):
    files = {}
    for parent, dirs, names in os.walk(project, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in dirs + sorted(names):
            path = Path(parent) / name
            if path.is_symlink():
                raise ValueError('Symlinked source needs a project-specific adapter: ' + str(path))
        for name in sorted(names):
            if name not in EXCLUDED:
                path = Path(parent) / name
                if not stat.S_ISREG(path.lstat().st_mode):
                    raise ValueError('Non-regular source file needs a project-specific adapter: ' + str(path))
                files[path.relative_to(project).as_posix()] = digest(path)
    return {'files': files, 'digest': encoded_hash(files), 'excluded_names': sorted(EXCLUDED)}


def get_project(value):
    path = Path(value).expanduser().resolve()
    if not (path / 'project.godot').is_file():
        raise ValueError('No project.godot at ' + str(path))
    return path


def profile_for(project):
    path = project / PROFILE
    data = load(path) if path.exists() else {}
    if not isinstance(data, dict) or data.get('format_version', 1) != 1:
        raise ValueError('Unsupported project profile format')
    for key in ('checks', 'script_excludes', 'observations', 'adopted_rules'):
        if key in data and not isinstance(data[key], list):
            raise ValueError('Profile ' + key + ' must be a list')
    if not isinstance(data.get('test', {}), dict):
        raise ValueError('Profile test must be an object')
    return data


def engine_path(explicit=None):
    value = explicit or os.environ.get('GODOT_BIN')
    candidates = [value] if value else [shutil.which('godot'), shutil.which('godot4'),
                                     '/Applications/Godot.app/Contents/MacOS/Godot']
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return Path(candidate).resolve()
    raise ValueError('Godot unavailable; pass --godot or set GODOT_BIN')


def identify_engine(path):
    result = subprocess.run([str(path), '--version'], capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise ValueError('Godot version probe failed: ' + result.stderr)
    return {'path': str(path), 'version': result.stdout.strip(), 'sha256': digest(path)}


def run_process(command, directory, log, timeout):
    """Retain output and raw status; terminate owned descendants at the boundary."""
    if timeout <= 0:
        raise ValueError('Timeout must be positive')
    started = time.time()
    timed_out = False
    proc = None
    error = None
    with Path(log).open('wb') as output:
        try:
            proc = subprocess.Popen([str(c) for c in command], cwd=str(directory), stdout=output,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
        except OSError as exc:
            error = str(exc)
        finally:
            if proc is not None:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
    text = Path(log).read_text(errors='replace')
    return {'command': [str(c) for c in command], 'raw_exit_code': proc.returncode if proc else None,
            'timed_out': timed_out, 'launch_error': error, 'seconds': round(time.time() - started, 3),
            'deadline_seconds': timeout, 'log': str(Path(log).resolve()),
            'log_sha256': digest(log), 'diagnostics': DIAGNOSTIC.findall(text)}


def process_outcome(process):
    if process['timed_out'] or process['launch_error']:
        return 'error'
    return 'fail' if process['raw_exit_code'] != 0 or process['diagnostics'] else 'pass'


def junit_result(path, expected):
    """Reconcile per-case results instead of trusting runner exit or summary counts."""
    if not Path(path).is_file():
        return {'outcome': 'error', 'reason': 'Expected JUnit report missing'}
    try:
        root = ET.parse(path).getroot()
        cases = list(root.iter('testcase'))
        names = [c.get('name', '') for c in cases]
        if any(not n for n in names) or len(names) != len(set((c.get('classname', ''), c.get('name')) for c in cases)):
            raise ValueError('Missing or duplicate case identity')
        skipped = sum(c.find('skipped') is not None for c in cases)
        failures = sum(c.find('failure') is not None for c in cases)
        errors = sum(c.find('error') is not None for c in cases)
        declared = root.get('tests')
        if declared is not None and int(declared) != len(cases):
            raise ValueError('Report total differs from case inventory')
        missing = sorted(set(expected) - set(names))
        counts = {'discovered': len(cases), 'executed': len(cases) - skipped,
                  'passed': len(cases) - skipped - failures - errors,
                  'failed': failures, 'errored': errors, 'skipped_or_pending': skipped}
        failed = not cases or failures or errors or skipped or missing
        return {'outcome': 'fail' if failed else 'pass', 'counts': counts,
                'case_ids': names, 'missing_required_cases': missing,
                'reason': 'Expected cases and outcomes reconciled' if not failed else 'Incomplete or failing test coverage',
                'report': str(Path(path).resolve()), 'report_sha256': digest(path)}
    except (ET.ParseError, ValueError, OSError) as exc:
        return {'outcome': 'error', 'reason': 'Unreliable JUnit report: ' + str(exc)}


def prepare_workspace(project, run_dir, engine, timeout):
    if any((project / name).exists() for name in ('project.binary', 'override.cfg')):
        raise ValueError('Binary project settings and override.cfg need a project-specific isolation adapter')
    scratch = run_dir / 'project'
    shutil.copytree(project, scratch, ignore=lambda _, names: [n for n in names if n in EXCLUDED])
    settings_path = scratch / 'project.godot'
    original_settings_hash = digest(settings_path)
    name = 'godot-workflow-' + run_dir.name
    binary_dir = run_dir / 'engine'
    binary_dir.mkdir()
    original = Path(engine)
    if sys.platform == 'darwin' and len(original.parents) > 2 and original.parents[2].suffix == '.app':
        app = binary_dir / original.parents[2].name
        shutil.copytree(original.parents[2], app)
        binary = app / 'Contents/MacOS' / original.name
    else:
        binary = binary_dir / 'Godot'
        shutil.copy2(engine, binary)
    (binary_dir / '_sc_').touch()
    # Self-contained mode redirects editor settings, but this pin still resolves
    # runtime user:// through the OS data path. Give only the unique fixture name
    # an exclusive symlink into this run; never replace an existing directory.
    data = run_dir / 'user-data'
    data.mkdir()
    if sys.platform == 'darwin':
        link = Path.home() / 'Library/Application Support/Godot/app_userdata' / name
    elif sys.platform.startswith('linux'):
        link = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))) / 'godot/app_userdata' / name
    else:
        raise ValueError('Only macOS/Linux editor-binary isolation is implemented')
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(data, target_is_directory=True)
    save(run_dir / 'owned-user-link.json', {'link': str(link), 'target': str(data)})
    probe = run_dir / 'isolation-probe'
    probe.mkdir()
    (probe / 'project.godot').write_text('[application]\nconfig/name=' + json.dumps(name) + '\n')
    script = probe / 'probe.gd'
    # Parse the candidate settings as data in a clean project. Native ConfigFile
    # handles legal whitespace/quoted keys; textual rewrites can leave an effective
    # original name or feature override and escape the isolated user-data mapping.
    script.write_text("""extends SceneTree
func _initialize():
	var settings = ConfigFile.new()
	if settings.load(%s) != OK:
		push_error("Cannot parse candidate project settings")
		quit(1)
		return
	for section in settings.get_sections():
		for key in settings.get_section_keys(section):
			var full = key if section.is_empty() else section + "/" + key
			if full == "application/config/use_custom_user_dir" and settings.get_value(section, key):
				push_error("Custom user data directory needs a project-specific isolation adapter")
				quit(1)
				return
			if full.begins_with("application/config/name.") or full.begins_with("application/config/use_custom_user_dir.") or full.begins_with("application/config/custom_user_dir_name.") or full == "application/config/project_settings_override" or full.begins_with("application/config/project_settings_override."):
				push_error("Application path overrides need a project-specific isolation adapter")
				quit(1)
				return
			if full == "debug/file_logging/log_path" or full.begins_with("debug/file_logging/log_path."):
				var log_path = settings.get_value(section, key)
				if not log_path is String or not (log_path.begins_with("user://") or log_path.begins_with("res://")) or ".." in log_path.split("/") or log_path.contains(String.chr(92)):
					push_error("External or traversing log paths need a project-specific isolation adapter")
					quit(1)
					return
			if full == "application/run/disable_stderr" or full.begins_with("application/run/disable_stderr.") or full == "application/run/disable_stdout" or full.begins_with("application/run/disable_stdout."):
				settings.set_value(section, key, false)
			if full == "application/config/name":
				settings.set_value(section, key, %s)
	settings.set_value("application", "config/name", %s)
	settings.set_value("application", "run/disable_stderr", false)
	settings.set_value("application", "run/disable_stdout", false)
	if settings.save(%s) != OK:
		push_error("Cannot save isolated project settings")
		quit(1)
		return
	print("GWF_SETTINGS_NORMALIZED")
	print("GWF_PATH=" + OS.get_user_data_dir())
	quit(0)
""" % (json.dumps(str(settings_path)), json.dumps(name), json.dumps(name), json.dumps(str(settings_path))))
    process = run_process([binary, '--headless', '--path', probe, '--script', script],
                          probe, run_dir / 'isolation.log', timeout)
    output = Path(process['log']).read_text(errors='replace')
    found = re.search(r'(?m)^GWF_PATH=(.+)$', output)
    actual = Path(found.group(1).strip()).resolve() if found else None
    if process_outcome(process) != 'pass' or 'GWF_SETTINGS_NORMALIZED' not in output or actual is None or run_dir not in actual.parents:
        raise ValueError('Pre-scenario user:// isolation not established; see ' + str(run_dir / 'isolation.log'))
    isolation = {'process': process, 'user_data_dir': str(actual),
                 'source_project_settings_sha256': original_settings_hash,
                 'variant_project_settings_sha256': digest(settings_path),
                 'transformation': 'Native ConfigFile normalization, enabled diagnostic streams and unique application name in isolated copy: ' + name,
                 'binary': str(binary), 'scratch': str(scratch), 'owned_user_link': str(link)}
    return scratch, binary, isolation


def parse_check(scratch, binary, manifest, profile, run_dir, timeout):
    excluded = profile.get('script_excludes', ['addons/**'])
    scripts = [f for f in manifest['files'] if f.endswith('.gd') and
               not any(fnmatch.fnmatch(f, pattern) for pattern in excluded)]
    resources = [f for f in manifest['files'] if f.endswith(('.tscn', '.tres', '.scn', '.res')) and
                 not any(fnmatch.fnmatch(f, pattern) for pattern in excluded)]
    processes = []
    for index, script in enumerate(scripts):
        process = run_process([binary, '--headless', '--path', scratch, '--check-only', '--script', 'res://' + script],
                              scratch, run_dir / ('parse-%s.log' % index), timeout)
        processes.append(process)
        if process_outcome(process) == 'error':
            break
    if resources and not any(process_outcome(p) == 'error' for p in processes):
        probe = scratch / '__workflow_load.gd'
        paths = json.dumps(['res://' + f for f in resources])
        probe.write_text('extends SceneTree\nfunc _initialize():\n\tvar paths = ' + paths +
                         '\n\tvar failed = false\n\tfor path in paths:\n'
                         '\t\tif ResourceLoader.load(path) == null:\n\t\t\tfailed = true\n'
                         '\tprint("GWF_LOAD_COMPLETE")\n\tquit(1 if failed else 0)\n')
        process = run_process([binary, '--headless', '--path', scratch, '--script', probe],
                              scratch, run_dir / 'load.log', timeout)
        processes.append(process)
        if 'GWF_LOAD_COMPLETE' not in Path(process['log']).read_text(errors='replace'):
            process['launch_error'] = 'Missing resource-load completion marker'
    states = [process_outcome(p) for p in processes]
    outcome = 'error' if 'error' in states else 'fail' if 'fail' in states else 'pass'
    if not scripts and not resources:
        outcome = 'blocked'
    return {'outcome': outcome, 'scripts': scripts, 'resources': resources, 'excluded_patterns': excluded,
            'reason': 'Explicit native inventory; dynamic dependencies and public types need scoped review',
            'processes': processes}


def behavior_check(scratch, binary, profile, expected, run_dir, timeout):
    test = profile.get('test', {})
    if test.get('framework', 'gut') != 'gut':
        return {'outcome': 'blocked', 'reason': 'This adapter supports GUT; retain the project runner and assess its evidence separately'}
    runner = scratch / 'addons/gut/gut_cmdln.gd'
    if not runner.is_file():
        return {'outcome': 'blocked', 'reason': 'GUT not present in project; no addon was injected'}
    report = run_dir / 'junit.xml'
    process = run_process([binary, '--headless', '--path', scratch, '--script', runner,
                           '-gdir=' + test.get('directory', 'res://tests'), '-ginclude_subdirs',
                           '-gexit', '-gdisable_colors', '-gjunit_xml_file=' + str(report)],
                          scratch, run_dir / 'tests.log', timeout)
    if process['timed_out'] or process['launch_error']:
        return {'outcome': 'error', 'reason': 'Test process did not complete reliably', 'processes': [process]}
    result = junit_result(report, expected)
    if process_outcome(process) == 'fail' and result['outcome'] == 'pass':
        result.update(outcome='fail', reason='Runner status or native diagnostics contradict a passing report')
    result['processes'] = [process]
    return result


def check(args):
    project = get_project(args.project)
    profile = profile_for(project)
    task_path = Path(args.task).resolve() if args.task else None
    task = load(task_path) if task_path else {}
    checks = args.checks.split(',') if args.checks else profile.get('checks', ['import', 'parse'])
    required = task.get('required_checks', checks)
    if not checks or any(c not in CHECKS for c in checks + required):
        raise ValueError('Supported checks: import,parse,tests')
    observations = task.get('observations', profile.get('observations', []))
    ids = [o['id'] for o in observations]
    if len(ids) != len(set(ids)) or any(o.get('gate') not in ('GT05', 'GT06') for o in observations):
        raise ValueError('Observation IDs must be unique and gate must be GT05 or GT06')
    for o in observations:
        if not o.get('scene') or not o.get('expected'):
            raise ValueError('Observation needs scene and expected behavior')
    manifest = source_manifest(project)
    run_id = time.strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
    base = Path(args.output).expanduser().resolve() if args.output else project / '.godot-workflow-artifacts'
    # Output inside source must be the excluded artifacts tree, otherwise it recursively copies itself.
    if project == base or (project in base.parents and '.godot-workflow-artifacts' not in base.relative_to(project).parts):
        raise ValueError('Use an external output directory or the project .godot-workflow-artifacts directory')
    run_dir = base / run_id
    run_dir.mkdir(parents=True)
    result = {'format_version': 1, 'toolkit_version': VERSION, 'helper_sha256': digest(__file__),
              'run_id': run_id, 'project': str(project), 'source': manifest,
              'profile_sha256': encoded_hash(profile), 'task': task,
              'task_path': str(task_path) if task_path else None,
              'task_sha256': digest(task_path) if task_path else None,
              'required_checks': required, 'selected_checks': checks,
              'required_observations': observations, 'results': {}, 'created_at': time.time(),
              'previous_run': str(Path(args.previous).resolve()) if args.previous else None,
              'rerun_reason': args.reason, 'resolution': args.resolution}
    if args.previous and not args.reason:
        raise ValueError('Diagnostic rerun requires --reason; every attempt is retained')
    try:
        engine = identify_engine(engine_path(args.godot))
        result['engine'] = engine
        pin = profile.get('engine_version')
        if not pin or pin != engine['version']:
            raise ValueError('Declare the actual engine pin in the game profile; actual=' + engine['version'])
        result['results']['preflight'] = {'gate': 'GT00', 'outcome': 'pass', 'reason': 'Engine pin and source inventoried'}
        scratch, binary, isolation = prepare_workspace(project, run_dir, engine['path'], args.timeout)
        result['isolation'] = isolation
        for name in checks:
            if name == 'import':
                process = run_process([binary, '--headless', '--path', scratch, '--import'],
                                      scratch, run_dir / 'import.log', args.timeout)
                record = {'outcome': process_outcome(process), 'processes': [process],
                          'reason': 'Native cold import; exit and diagnostics inspected'}
            elif name == 'parse':
                record = parse_check(scratch, binary, manifest, profile, run_dir, args.timeout)
            else:
                expected = task.get('required_test_cases', profile.get('test', {}).get('expected_cases', []))
                record = behavior_check(scratch, binary, profile, expected, run_dir, args.timeout)
            record['gate'] = CHECKS[name]
            result['results'][name] = record
        result['variant_source'] = source_manifest(scratch)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        result['results']['preflight'] = {'gate': 'GT00', 'outcome': 'blocked', 'reason': str(exc)}
    result['source_unchanged_during_run'] = source_manifest(project)['digest'] == manifest['digest']
    save(run_dir / 'run.json', result)
    summary = summarize_record(run_dir / 'run.json')
    print(json.dumps({'run': str(run_dir / 'run.json'), 'summary': summary}, indent=2))
    return 0 if summary['outcome'] == 'pass' else 1


def artifact_issues(record):
    issues = []
    processes = [p for result in record['results'].values() for p in result.get('processes', [])]
    if record.get('isolation', {}).get('process'):
        processes.append(record['isolation']['process'])
    for proc in processes:
        path = Path(proc['log'])
        if not path.is_file() or digest(path) != proc['log_sha256']:
            issues.append('Missing/changed process log: ' + str(path))
    for result in record['results'].values():
        if 'report' in result:
            path = Path(result['report'])
            if not path.is_file() or digest(path) != result['report_sha256']:
                issues.append('Missing/changed test report')
    return issues


def changed_files(before, after):
    return [name for name in sorted(set(before['files']) | set(after['files']))
            if before['files'].get(name) != after['files'].get(name)]


def retained_failure_issues(path, visited=None, memo=None):
    """Reconcile failure history without requiring an old candidate to stay current."""
    path = Path(path).resolve()
    seen = set() if visited is None else set(visited)
    completed = {} if memo is None else memo
    if path in seen:
        raise ValueError('Cycle in retained observation/attempt history')
    if path in completed:
        return completed[path]
    seen.add(path)
    record = load(path)
    states = [r['outcome'] for r in record['results'].values()]
    for observation_path in sorted((path.parent / 'observations').glob('*.json')):
        observation = load(observation_path)
        states.append(observation['outcome'])
        if observation.get('kind') == 'reused':
            # A reused pass cannot hide newly recorded failures in its origin.
            inherited = retained_failure_issues(observation['derived_from']['run'], seen, completed)
            states.extend(inherited)
    if record.get('previous_run'):
        inherited = retained_failure_issues(record['previous_run'], seen, completed)
        if not record.get('resolution'):
            states.extend(inherited)
    completed[path] = [state for state in ('fail', 'error') if state in states]
    return completed[path]


def observation_scenario(record, identifier):
    return next((o for o in record['required_observations'] if o['id'] == identifier), None)


def observation_dependencies(manifest, selected):
    if not selected:
        return dict(manifest['files']), 'all_source'
    names = set(selected)
    names.update(n for n in ('project.godot', PROFILE) if n in manifest['files'])
    dependencies = {}
    for name in sorted(names):
        name = name.removeprefix('res://')
        parts = Path(name).parts
        if not parts or Path(name).is_absolute() or '..' in parts or '\\' in name or ':' in name:
            raise ValueError('Dependency must be a project-relative source file: ' + name)
        if name not in manifest['files']:
            raise ValueError('Dependency absent from recorded source: ' + name)
        dependencies[name] = manifest['files'][name]
    return dependencies, 'files'


def reuse_issues(prior, observation, current, allow_helper_change=False):
    issues = []
    old_scenario = observation_scenario(prior, observation.get('id'))
    new_scenario = observation_scenario(current, observation.get('id'))
    if not old_scenario or old_scenario != new_scenario:
        issues.append('Observation requirement changed or is absent')
    if observation.get('outcome') != 'pass':
        issues.append('Only a passing observation can be reused; retain failures as history')
    if not prior.get('source_unchanged_during_run') or not current.get('source_unchanged_during_run'):
        issues.append('Source changed during checking')
    if any(prior['results'].get(k, {}).get('outcome') != 'pass' for k in prior['required_checks']):
        issues.append('Original required checks did not pass')
    if any(current['results'].get(k, {}).get('outcome') != 'pass' for k in current['required_checks']):
        issues.append('Current required checks must pass before reuse')
    old_engine, new_engine = prior.get('engine', {}), current.get('engine', {})
    if not all(old_engine.get(k) and old_engine.get(k) == new_engine.get(k) for k in ('version', 'sha256')):
        issues.append('Engine version/build identity changed or is unknown')
    if prior.get('profile_sha256') != current.get('profile_sha256'):
        issues.append('Project profile changed; reacquire the observation')
    tool_changed = any(prior.get(k) != current.get(k) for k in ('helper_sha256', 'helper_components'))
    if tool_changed and not allow_helper_change:
        issues.append('Checking helper changed; explicit reviewed helper-change reuse is required')
    dependencies = observation.get('dependencies', prior['source']['files'])
    scope = observation.get('dependency_scope', 'all_source')
    if scope not in ('all_source', 'files') or not isinstance(dependencies, dict) or not dependencies:
        issues.append('Observation dependency scope is invalid')
    elif scope == 'all_source' and prior['source']['digest'] != current['source']['digest']:
        issues.append('Full-source observation requires an unchanged source identity')
    else:
        mandatory = {n for n in ('project.godot', PROFILE) if n in prior['source']['files']}
        if scope == 'files' and not mandatory.issubset(dependencies):
            issues.append('Observation dependencies omit project settings or profile')
        for name, value in dependencies.items():
            if (name not in prior['source']['files'] or name not in current['source']['files']
                    or not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value)
                    or prior['source']['files'][name] != value or current['source']['files'][name] != value):
                issues.append('Observation dependency changed: ' + name)
    return issues


def observation_issues(observation, record, path, visited=None):
    path = Path(path).resolve()
    seen = set() if visited is None else set(visited)
    if path in seen:
        return ['Cycle in observation reuse history']
    seen.add(path)
    issues = []
    if observation.get('kind', 'acquired') not in ('acquired', 'reused'):
        issues.append('Invalid observation kind')
    dependencies = observation.get('dependencies', record['source']['files'])
    scope = observation.get('dependency_scope', 'all_source')
    if scope not in ('all_source', 'files') or not isinstance(dependencies, dict) or not dependencies:
        issues.append('Invalid observation dependency scope')
    else:
        mandatory = {n for n in ('project.godot', PROFILE) if n in record['source']['files']}
        if ((scope == 'all_source' and dependencies != record['source']['files'])
                or (scope == 'files' and not mandatory.issubset(dependencies))):
            issues.append('Observation dependency inventory differs from its scope')
        for name, value in dependencies.items():
            if (name not in record['source']['files'] or not isinstance(value, str)
                    or not re.fullmatch(r'[0-9a-f]{64}', value)
                    or record['source']['files'][name] != value):
                issues.append('Invalid recorded observation dependency: ' + str(name))
    if observation.get('source_manifest') is not None and observation['source_manifest'] != record['source']:
        issues.append('Observation source manifest differs from its run')
    scenario = observation_scenario(record, observation.get('id'))
    if (not scenario or any(observation.get(k) != scenario.get(k) for k in ('gate', 'scene', 'expected'))
            or observation.get('run_id') != record['run_id']
            or observation.get('source_digest') != record['source']['digest']):
        issues.append('Observation does not match the recorded source or scenario')
    if observation.get('outcome') not in OUTCOMES - {'not_applicable'}:
        issues.append('Invalid observation outcome')
    for artifact in observation.get('artifacts', []):
        target = Path(artifact['path'])
        if not target.is_file() or digest(target) != artifact['sha256']:
            issues.append('Observation artifact missing or changed: ' + str(target))
    if observation.get('variant_root'):
        try:
            if source_manifest(get_project(observation['variant_root']))['digest'] != observation['variant_digest']:
                issues.append('Observation variant source changed')
        except (OSError, ValueError):
            issues.append('Observation variant source missing or unsupported')
    if observation.get('kind') == 'reused':
        try:
            original = observation['derived_from']
            prior_path, original_path = Path(original['run']), Path(original['observation'])
            if (digest(prior_path) != original['run_sha256']
                    or digest(original_path) != original['observation_sha256']):
                raise ValueError('Original reuse records changed')
            prior, old = load(prior_path), load(original_path)
            if (original['source_digest'] != prior['source']['digest']
                    or original['helper_sha256'] != prior.get('helper_sha256')):
                raise ValueError('Original acquisition identity fields differ from the run')
            if original_path.resolve().parent != prior_path.resolve().parent / 'observations':
                raise ValueError('Original observation is outside its recorded run')
            issues.extend(artifact_issues(prior))
            if retained_failure_issues(prior_path):
                issues.append('Originating observation/attempt history has unresolved failures or errors')
            issues.extend(observation_issues(old, prior, original_path, seen))
            reuse = observation['reuse']
            if not reuse['reason'].strip() or not reuse['reviewer'].strip():
                raise ValueError('Reuse needs a named reviewer and reason')
            if not isinstance(reuse.get('allow_helper_change', False), bool):
                raise ValueError('Helper-change review flag must be a boolean')
            issues.extend(reuse_issues(prior, old, record, reuse.get('allow_helper_change', False)))
            if reuse['changed_files'] != changed_files(prior['source'], record['source']):
                raise ValueError('Reuse changed-file inventory differs')
            for field in ('id', 'gate', 'scene', 'expected', 'actual', 'observer', 'method', 'sequence',
                          'outcome', 'variant_root', 'variant_digest', 'variant_source', 'transformation', 'artifacts'):
                if observation.get(field) != old.get(field):
                    raise ValueError('Reuse altered original observation field: ' + field)
            if observation['acquired_at'] != old.get('acquired_at', old['created_at']):
                raise ValueError('Reuse altered the acquisition timestamp')
            if (observation.get('dependencies') != old.get('dependencies', prior['source']['files'])
                    or observation.get('dependency_scope') != old.get('dependency_scope', 'all_source')):
                raise ValueError('Reuse altered the original dependency scope')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            issues.append('Invalid reuse provenance: ' + str(exc))
    return issues


def summarize_record(path, visited=None):
    path = Path(path).resolve()
    visited = set() if visited is None else visited
    if path in visited:
        raise ValueError('Cycle in attempt history')
    visited.add(path)
    r = load(path)
    if r.get('format_version') != 1 or not r.get('results'):
        raise ValueError('Missing/unsupported run record')
    problems = artifact_issues(r)
    project = get_project(r['project'])
    if source_manifest(project)['digest'] != r['source']['digest'] or not r['source_unchanged_during_run']:
        problems.append('Candidate source changed; evidence stale')
    if encoded_hash(profile_for(project)) != r['profile_sha256']:
        problems.append('Project profile changed')
    if r.get('task_path') and (not Path(r['task_path']).is_file() or digest(r['task_path']) != r['task_sha256']):
        problems.append('Task changed or missing')
    if r.get('engine') and (not Path(r['engine']['path']).is_file() or digest(r['engine']['path']) != r['engine']['sha256']):
        problems.append('Engine changed or missing')
    if r.get('helper_sha256') != digest(__file__):
        problems.append('Checking helper changed; recalibrate/recheck affected evidence')
    states = [x['outcome'] for x in r['results'].values()]
    if any(s not in OUTCOMES for s in states):
        raise ValueError('Invalid recorded outcome')
    for name in r['required_checks']:
        if name not in r['results']:
            problems.append('Required check absent: ' + name)
    observed = []
    for opath in sorted((path.parent / 'observations').glob('*.json')):
        o = load(opath)
        observation_problems = observation_issues(o, r, opath)
        if observation_problems:
            problems.extend('Observation ' + o.get('id', '?') + ': ' + issue for issue in observation_problems)
        else:
            observed.append(o)
    for required in r['required_observations']:
        found = [o for o in observed if o['id'] == required['id']]
        if not found:
            problems.append('Required observation absent: ' + required['id'])
        else:
            states.extend(o['outcome'] for o in found)
    unresolved_error = 'error' in states
    previous = r.get('previous_run')
    if previous:
        prior = summarize_record(previous, visited)
        if prior['unresolved_failure'] and not r.get('resolution'):
            problems.append('Earlier observed failure unresolved; later pass alone is insufficient')
            states.append('fail')
        if prior['unresolved_error'] and not r.get('resolution'):
            unresolved_error = True
            problems.append('Earlier infrastructure error needs a recorded resolution')
    outcome = 'error' if 'error' in states else 'fail' if 'fail' in states else 'blocked' if problems or 'blocked' in states else 'pass'
    return {'gate': 'GT09', 'outcome': outcome, 'problems': problems,
            'unresolved_failure': 'fail' in states, 'unresolved_error': unresolved_error,
            'observation_records': {kind: sum(o.get('kind', 'acquired') == kind for o in observed)
                                    for kind in ('acquired', 'reused')},
            'claim': 'Current selected evidence complete; observation credibility and scope need judgment' if outcome == 'pass' else 'Required verification remains incomplete or failing'}


def observe(args):
    path = Path(args.run).resolve()
    r = load(path)
    if source_manifest(get_project(r['project']))['digest'] != r['source']['digest']:
        raise ValueError('Candidate changed; create a current run before observing')
    selected = [o for o in r['required_observations'] if o['id'] == args.id]
    if not selected or selected[0]['scene'] != args.scene:
        raise ValueError('Observation must identify a declared scenario and its actual scene')
    if args.outcome == 'not_applicable':
        raise ValueError('Change declared scope explicitly; observation cannot waive a required scenario')
    for text in (args.observer, args.method, args.actual, args.sequence):
        if not text.strip():
            raise ValueError('Observer, method, actual outcome and interaction sequence are required')
    if args.variant_root and not args.transformation:
        raise ValueError('Controlled variant needs --transformation')
    variant = get_project(args.variant_root) if args.variant_root else None
    artifacts = [{'path': str(Path(p).resolve()), 'sha256': digest(p)} for p in args.artifact]
    dependencies, scope = observation_dependencies(r['source'], args.dependency)
    now = time.time()
    acquired_at = args.acquired_at if args.acquired_at is not None else now
    if not 0 < acquired_at <= now:
        raise ValueError('Acquisition time must be a positive past/current Unix timestamp')
    o = {'id': args.id, 'gate': selected[0]['gate'], 'run_id': r['run_id'],
         'source_digest': r['source']['digest'], 'source_manifest': r['source'], 'scene': args.scene,
         'expected': selected[0]['expected'], 'actual': args.actual, 'outcome': args.outcome,
         'observer': args.observer, 'method': args.method, 'sequence': args.sequence,
         'artifacts': artifacts, 'created_at': now, 'recorded_at': now, 'acquired_at': acquired_at,
         'acquisition_time_basis': 'observer_declared' if args.acquired_at is not None else 'recording_time',
         'kind': 'acquired', 'dependencies': dependencies, 'dependency_scope': scope,
         'transformation': args.transformation,
         'variant_root': str(variant) if variant else None,
         'variant_digest': source_manifest(variant)['digest'] if variant else None,
         'variant_source': source_manifest(variant) if variant else None}
    # Arbitrary scenario strings cannot escape the observations directory.
    out = path.parent / 'observations' / (uuid.uuid4().hex + '.json')
    save(out, o)
    print(str(out))
    return 0


def reuse_observation(args):
    path, previous_path = Path(args.run).resolve(), Path(args.from_run).resolve()
    original_path = Path(args.observation).resolve()
    current, prior, original = load(path), load(previous_path), load(original_path)
    if path == previous_path:
        raise ValueError('Reuse requires a different checking run; original observations remain intact')
    if source_manifest(get_project(current['project']))['digest'] != current['source']['digest']:
        raise ValueError('Candidate changed; create a current run before reusing observations')
    if original_path.parent != previous_path.parent / 'observations':
        raise ValueError('Original observation must belong to the supplied prior run')
    if not args.reason.strip() or not args.reviewer.strip():
        raise ValueError('Reuse needs a named reviewer and reason')
    issues = artifact_issues(prior) + observation_issues(original, prior, original_path)
    if retained_failure_issues(previous_path):
        issues.append('Originating observation/attempt history has unresolved failures or errors')
    issues += reuse_issues(prior, original, current, args.allow_helper_change)
    if issues:
        raise ValueError('Cannot reuse observation: ' + '; '.join(issues))
    now = time.time()
    o = dict(original)
    o.update(kind='reused', run_id=current['run_id'], source_digest=current['source']['digest'],
             source_manifest=current['source'], created_at=now, recorded_at=now,
             acquired_at=original.get('acquired_at', original['created_at']),
             acquisition_time_basis=original.get('acquisition_time_basis', 'legacy_recording_time'),
             dependencies=original.get('dependencies', prior['source']['files']),
             dependency_scope=original.get('dependency_scope', 'all_source'),
             derived_from={'run': str(previous_path), 'run_sha256': digest(previous_path),
                           'observation': str(original_path), 'observation_sha256': digest(original_path),
                           'source_digest': prior['source']['digest'], 'helper_sha256': prior.get('helper_sha256')},
             reuse={'reviewer': args.reviewer, 'reason': args.reason,
                    'changed_files': changed_files(prior['source'], current['source']),
                    'allow_helper_change': args.allow_helper_change})
    out = path.parent / 'observations' / (uuid.uuid4().hex + '.json')
    save(out, o)
    print(str(out))
    return 0


def archive_module():
    path = Path(__file__).with_name('evidence_archive.py')
    spec = importlib.util.spec_from_file_location('godot_evidence_archive', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def init_project(args):
    project = get_project(args.project)
    root = Path(__file__).resolve().parents[1]
    profile = load(root / 'templates/project.json')
    profile['engine_version'] = identify_engine(engine_path(args.godot))['version']
    if (project / 'addons/gut/gut_cmdln.gd').is_file():
        profile['test']['framework'] = 'gut'
    elif (project / 'addons/gdUnit4').exists():
        profile['test']['framework'] = 'gdunit4'
    pointer = (root / 'templates/AGENTS.fragment.md').read_text()
    existing = (project / 'AGENTS.md').read_text() if (project / 'AGENTS.md').exists() else ''
    changes = []
    if not (project / PROFILE).exists():
        changes.append(PROFILE)
    if '<!-- godot-workflows:start -->' not in existing:
        changes.append('AGENTS.md (append pointer)')
    ignore = (project / '.gitignore').read_text() if (project / '.gitignore').exists() else ''
    if '.godot-workflow-artifacts/' not in ignore.splitlines():
        changes.append('.gitignore (append artifacts exclusion)')
    if args.apply:
        if PROFILE in changes:
            save(project / PROFILE, profile)
        if 'AGENTS.md (append pointer)' in changes:
            (project / 'AGENTS.md').write_text(existing + ('\n\n' if existing else '') + pointer)
        if '.gitignore (append artifacts exclusion)' in changes:
            (project / '.gitignore').write_text(ignore + ('\n' if ignore else '') + '.godot-workflow-artifacts/\n')
    print(json.dumps({'applied': args.apply, 'changes': changes, 'proposed_profile': profile,
                      'existing_profile': 'preserved' if (project / PROFILE).exists() else 'absent'}, indent=2))
    return 0


def cleanup_run(path):
    run_dir = Path(path).resolve().parent
    ownership = run_dir / 'owned-user-link.json'
    if ownership.is_file():
        record = load(ownership)
        link = Path(record['link'])
        target = Path(record['target'])
        if target.parent != run_dir or not link.name.startswith('godot-workflow-'):
            raise ValueError('Invalid owned user-data mapping')
        if link.is_symlink() and link.resolve() == target.resolve():
            link.unlink()
        elif link.exists():
            raise ValueError('User-data link was replaced; refusing cleanup')
    print('Removed only the owned user-data symlink; logs and run data retained.')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'check', 'init-project'):
        p = sub.add_parser(name)
        p.add_argument('--project', required=True)
        p.add_argument('--godot')
        if name == 'check':
            p.add_argument('--checks', help='Comma separated import,parse,tests; task-required omissions remain blocked')
            p.add_argument('--task')
            p.add_argument('--output')
            p.add_argument('--timeout', type=float, default=120, help='Seconds per external process; tune to project workload')
            p.add_argument('--previous', help='Previous run.json; retained, never overwritten')
            p.add_argument('--reason', default='')
            p.add_argument('--resolution', default='', help='Supported diagnosis/correction with affected retest; never inferred')
        if name == 'init-project':
            p.add_argument('--apply', action='store_true')
    p = sub.add_parser('summarize')
    p.add_argument('--run', required=True)
    p = sub.add_parser('cleanup-run')
    p.add_argument('--run', required=True)
    p = sub.add_parser('observe')
    for key in ('run', 'id', 'scene', 'observer', 'method', 'sequence', 'actual'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--outcome', choices=sorted(OUTCOMES - {'not_applicable'}), required=True)
    p.add_argument('--artifact', action='append', default=[])
    p.add_argument('--variant-root')
    p.add_argument('--transformation', default='')
    p.add_argument('--dependency', action='append', default=[], help='Claim dependencies; defaults to all source, settings/profile always included')
    p.add_argument('--acquired-at', type=float, help='Actual acquisition Unix timestamp; defaults to recording time')
    p = sub.add_parser('reuse-observation')
    for key in ('run', 'from-run', 'observation', 'reason', 'reviewer'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--allow-helper-change', action='store_true', help='Explicit reviewed reuse across helper identities; current checks still must pass')
    p = sub.add_parser('archive')
    p.add_argument('--run', required=True)
    p.add_argument('--output', required=True)
    p = sub.add_parser('verify-archive')
    p.add_argument('--archive', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'check':
            return check(args)
        if args.command == 'observe':
            return observe(args)
        if args.command == 'reuse-observation':
            return reuse_observation(args)
        if args.command in ('archive', 'verify-archive'):
            archive = archive_module()
            # Pass a module-like namespace so the sibling has no import-cycle or host-path dependency.
            from types import SimpleNamespace
            api = SimpleNamespace(**globals())
            if args.command == 'archive':
                result = archive.archive_run(Path(args.run), Path(args.output), api)
            else:
                result = archive.verify_archive(Path(args.archive), api)
            print(json.dumps(result, indent=2))
            return 0 if result['outcome'] == 'pass' else 1
        if args.command == 'init-project':
            return init_project(args)
        if args.command == 'cleanup-run':
            return cleanup_run(args.run)
        if args.command == 'summarize':
            result = summarize_record(args.run)
            print(json.dumps(result, indent=2))
            return 0 if result['outcome'] == 'pass' else 1
        project = get_project(args.project)
        print(json.dumps({'project': str(project), 'engine': identify_engine(engine_path(args.godot)),
                          'profile': profile_for(project), 'source': source_manifest(project),
                          'observed_runner_files': {
                              'gut': (project / 'addons/gut/gut_cmdln.gd').is_file(),
                              'gdunit4': (project / 'addons/gdUnit4').exists()},
                          'adapter': 'macOS/Linux editor binary; GUI access not yet demonstrated'}, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'outcome': 'error', 'reason': str(exc)}, indent=2))
        return 2


if __name__ == '__main__':
    sys.exit(main())
