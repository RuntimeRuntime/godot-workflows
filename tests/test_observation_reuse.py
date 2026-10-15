"""Claim-level reuse preserves acquired evidence and rejects stale dependencies."""
import contextlib
import io
import json
from pathlib import Path

from test_tools import SandboxCase, workflow


class ObservationReuseTests(SandboxCase):
    def setUp(self):
        super().setUp()
        (self.project / 'main.gd').write_text('extends Node\n')
        (self.project / 'README.md').write_text('Original explanation\n')
        self.engine = self.root / 'engine'
        self.engine.write_bytes(b'fixed engine identity')
        self.capture = self.root / 'capture.png'
        self.capture.write_bytes(b'observed pixels')
        self.scenario = {'id': 'play', 'gate': 'GT06', 'scene': 'res://main.tscn', 'expected': 'Movement and pause work'}

    def new_run(self, outcome='pass', scenario=None):
        path, record = self.run_record(outcome, observations=[scenario or self.scenario])
        record['engine'] = {'path': str(self.engine), 'version': 'fixture-engine', 'sha256': workflow.digest(self.engine)}
        workflow.save(path, record)
        return path

    def cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = workflow.main(list(args))
        return result, output.getvalue()

    def acquired(self, path, dependencies=(), outcome='pass', variant=None):
        args = ['observe', '--run', str(path), '--id', 'play', '--scene', self.scenario['scene'],
                '--observer', 'Actual observer', '--method', 'Native keyboard input',
                '--sequence', 'Right, pause, resume', '--actual', 'Ship moved and paused', '--outcome', outcome,
                '--artifact', str(self.capture), '--acquired-at', '1000']
        for dependency in dependencies:
            args += ['--dependency', dependency]
        if variant:
            args += ['--variant-root', str(variant), '--transformation', 'Controlled Inspector speed variant']
        result, output = self.cli(*args)
        self.assertEqual(result, 0, output)
        return Path(output.strip())

    def reused(self, path, prior, observation, extra=()):
        return self.cli('reuse-observation', '--run', str(path), '--from-run', str(prior),
                        '--observation', str(observation), '--reviewer', 'Independent reviewer',
                        '--reason', 'Reviewed unchanged claim dependencies against changed files', *extra)

    def test_reuse_preserves_original_and_reports_acquisition_separately(self):
        prior = self.new_run()
        observation = self.acquired(prior)
        original_bytes = observation.read_bytes()
        current = self.new_run()
        status, output = self.reused(current, prior, observation)
        self.assertEqual(status, 0, output)
        reused = workflow.load(output.strip())
        self.assertEqual(reused['kind'], 'reused')
        self.assertEqual(reused['acquired_at'], 1000)
        self.assertGreater(reused['recorded_at'], 1000)
        self.assertEqual(reused['observer'], 'Actual observer')
        self.assertEqual(reused['reuse']['reviewer'], 'Independent reviewer')
        self.assertEqual(reused['reuse']['changed_files'], [])
        self.assertEqual(observation.read_bytes(), original_bytes)
        summary = workflow.summarize_record(current)
        self.assertEqual(summary['outcome'], 'pass')
        self.assertEqual(summary['observation_records'], {'acquired': 0, 'reused': 1})

    def test_explicit_dependencies_allow_document_edit_but_not_gameplay_edit(self):
        prior = self.new_run()
        observation = self.acquired(prior, ['main.gd'])
        (self.project / 'README.md').write_text('Updated explanation\n')
        current = self.new_run()
        status, output = self.reused(current, prior, observation)
        self.assertEqual(status, 0, output)
        self.assertEqual(workflow.load(output.strip())['reuse']['changed_files'], ['README.md'])
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'pass')
        (self.project / 'main.gd').write_text('extends Node2D\n')
        current = self.new_run()
        status, output = self.reused(current, prior, observation)
        self.assertEqual(status, 2)
        self.assertIn('dependency changed: main.gd', output)

    def test_default_scope_rejects_added_source(self):
        prior = self.new_run()
        observation = self.acquired(prior)
        (self.project / 'new_script.gd').write_text('extends Node\n')
        status, output = self.reused(self.new_run(), prior, observation)
        self.assertEqual(status, 2)
        self.assertIn('unchanged source identity', output)

    def test_settings_and_profile_cannot_be_excluded_from_file_scope(self):
        prior = self.new_run()
        observation = self.acquired(prior, ['main.gd'])
        data = workflow.load(observation)
        self.assertIn('project.godot', data['dependencies'])
        self.assertIn(workflow.PROFILE, data['dependencies'])
        (self.project / 'project.godot').write_text('[application]\nconfig/name="Changed"\n')
        status, output = self.reused(self.new_run(), prior, observation)
        self.assertEqual(status, 2)
        self.assertIn('dependency changed: project.godot', output)

    def test_helper_change_needs_explicit_review_and_engine_change_is_rejected(self):
        prior = self.new_run()
        observation = self.acquired(prior)
        data = workflow.load(prior)
        data['helper_sha256'] = 'older checking helper'
        workflow.save(prior, data)
        current = self.new_run()
        status, output = self.reused(current, prior, observation)
        self.assertEqual(status, 2)
        self.assertIn('explicit reviewed helper-change', output)
        status, output = self.reused(current, prior, observation, ['--allow-helper-change'])
        self.assertEqual(status, 0, output)
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'pass')
        data = workflow.load(current)
        data['engine']['sha256'] = 'different engine'
        workflow.save(current, data)
        status, output = self.reused(current, prior, observation, ['--allow-helper-change'])
        self.assertEqual(status, 2)
        self.assertIn('Engine version/build', output)

    def test_failed_observation_changed_requirement_and_failed_checks_rejected(self):
        prior = self.new_run()
        failed = self.acquired(prior, outcome='fail')
        status, _ = self.reused(self.new_run(), prior, failed)
        self.assertEqual(status, 2)
        passing = self.acquired(prior)
        scenario = dict(self.scenario, expected='A materially different expectation')
        status, output = self.reused(self.new_run(scenario=scenario), prior, passing)
        self.assertEqual(status, 2)
        self.assertIn('requirement changed', output)
        status, output = self.reused(self.new_run(outcome='fail'), prior, passing)
        self.assertEqual(status, 2)
        self.assertIn('Current required checks must pass', output)

    def test_mutated_capture_or_original_record_blocks_reuse_chain(self):
        prior = self.new_run()
        observation = self.acquired(prior)
        current = self.new_run()
        status, output = self.reused(current, prior, observation)
        self.assertEqual(status, 0, output)
        self.capture.write_bytes(b'changed pixels')
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'blocked')
        self.capture.write_bytes(b'observed pixels')
        original = workflow.load(observation)
        original['actual'] = 'Rewritten acquisition claim'
        workflow.save(observation, original)
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'blocked')

    def test_transitive_reuse_keeps_original_time_and_validates_every_link(self):
        first = self.new_run()
        original = self.acquired(first)
        second = self.new_run()
        status, output = self.reused(second, first, original)
        self.assertEqual(status, 0, output)
        second_observation = Path(output.strip())
        third = self.new_run()
        status, output = self.reused(third, second, second_observation)
        self.assertEqual(status, 0, output)
        self.assertEqual(workflow.load(output.strip())['acquired_at'], 1000)
        self.assertEqual(workflow.summarize_record(third)['outcome'], 'pass')
        original.unlink()
        self.assertEqual(workflow.summarize_record(third)['outcome'], 'blocked')

    def test_legacy_observation_reuses_full_source_without_inventing_acquisition_time(self):
        prior = self.new_run()
        original = self.acquired(prior)
        data = workflow.load(original)
        for key in ('kind', 'acquired_at', 'recorded_at', 'dependencies', 'dependency_scope', 'acquisition_time_basis'):
            data.pop(key, None)
        workflow.save(original, data)
        current = self.new_run()
        status, output = self.reused(current, prior, original)
        self.assertEqual(status, 0, output)
        reused = workflow.load(output.strip())
        self.assertEqual(reused['acquired_at'], data['created_at'])
        self.assertEqual(reused['acquisition_time_basis'], 'legacy_recording_time')
        self.assertEqual(reused['dependency_scope'], 'all_source')

    def test_variant_mutation_is_not_hidden_by_reuse(self):
        variant = self.root / 'variant'
        variant.mkdir()
        (variant / 'project.godot').write_text('[application]\nconfig/name="Variant"\n')
        prior = self.new_run()
        observation = self.acquired(prior, variant=variant)
        current = self.new_run()
        status, output = self.reused(current, prior, observation)
        self.assertEqual(status, 0, output)
        (variant / 'new.gd').write_text('extends Node\n')
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'blocked')

    def test_native_unicode_diagnostics_fail_zero_exit_but_mentions_do_not(self):
        messages = ['Unicode parsing error: Invalid unicode codepoint (25cf)',
                    'Unicode parsing error, some characters were replaced: Invalid UTF-8 leading byte (ff)']
        for index, message in enumerate(messages):
            process = workflow.run_process([__import__('sys').executable, '-c', 'print(' + repr(message) + ')'],
                                            self.root, self.root / ('unicode-%d.log' % index), 5)
            self.assertEqual(process['raw_exit_code'], 0)
            self.assertEqual(workflow.process_outcome(process), 'fail')
            self.assertIn(message, process['diagnostics'])
        self.assertFalse(workflow.DIAGNOSTIC.search('INFO: Documentation mentions Unicode parsing error: as an example'))

    def test_reuse_does_not_discard_sibling_failures_or_errors(self):
        for outcome in ('fail', 'error'):
            with self.subTest(outcome=outcome):
                prior = self.new_run()
                self.acquired(prior, outcome=outcome)
                passing = self.acquired(prior)
                status, output = self.reused(self.new_run(), prior, passing)
                self.assertEqual(status, 2)
                self.assertIn('unresolved failures or errors', output)

    def test_reuse_does_not_discard_unresolved_previous_attempt(self):
        first = self.new_run(outcome='fail')
        prior = self.new_run()
        data = workflow.load(prior)
        data['previous_run'] = str(first)
        workflow.save(prior, data)
        passing = self.acquired(prior)
        status, output = self.reused(self.new_run(), prior, passing)
        self.assertEqual(status, 2)
        self.assertIn('unresolved failures or errors', output)
        data['resolution'] = 'Corrected the failed scene contract; affected check reran in this run'
        workflow.save(prior, data)
        status, output = self.reused(self.new_run(), prior, passing)
        self.assertEqual(status, 0, output)

    def test_failure_added_to_origin_after_reuse_blocks_current_summary(self):
        prior = self.new_run()
        original = self.acquired(prior)
        current = self.new_run()
        status, output = self.reused(current, prior, original)
        self.assertEqual(status, 0, output)
        self.acquired(prior, outcome='fail')
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'blocked')

    def test_invalid_kind_scope_or_null_dependency_cannot_pass_or_reuse(self):
        for mutation in ({'kind': 'reuse_typo'}, {'dependency_scope': 'not-a-scope'},
                         {'dependency_scope': 'files', 'dependencies': {'nonexistent.gd': None}}):
            with self.subTest(mutation=mutation):
                prior = self.new_run()
                observation = self.acquired(prior)
                data = workflow.load(observation)
                data.update(mutation)
                workflow.save(observation, data)
                self.assertEqual(workflow.summarize_record(prior)['outcome'], 'blocked')
                status, output = self.reused(self.new_run(), prior, observation)
                self.assertEqual(status, 2, output)

    def test_shared_reuse_history_is_linear_and_later_failures_remain_visible(self):
        from unittest import mock
        prior = None
        for layer in range(9):
            current = self.new_run()
            record = workflow.load(current)
            record['previous_run'] = str(prior) if prior else None
            workflow.save(current, record)
            if prior:
                for index in range(3):
                    workflow.save(current.parent / 'observations' / ('copy%d.json' % index),
                                  {'kind': 'reused', 'outcome': 'pass', 'derived_from': {'run': str(prior)}})
            prior = current
        with mock.patch.object(workflow, 'load', wraps=workflow.load) as reads:
            self.assertEqual(workflow.retained_failure_issues(current), [])
            self.assertLess(reads.call_count, 50, 'Shared origins should be read once per reconciliation')
        workflow.save(current.parent / 'observations/new-failure.json', {'outcome': 'fail'})
        self.assertEqual(workflow.retained_failure_issues(current), ['fail'])

    def test_reused_origin_identity_metadata_cannot_contradict_original_record(self):
        prior = self.new_run()
        original = self.acquired(prior)
        current = self.new_run()
        status, output = self.reused(current, prior, original)
        self.assertEqual(status, 0, output)
        copy = Path(output.strip())
        data = workflow.load(copy)
        data['derived_from']['source_digest'] = 'contradictory source identity'
        workflow.save(copy, data)
        self.assertEqual(workflow.summarize_record(current)['outcome'], 'blocked')

    def test_source_inventory_rejects_fifo_before_hashing_it(self):
        import os
        if not hasattr(os, 'mkfifo'):
            self.skipTest('FIFO is unavailable on this platform')
        os.mkfifo(self.project / 'unexpected.pipe')
        with self.assertRaisesRegex(ValueError, 'Non-regular source'):
            workflow.source_manifest(self.project)
