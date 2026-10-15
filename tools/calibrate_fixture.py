#!/usr/bin/env python3
"""Run independently specified valid/fault variants through the real checking CLI."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import godot_workflow as workflow
from bootstrap_fixture import verify_addon


def change(project, file, before, after):
    path = project / file
    text = path.read_text()
    if before not in text:
        raise ValueError('Seed no longer applies: ' + file + ' / ' + before)
    path.write_text(text.replace(before, after))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--cases', help='Comma-separated case names for a bounded calibration subset; default runs all')
    args = parser.parse_args()
    verify_addon(ROOT / 'validation/fixture/addons/gut', workflow.load(ROOT / 'validation/dependencies.json')['gut'])
    base = (args.output or ROOT / '.godot-workflow-artifacts' / ('calibration-' + uuid.uuid4().hex[:8])).resolve()
    base.mkdir(parents=True)
    cases = [
        ('valid-baseline', 'pass', None),
        ('valid-user-log-path', 'pass', ('project.godot', '[application]', '[debug]\nfile_logging/log_path="user://logs/fixture.log"\n\n[application]')),
        ('external-log-path', 'blocked', ('project.godot', '[application]', '[debug]\nfile_logging/log_path="/tmp/godot-workflow-unowned.log"\n\n[application]')),
        ('traversing-log-path', 'blocked', ('project.godot', '[application]', '[debug]\nfile_logging/log_path="user://../../unowned.log"\n\n[application]')),
        ('feature-log-path-alias', 'blocked', ('project.godot', '[application]', '[debug/file_logging]\nlog_path.macos="/tmp/godot-workflow-unowned.log"\n\n[application]')),
        ('invalid-script-hidden-diagnostics', 'fail', ('actor_state.gd', 'extends Resource', 'extends ThisIsNotARealGodotType')),
        ('valid-section-name-alias', 'pass', ('project.godot', '[display]', '[application/config]\nname="Godot Workflow Fixture"\n\n[display]')),
        ('valid-root-name-alias', 'pass', ('project.godot', 'config_version=5', 'config_version=5\n"application/config/name"="Godot Workflow Fixture"')),
        ('root-custom-directory', 'blocked', ('project.godot', 'config_version=5', 'config_version=5\n"application/config/use_custom_user_dir"=true')),
        ('section-feature-name', 'blocked', ('project.godot', '[display]', '[application/config]\nname.macos="Unsupported identity"\n\n[display]')),
        ('settings-override-selector', 'blocked', ('project.godot', '[application]', '[application]\nconfig/project_settings_override="res://other.cfg"')),
        ('feature-override-selector', 'blocked', ('project.godot', 'config_version=5', 'config_version=5\n"application/config/project_settings_override.macos"="res://other.cfg"')),
        ('override-config-file', 'blocked', None),
        ('binary-project-settings', 'blocked', None),
        ('valid-spaced-name', 'pass', ('project.godot', 'config/name="Godot Workflow Fixture"', 'config/name = "Godot Workflow Fixture"')),
        ('valid-quoted-name', 'pass', ('project.godot', 'config/name="Godot Workflow Fixture"', '"config/name" = "Godot Workflow Fixture"')),
        ('feature-name-override', 'blocked', ('project.godot', '[application]', '[application]\n"config/name.macos" = "Unsupported identity"')),
        ('custom-user-directory', 'blocked', ('project.godot', '[application]', '[application]\n"config/use_custom_user_dir" = true')),
        ('feature-user-directory', 'blocked', ('project.godot', '[application]', '[application]\n"config/use_custom_user_dir.macos" = true')),
        ('invalid-script', 'fail', ('actor_state.gd', 'extends Resource', 'extends ThisIsNotARealGodotType')),
        ('missing-asset', 'fail', ('enemy.tscn', 'res://enemy_definition.tres', 'res://missing_definition.tres')),
        ('reversed-physical-bindings', 'fail', None),
        ('native-unicode-diagnostic', 'fail', ('tests/test_contracts.gd', 'extends GutTest',
            'extends GutTest\n\nfunc test_native_unicode_diagnostic() -> void:\n\tPackedByteArray([0xff]).get_string_from_utf8()')),
        ('shared-mutable-state', 'fail', ('enemy.tscn', 'resource_local_to_scene = true', 'resource_local_to_scene = false')),
        ('ignored-tuning', 'fail', ('enemy.gd', 'state.health = health', 'state.health = 3')),
        ('lost-owned-child', 'fail', ('tests/test_contracts.gd', 'child.owner = root', '# Intentionally missing saved owner')),
        ('wrong-assertion', 'fail', ('tests/test_contracts.gd', 'assert_eq(first.state.health, 2)', 'assert_eq(first.state.health, 99)')),
        ('empty-suite', 'fail', ('tests/test_contracts.gd', 'func test_', 'func example_')),
        ('pending-case', 'fail', ('tests/test_contracts.gd', 'extends GutTest', 'extends GutTest\n\nfunc test_pending_calibration() -> void:\n\tpending("Deliberate calibration case")')),
        ('hung-test', 'error', ('tests/test_contracts.gd', 'extends GutTest', 'extends GutTest\n\nfunc test_hung_calibration() -> void:\n\tawait get_tree().create_timer(10000).timeout')),
        ('valid-procedural-content', 'pass', ('enemy.gd', 'var ready_count: int = 0', 'func make_transient_effect() -> void:\n\tvar effect = Node2D.new()\n\tadd_child(effect)\n\teffect.queue_free()\n\nvar ready_count: int = 0')),
        ('valid-dynamic-boundary', 'pass', ('enemy.gd', 'var ready_count: int = 0', 'func read_external_field(data: Dictionary, key: String) -> Variant:\n\treturn data.get(key)\n\nvar ready_count: int = 0')),
    ]
    if args.cases:
        selected = {name.strip() for name in args.cases.split(',') if name.strip()}
        unknown = selected - {name for name, _, _ in cases}
        if unknown or not selected:
            parser.error('Unknown or empty calibration case selection: ' + ', '.join(sorted(unknown)))
        cases = [case for case in cases if case[0] in selected]
    results = []
    started = time.time()
    baseline = None
    for name, expected, fault in cases:
        project = base / name / 'project'
        shutil.copytree(ROOT / 'validation/fixture', project,
                        ignore=lambda _, names: [n for n in names if n in workflow.EXCLUDED])
        if fault:
            change(project, *fault)
        if name == 'reversed-physical-bindings':
            # Swap only the arrow bindings; A/D remain a valid alternative.
            change(project, 'project.godot', '"physical_keycode":4194319', '"physical_keycode":0')
            change(project, 'project.godot', '"physical_keycode":4194321', '"physical_keycode":4194319')
            change(project, 'project.godot', '"physical_keycode":0', '"physical_keycode":4194321')
        if name == 'invalid-script-hidden-diagnostics':
            with (project / 'project.godot').open('a') as settings:
                settings.write('\n[application/run]\ndisable_stderr=true\ndisable_stderr.macos=true\ndisable_stdout=true\n')
        if name == 'override-config-file':
            (project / 'override.cfg').write_text('[application]\nconfig/name="Unsupported identity"\n')
        if name == 'binary-project-settings':
            (project / 'project.binary').write_bytes(b'Unsupported compiled project settings')
        checks = ['import', 'parse'] if name in ('invalid-script', 'missing-asset', 'invalid-script-hidden-diagnostics') else ['import', 'parse', 'tests']
        task_path = base / name / 'task.json'
        workflow.save(task_path, {'outcome': 'Machine-only calibration: ' + name,
                                 'acceptance': ['Detect the stated fault or preserve the valid alternative'],
                                 'required_checks': checks, 'observations': [],
                                 'conditions': {'randomness': 'None used', 'timing': 'Scene signals/frame completion; external process deadline'}})
        command = [sys.executable, str(ROOT / 'tools/godot_workflow.py'), 'check', '--project', str(project),
                   '--task', str(task_path), '--checks', ','.join(checks), '--timeout', '10' if name == 'hung-test' else '30']
        if args.godot:
            command.extend(['--godot', args.godot])
        completed = subprocess.run(command, capture_output=True, text=True)
        (base / name / 'cli.log').write_text(completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        run = Path(payload['run'])
        record = workflow.load(run)
        actual = payload['summary']['outcome']
        row = {'case': name, 'expected': expected, 'actual': actual, 'matches': actual == expected,
               'cli_exit_code': completed.returncode, 'run': str(run),
               'checks': {k: v['outcome'] for k, v in record['results'].items()}}
        if 'tests' in record['results']:
            row['tests'] = record['results']['tests']
        if name in ('valid-baseline', 'valid-spaced-name', 'valid-quoted-name', 'valid-section-name-alias', 'valid-root-name-alias') and actual == 'pass':
            # Check effective settings in the transformed native project, in
            # addition to the clean pre-scenario probe. This is trusted fixture code.
            isolated = Path(record['isolation']['scratch'])
            probe = run.parent / 'candidate-path.gd'
            probe.write_text('extends SceneTree\nfunc _initialize():\n' +
                             '\tprint("GWF_ACTUAL_PATH=" + OS.get_user_data_dir())\n\tquit(0)\n')
            process = workflow.run_process([record['isolation']['binary'], '--headless', '--path', isolated,
                                            '--script', probe], isolated, run.parent / 'candidate-path.log', 30)
            output = Path(process['log']).read_text(errors='replace')
            paths = [line.split('=', 1)[1] for line in output.splitlines() if line.startswith('GWF_ACTUAL_PATH=')]
            isolated_path = len(paths) == 1 and Path(paths[0]).resolve() == Path(record['isolation']['user_data_dir'])
            row['candidate_user_data_isolated'] = workflow.process_outcome(process) == 'pass' and isolated_path
            row['candidate_path_probe'] = process
            row['matches'] = row['matches'] and row['candidate_user_data_isolated']
        if name == 'native-unicode-diagnostic':
            # Native invalid-UTF8 conversion must be detected even with a clean
            # runner exit and a passing report. A printed imitation is insufficient.
            tests = record['results'].get('tests', {})
            process = tests.get('processes', [{}])[0]
            output = Path(process['log']).read_text(errors='replace') if process.get('log') else ''
            row['native_unicode_emitted'] = 'Unicode parsing error' in output
            row['native_unicode_zero_exit'] = process.get('raw_exit_code') == 0
            report = tests.get('report')
            report_result = (workflow.junit_result(report, workflow.profile_for(project)['test']['expected_cases'])
                             if report else {})
            row['native_unicode_report_passed'] = report_result.get('outcome') == 'pass'
            row['matches'] = (row['matches'] and row['native_unicode_emitted']
                              and row['native_unicode_zero_exit'] and row['native_unicode_report_passed'])
        results.append(row)
        print(name + ': expected=' + expected + ' actual=' + actual, flush=True)
        if name == 'valid-baseline':
            baseline = (run, project)
        with __import__('contextlib').redirect_stdout(__import__('io').StringIO()):
            workflow.cleanup_run(run)
        # The copied vendor app is reproducible; keep source, raw reports and logs.
        shutil.rmtree(run.parent / 'engine', ignore_errors=True)
    if baseline:
        run, project = baseline
        (project / 'dirty-untracked.gd').write_text('extends Node\n')
        result = workflow.summarize_record(run)
        results.append({'case': 'dirty-after-success', 'expected': 'blocked', 'actual': result['outcome'],
                        'matches': result['outcome'] == 'blocked', 'run': str(run)})
        (project / 'dirty-untracked.gd').unlink()
        report = run.parent / 'junit.xml'
        raw = report.read_bytes()
        report.unlink()
        result = workflow.summarize_record(run)
        results.append({'case': 'missing-report-after-success', 'expected': 'blocked', 'actual': result['outcome'],
                        'matches': result['outcome'] == 'blocked', 'run': str(run)})
        report.write_text('<corrupt')
        result = workflow.summarize_record(run)
        results.append({'case': 'corrupt-report-after-success', 'expected': 'blocked', 'actual': result['outcome'],
                        'matches': result['outcome'] == 'blocked', 'run': str(run)})
        report.write_bytes(raw)
        # Run the observation-bearing profile through summary without claiming GUI work.
        record = workflow.load(run)
        record['required_observations'] = workflow.profile_for(project)['observations']
        obs_run = run.parent / 'observation-scope.json'
        workflow.save(obs_run, record)
        result = workflow.summarize_record(obs_run)
        results.append({'case': 'unobserved-required-play', 'expected': 'blocked', 'actual': result['outcome'],
                        'matches': result['outcome'] == 'blocked', 'run': str(obs_run)})
    report = {'toolkit_version': workflow.VERSION, 'engine': workflow.identify_engine(workflow.engine_path(args.godot)),
              'gut_pin': workflow.load(ROOT / 'validation/dependencies.json')['gut'],
              'seconds': round(time.time() - started, 2), 'cases': results,
              'all_matched': all(row['matches'] for row in results),
              'limits': ['Machine-only fixture calibration; physical-key event injection covers InputMap/scene routing. Editor reopen, Inspector UI and real hardware/focus remain separate observations.',
                         'Public typing and preference/architecture correctness remain judgment.',
                         'Copied applications removed after calibration; original tool hashes, source, reports and logs retained.']}
    workflow.save(base / 'calibration.json', report)
    print('Report: ' + str(base / 'calibration.json'))
    return 0 if report['all_matched'] else 1


if __name__ == '__main__':
    sys.exit(main())
