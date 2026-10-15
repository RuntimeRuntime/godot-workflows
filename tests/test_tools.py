import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


workflow = module('workflow', ROOT / 'tools/godot_workflow.py')
packaging = module('packaging', ROOT / 'tools/package_skills.py')
bootstrap = module('bootstrap', ROOT / 'tools/bootstrap_fixture.py')


class SandboxCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='godot-workflows-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / 'game'
        self.project.mkdir()
        (self.project / 'project.godot').write_text('[application]\nconfig/name="Example"\n')
        workflow.save(self.project / workflow.PROFILE, {'format_version': 1})

    def report(self, xml):
        path = self.root / 'junit.xml'
        path.write_text(xml)
        return path

    def run_record(self, outcome='pass', observations=None):
        run_dir = self.project / '.godot-workflow-artifacts' / os.urandom(4).hex()
        run_dir.mkdir(parents=True)
        path = run_dir / 'run.json'
        data = {'format_version': 1, 'run_id': run_dir.name, 'project': str(self.project),
                'source': workflow.source_manifest(self.project),
                'profile_sha256': workflow.encoded_hash(workflow.profile_for(self.project)),
                'helper_sha256': workflow.digest(workflow.__file__),
                'source_unchanged_during_run': True,
                'required_checks': ['parse'], 'selected_checks': ['parse'],
                'required_observations': observations or [],
                'results': {'parse': {'gate': 'GT03', 'outcome': outcome}}}
        workflow.save(path, data)
        return path, data


class ReportTests(SandboxCase):
    def test_real_cases_can_pass(self):
        path = self.report('<testsuites tests="1"><testsuite><testcase name="test_scene"/></testsuite></testsuites>')
        r = workflow.junit_result(path, ['test_scene'])
        self.assertEqual(r['outcome'], 'pass')
        self.assertEqual(r['counts']['executed'], 1)

    def test_zero_cases_do_not_pass(self):
        self.assertEqual(workflow.junit_result(self.report('<testsuites tests="0"/>'), [])['outcome'], 'fail')

    def test_pending_fails_even_with_successful_exit(self):
        path = self.report('<testsuite tests="1"><testcase name="test_scene"><skipped/></testcase></testsuite>')
        self.assertEqual(workflow.junit_result(path, ['test_scene'])['outcome'], 'fail')

    def test_missing_required_case_is_reported(self):
        path = self.report('<testsuite><testcase name="other"/></testsuite>')
        self.assertEqual(workflow.junit_result(path, ['required'])['missing_required_cases'], ['required'])

    def test_failing_assertion_is_not_an_infrastructure_error(self):
        path = self.report('<testsuite><testcase name="test_scene"><failure>wrong health</failure></testcase></testsuite>')
        self.assertEqual(workflow.junit_result(path, [])['outcome'], 'fail')

    def test_corrupt_missing_and_inconsistent_reports_are_errors(self):
        for xml in ('<broken', '<testsuite tests="2"><testcase name="one"/></testsuite>'):
            with self.subTest(xml=xml):
                self.assertEqual(workflow.junit_result(self.report(xml), [])['outcome'], 'error')
        self.assertEqual(workflow.junit_result(self.root / 'absent.xml', [])['outcome'], 'error')


class EvidenceTests(SandboxCase):
    def test_adoption_preview_and_apply_preserve_existing_profile_and_instructions(self):
        profile = self.project / workflow.PROFILE
        before = profile.read_bytes()
        instructions = self.project / 'AGENTS.md'
        instructions.write_bytes(b'Existing rules with intentional spacing.\n')
        with mock.patch.object(workflow, 'engine_path', return_value=Path('/fake/godot')), \
                mock.patch.object(workflow, 'identify_engine', return_value={'version': 'fixture-pin'}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(workflow.main(['init-project', '--project', str(self.project)]), 0)
            self.assertEqual(instructions.read_bytes(), b'Existing rules with intentional spacing.\n')
            self.assertEqual(workflow.main(['init-project', '--project', str(self.project), '--apply']), 0)
            applied = instructions.read_bytes()
            self.assertTrue(applied.startswith(b'Existing rules with intentional spacing.\n'))
            self.assertEqual(profile.read_bytes(), before)
            self.assertEqual(workflow.main(['init-project', '--project', str(self.project), '--apply']), 0)
            self.assertEqual(instructions.read_bytes(), applied)

    def test_cleanup_removes_only_the_exact_owned_link(self):
        path, _ = self.run_record()
        data = path.parent / 'user-data'
        data.mkdir()
        link = self.root / 'godot-workflow-test'
        link.symlink_to(data)
        workflow.save(path.parent / 'owned-user-link.json', {'link': str(link), 'target': str(data)})
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.cleanup_run(path)
        self.assertFalse(link.exists())
        self.assertTrue(data.is_dir())
        link.mkdir()
        with self.assertRaisesRegex(ValueError, 'replaced'):
            workflow.cleanup_run(path)

    def test_fresh_evidence_passes_then_dirty_untracked_input_blocks(self):
        path, _ = self.run_record()
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'pass')
        (self.project / 'new_script.gd').write_text('extends Node\n')
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'blocked')

    def test_cache_and_evidence_do_not_change_source_identity(self):
        before = workflow.source_manifest(self.project)
        (self.project / '.godot').mkdir()
        (self.project / '.godot/cache').write_text('different')
        self.run_record()
        self.assertEqual(before, workflow.source_manifest(self.project))

    def test_required_check_omitted_cannot_pass(self):
        path, data = self.run_record()
        data['required_checks'].append('tests')
        workflow.save(path, data)
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'blocked')

    def test_unobserved_editor_case_blocks(self):
        path, _ = self.run_record(observations=[{'id': 'reopen', 'gate': 'GT05', 'scene': 'res://enemy.tscn', 'expected': 'saved children'}])
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'blocked')

    def test_wrong_scene_is_rejected_then_named_observation_is_accepted(self):
        path, _ = self.run_record(observations=[{'id': 'reopen', 'gate': 'GT05', 'scene': 'res://enemy.tscn', 'expected': 'saved children'}])
        args = ['observe', '--run', str(path), '--id', 'reopen', '--scene', 'res://wrong.tscn',
                '--observer', 'Fixture tester', '--method', 'Editor interaction', '--sequence', 'Save, close, reopen',
                '--actual', 'Children persisted', '--outcome', 'pass']
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(workflow.main(args), 2)
            args[args.index('res://wrong.tscn')] = 'res://enemy.tscn'
            self.assertEqual(workflow.main(args), 0)
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'pass')

    def test_failure_is_retained_after_passing_observation(self):
        path, _ = self.run_record(observations=[{'id': 'play', 'gate': 'GT06', 'scene': 'res://main.tscn', 'expected': 'input works'}])
        args = ['observe', '--run', str(path), '--id', 'play', '--scene', 'res://main.tscn',
                '--observer', 'Fixture tester', '--method', 'Actual input', '--sequence', 'Pause, click, resume',
                '--actual', 'Input leaked', '--outcome', 'fail']
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(workflow.main(args), 0)
            args[-1] = 'pass'
            self.assertEqual(workflow.main(args), 0)
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'fail')

    def test_later_pass_needs_supported_resolution(self):
        prior, _ = self.run_record('fail')
        current, data = self.run_record()
        data['previous_run'] = str(prior)
        workflow.save(current, data)
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'fail')
        data['resolution'] = 'Connection owner corrected and repeated-transition regression retested'
        workflow.save(current, data)
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'pass')

    def test_infrastructure_error_survives_multiple_unresolved_reruns(self):
        prior, _ = self.run_record('error')
        middle, data = self.run_record()
        data['previous_run'] = str(prior)
        workflow.save(middle, data)
        current, data = self.run_record()
        data['previous_run'] = str(middle)
        workflow.save(current, data)
        for path in (middle, current):
            result = workflow.summarize_record(path)
            self.assertEqual(result['outcome'], 'blocked')
            self.assertTrue(result['unresolved_error'])
        data['resolution'] = 'Infrastructure corrected; affected checks retested'
        workflow.save(current, data)
        result = workflow.summarize_record(current)
        self.assertEqual(result['outcome'], 'pass')
        self.assertFalse(result['unresolved_error'])

    def test_missing_or_changed_isolation_probe_log_blocks_closure(self):
        path, data = self.run_record()
        log = path.parent / 'isolation.log'
        log.write_text('GWF_PATH=isolated-user-data')
        data['isolation'] = {'process': {'log': str(log), 'log_sha256': workflow.digest(log)}}
        workflow.save(path, data)
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'pass')
        log.write_text('changed')
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'blocked')
        log.unlink()
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'blocked')

    def test_missing_or_changed_log_blocks_closure(self):
        path, data = self.run_record()
        log = path.parent / 'process.log'
        log.write_text('completed')
        data['results']['parse']['processes'] = [{'log': str(log), 'log_sha256': workflow.digest(log)}]
        workflow.save(path, data)
        log.write_text('truncated')
        self.assertEqual(workflow.summarize_record(path)['outcome'], 'blocked')

    def test_symlinked_source_is_not_followed(self):
        (self.project / 'external').symlink_to(self.root / 'private')
        with self.assertRaisesRegex(ValueError, 'Symlinked source'):
            workflow.source_manifest(self.project)

    def test_timeout_keeps_partial_log_and_raw_status(self):
        log = self.root / 'timeout.log'
        process = workflow.run_process([sys.executable, '-u', '-c', 'import time; print("started"); time.sleep(20)'], self.root, log, 0.2)
        self.assertTrue(process['timed_out'])
        self.assertEqual(workflow.process_outcome(process), 'error')
        self.assertIn('started', log.read_text())
        self.assertNotEqual(process['raw_exit_code'], 0)

    def test_native_error_with_zero_exit_is_not_green(self):
        process = workflow.run_process([sys.executable, '-c', 'print("ERROR: missing asset")'], self.root, self.root / 'error.log', 5)
        self.assertEqual(process['raw_exit_code'], 0)
        self.assertEqual(workflow.process_outcome(process), 'fail')


class DependencyTests(SandboxCase):
    def test_existing_addon_cache_must_match_locked_content(self):
        addon = self.root / 'validation/fixture/addons/gut'
        addon.mkdir(parents=True)
        script = addon / 'gut_cmdln.gd'
        script.write_text('locked fixture content')
        pin = {'addon_tree_sha256': bootstrap.addon_hash(addon)}
        workflow.save(self.root / 'validation/dependencies.json', {'gut': pin})
        with mock.patch.object(bootstrap, 'ROOT', self.root), \
                mock.patch.object(sys, 'argv', ['bootstrap_fixture.py']), \
                mock.patch.object(bootstrap.subprocess, 'run') as fetch, \
                contextlib.redirect_stdout(io.StringIO()):
            bootstrap.main()
            fetch.assert_not_called()
            script.write_text('changed content')
            with self.assertRaisesRegex(ValueError, 'differs from the locked dependency'):
                bootstrap.main()
        self.assertEqual(script.read_text(), 'changed content')

    def test_addon_cache_symlinks_are_rejected(self):
        addon = self.root / 'gut'
        addon.mkdir()
        (addon / 'external.gd').symlink_to(self.project / 'project.godot')
        with self.assertRaisesRegex(ValueError, 'without symlinks'):
            bootstrap.addon_hash(addon)


class PackageTests(SandboxCase):
    def packages(self):
        path = self.root / 'packages'
        packaging.build(path)
        return path

    def skills_repo(self):
        path = self.root / 'skills-repo'
        (path / 'scripts').mkdir(parents=True)
        (path / 'scripts/skills.js').write_text('// manager fixture')
        (path / 'skills.json').write_text('{"enabled": ["local/existing"]}')
        (path / 'AGENTS.md').write_text('Existing instructions\n')
        return path

    def test_self_contained_packages_validate_and_run_outside_checkout(self):
        packages = self.packages()
        for skill in packages.iterdir():
            packaging.validate_links(skill)
            result = subprocess.run([sys.executable, str(skill / 'scripts/godot_workflow.py'), '--help'], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_preview_is_read_only_and_apply_preserves_manager_state(self):
        packages = self.packages()
        repo = self.skills_repo()
        before = (repo / 'skills.json').read_bytes()
        packaging.install(packages, repo)
        self.assertFalse((repo / 'local').exists())
        packaging.install(packages, repo, True)
        self.assertEqual((repo / 'skills.json').read_bytes(), before)
        self.assertEqual((repo / 'AGENTS.md').read_text(), 'Existing instructions\n')
        packaging.install(packages, repo, True)

    def test_local_edits_and_unowned_files_are_preserved(self):
        packages = self.packages()
        repo = self.skills_repo()
        packaging.install(packages, repo, True)
        skill = repo / 'local/godot-author-scenes'
        (skill / 'SKILL.md').write_text('Local edit')
        with self.assertRaisesRegex(ValueError, 'local edits'):
            packaging.install(packages, repo, True)
        self.assertEqual((skill / 'SKILL.md').read_text(), 'Local edit')

    def test_conflict_is_discovered_before_any_destination_changes(self):
        packages = self.packages()
        repo = self.skills_repo()
        conflicting = repo / 'local/godot-verify-behavior'
        conflicting.mkdir(parents=True)
        (conflicting / 'SKILL.md').write_text('User-owned')
        with self.assertRaisesRegex(ValueError, 'not owned'):
            packaging.install(packages, repo, True)
        self.assertFalse((repo / 'local/godot-author-scenes').exists())

    def test_generated_package_modification_is_rejected(self):
        packages = self.packages()
        repo = self.skills_repo()
        (packages / 'godot-author-scenes/SKILL.md').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'changed after build'):
            packaging.install(packages, repo, True)

    def test_broken_reference_is_rejected(self):
        page = self.root / 'broken.md'
        page.write_text('[reference](missing.md)')
        with self.assertRaisesRegex(ValueError, 'Broken/nonportable'):
            packaging.validate_links(self.root)

    def test_existing_manager_activates_packages_in_temporary_codex_home(self):
        manager = Path('/Users/kyle/Documents/code/Skills/scripts/skills.js')
        if not manager.exists() or not shutil.which('node'):
            self.skipTest('Personal manager/Node unavailable; generic package checks still run')
        repo = self.skills_repo()
        shutil.copy2(manager, repo / 'scripts/skills.js')
        existing = repo / 'local/existing'
        existing.mkdir(parents=True)
        (existing / 'SKILL.md').write_text('---\nname: existing\ndescription: Existing fixture skill\n---\nPreserve this skill.\n')
        workflow.save(repo / 'skills.json', {'version': 1, 'enabled': ['local/existing'], 'installed': {}})
        packaging.install(self.packages(), repo, True)
        # CODEX_HOME retains its intended meaning: isolate the child manager's
        # real activation directory, without changing this process or user setup.
        environment = dict(os.environ, CODEX_HOME=str(self.root / 'activation'))
        names = json.loads((ROOT / 'toolkit.json').read_text())['skills']
        for name in names:
            result = subprocess.run(['node', 'scripts/skills.js', 'enable', 'local/' + name],
                                    cwd=repo, env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((self.root / 'activation/skills' / name).resolve(), repo / 'local' / name)
        for command in ('validate', 'doctor'):
            result = subprocess.run(['node', 'scripts/skills.js', command], cwd=repo,
                                    env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('local/existing', workflow.load(repo / 'skills.json')['enabled'])


if __name__ == '__main__':
    unittest.main()
