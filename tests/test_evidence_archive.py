import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


workflow = module('archive_workflow', ROOT / 'tools/godot_workflow.py')
archive = module('archive_helper', ROOT / 'tools/evidence_archive.py')


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='godot-archive-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / 'game'
        self.project.mkdir()
        (self.project / 'project.godot').write_text('[application]\nconfig/name="Archive"\n')
        (self.project / 'ship.gd').write_text('extends Node2D\n')
        self.output = self.root / 'bundle'

    def run_record(self, name='current', previous=None):
        directory = self.root / 'attempts' / name
        directory.mkdir(parents=True)
        log = directory / 'parse.log'
        log.write_text('Parsed cleanly\n')
        report = directory / 'junit.xml'
        report.write_text('<testsuite><testcase name="test_play"/></testsuite>\n')
        data = {'format_version': 1, 'run_id': name, 'project': str(self.project),
                'source': workflow.source_manifest(self.project), 'helper_sha256': 'a' * 64,
                'results': {'parse': {'outcome': 'pass', 'processes': [
                    {'command': ['/historical/Godot', '--path', '/historical/project'],
                     'log': str(log), 'log_sha256': workflow.digest(log)}]},
                    'tests': {'outcome': 'pass', 'report': str(report), 'report_sha256': workflow.digest(report)}},
                'previous_run': str(previous) if previous else None}
        path = directory / 'run.json'
        workflow.save(path, data)
        return path, data

    def observation(self, run, data, name='play', derived=None):
        capture = run.parent / 'captures' / (name + '.png')
        capture.parent.mkdir(exist_ok=True)
        capture.write_bytes(b'captured pixels')
        observation = {'id': name, 'run_id': data['run_id'], 'source_digest': data['source']['digest'],
                       'outcome': 'pass', 'created_at': 1234, 'scene': 'res://main.tscn',
                       'observer': 'Fixture observer', 'sequence': 'Launch, move, pause',
                       'artifacts': [{'path': str(capture), 'sha256': workflow.digest(capture)}]}
        if derived:
            prior_run, prior_data, prior_observation = derived
            observation['derived_from'] = {
                'run': str(prior_run), 'run_sha256': workflow.digest(prior_run),
                'observation': str(prior_observation), 'observation_sha256': workflow.digest(prior_observation),
                'source_digest': prior_data['source']['digest'], 'helper_sha256': prior_data['helper_sha256']}
        path = run.parent / 'observations' / (name + '.json')
        workflow.save(path, observation)
        return path, observation

    def read_manifest(self):
        return json.loads((self.output / archive.MANIFEST).read_text())

    def write_manifest(self, data):
        workflow.save(self.output / archive.MANIFEST, data)

    def test_bundle_survives_deleting_originals_and_moving_with_verbatim_records(self):
        prior, _ = self.run_record('prior')
        current, data = self.run_record(previous=prior)
        observation, _ = self.observation(current, data)
        run_bytes, observation_bytes = current.read_bytes(), observation.read_bytes()
        result = archive.archive_run(current, self.output, workflow)
        self.assertEqual(result['runs'], 2)
        manifest = self.read_manifest()
        self.assertEqual((self.output / manifest['runs'][str(current)]['record']).read_bytes(), run_bytes)
        self.assertEqual((self.output / manifest['observations'][str(observation)]['record']).read_bytes(), observation_bytes)
        shutil.rmtree(self.project)
        shutil.rmtree(self.root / 'attempts')
        moved = self.root / 'moved'
        self.output.rename(moved)
        # Verification is independent of the helper version and original roots.
        with mock.patch.object(workflow, 'source_manifest', side_effect=AssertionError('must not read source')):
            result = archive.verify_archive(moved, workflow)
        self.assertEqual(result['outcome'], 'pass')
        self.assertEqual(result['historical_integrity'], 'verified')
        self.assertFalse(result['current_project_acceptance'])

    def test_missing_or_changed_required_files_reject_and_remove_partial_output(self):
        for kind in ('log', 'report', 'capture', 'prior'):
            with self.subTest(kind=kind):
                prior, _ = self.run_record('prior-' + kind)
                current, data = self.run_record('current-' + kind, prior)
                _, observation = self.observation(current, data)
                target = {'log': current.parent / 'parse.log', 'report': current.parent / 'junit.xml',
                          'capture': Path(observation['artifacts'][0]['path']), 'prior': prior}[kind]
                target.unlink()
                with self.assertRaises((ValueError, OSError)):
                    archive.archive_run(current, self.output, workflow)
                self.assertFalse(self.output.exists())
                target.write_text('Mutated bytes')
                with self.assertRaises((ValueError, OSError)):
                    archive.archive_run(current, self.output, workflow)
                self.assertFalse(self.output.exists())

    def test_changed_candidate_retains_old_manifest_without_substituting_new_source(self):
        current, data = self.run_record()
        original = data['source']
        (self.project / 'ship.gd').write_text('extends Area2D\n')
        result = archive.archive_run(current, self.output, workflow)
        snapshot = self.read_manifest()['runs'][str(current)]['snapshots']['candidate']
        self.assertEqual(snapshot['status'], 'unavailable')
        self.assertEqual(snapshot['recorded_manifest'], original)
        self.assertEqual(snapshot['files'], {})
        self.assertEqual(len(result['unavailable_source_snapshots']), 1)

    def test_missing_historical_project_is_a_declared_snapshot_limit(self):
        current, _ = self.run_record()
        shutil.rmtree(self.project)
        result = archive.archive_run(current, self.output, workflow)
        self.assertEqual(result['outcome'], 'pass')
        self.assertTrue(result['unavailable_source_snapshots'])

    def test_changed_raw_task_retains_embedded_task_and_original_hash(self):
        current, data = self.run_record()
        task = self.root / 'task.json'
        workflow.save(task, {'required_checks': ['parse']})
        data.update(task_path=str(task), task_sha256=workflow.digest(task), task=workflow.load(task))
        original_task = data['task']
        workflow.save(current, data)
        workflow.save(task, {'required_checks': ['parse', 'tests']})
        result = archive.archive_run(current, self.output, workflow)
        manifest = self.read_manifest()
        raw = manifest['runs'][str(current)]['raw_task']
        self.assertEqual(raw['status'], 'unavailable')
        self.assertEqual(raw['recorded_sha256'], data['task_sha256'])
        self.assertNotIn(str(task), manifest['inputs'])
        archived_run = json.loads((self.output / manifest['runs'][str(current)]['record']).read_text())
        self.assertEqual(archived_run['task'], original_task)
        self.assertEqual(len(result['unavailable_raw_tasks']), 1)

    def test_missing_raw_task_without_embedded_task_rejects(self):
        current, data = self.run_record()
        data.update(task_path=str(self.root / 'absent-task.json'), task_sha256='a' * 64)
        workflow.save(current, data)
        with self.assertRaisesRegex(ValueError, 'without an embedded task'):
            archive.archive_run(current, self.output, workflow)

    def test_matching_raw_task_retained_and_verified_after_original_removed(self):
        current, data = self.run_record()
        task = self.root / 'task.json'
        workflow.save(task, {'required_checks': ['parse']})
        data.update(task_path=str(task), task_sha256=workflow.digest(task), task=workflow.load(task))
        workflow.save(current, data)
        archive.archive_run(current, self.output, workflow)
        self.assertEqual(self.read_manifest()['runs'][str(current)]['raw_task']['status'], 'retained')
        task.unlink()
        self.assertEqual(archive.verify_archive(self.output)['unavailable_raw_tasks'], [])

    def test_observation_variant_retained_only_at_recorded_digest(self):
        current, data = self.run_record()
        observation, record = self.observation(current, data)
        variant = self.root / 'variant'
        shutil.copytree(self.project, variant)
        (variant / 'ship.gd').write_text('extends Area2D\n')
        record['variant_root'] = str(variant)
        record['variant_source'] = workflow.source_manifest(variant)
        record['variant_digest'] = record['variant_source']['digest']
        workflow.save(observation, record)
        archive.archive_run(current, self.output, workflow)
        snapshot = self.read_manifest()['observations'][str(observation)]['variant_snapshot']
        self.assertEqual(snapshot['status'], 'retained')
        self.assertEqual((self.output / snapshot['files']['ship.gd']).read_text(), 'extends Area2D\n')

    def test_reuse_chain_outside_previous_history_is_retained_transitively(self):
        origin, origin_data = self.run_record('origin')
        origin_obs, _ = self.observation(origin, origin_data)
        middle, middle_data = self.run_record('middle')
        middle_obs, _ = self.observation(middle, middle_data, derived=(origin, origin_data, origin_obs))
        current, data = self.run_record()
        self.observation(current, data, derived=(middle, middle_data, middle_obs))
        result = archive.archive_run(current, self.output, workflow)
        self.assertEqual(result['runs'], 3)
        self.assertEqual(result['observations'], 3)
        shutil.rmtree(self.root / 'attempts')
        self.assertEqual(archive.verify_archive(self.output)['runs'], 3)

    def test_changed_reuse_origin_run_or_observation_rejects(self):
        for item in ('run', 'observation'):
            with self.subTest(item=item):
                origin, origin_data = self.run_record('origin-' + item)
                origin_obs, _ = self.observation(origin, origin_data)
                current, data = self.run_record('current-' + item)
                self.observation(current, data, derived=(origin, origin_data, origin_obs))
                target = origin if item == 'run' else origin_obs
                target.write_text(target.read_text() + ' \n')
                with self.assertRaisesRegex(ValueError, 'Changed'):
                    archive.archive_run(current, self.output, workflow)

    def test_attempt_cycle_rejects_archival(self):
        first, first_data = self.run_record('first')
        second, _ = self.run_record('second', first)
        first_data['previous_run'] = str(second)
        workflow.save(first, first_data)
        with self.assertRaisesRegex(ValueError, 'Cycle'):
            archive.archive_run(second, self.output, workflow)

    def test_symlinked_input_parent_capture_source_and_output_rejected(self):
        current, data = self.run_record()
        _, record = self.observation(current, data)
        capture = Path(record['artifacts'][0]['path'])
        target = self.root / 'outside.png'
        capture.rename(target)
        capture.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            archive.archive_run(current, self.output, workflow)
        capture.unlink()
        target.rename(capture)
        (self.project / 'external.gd').symlink_to(self.project / 'ship.gd')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            archive.archive_run(current, self.output, workflow)
        (self.project / 'external.gd').unlink()
        link = self.root / 'alias'
        link.symlink_to(current.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            archive.archive_run(link / 'run.json', self.output, workflow)
        outlink = self.root / 'outlink'
        outlink.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            archive.archive_run(current, outlink / 'new', workflow)

    def test_output_must_be_new_and_outside_source(self):
        current, _ = self.run_record()
        with self.assertRaisesRegex(ValueError, 'outside'):
            archive.archive_run(current, self.project / 'archive', workflow)
        self.output.mkdir()
        (self.output / 'keep').write_text('owned by someone else')
        with self.assertRaisesRegex(ValueError, 'new directory'):
            archive.archive_run(current, self.output, workflow)
        self.assertEqual((self.output / 'keep').read_text(), 'owned by someone else')

    def test_verification_rejects_mutated_blob_and_missing_inventory(self):
        current, _ = self.run_record()
        archive.archive_run(current, self.output, workflow)
        manifest = self.read_manifest()
        blob = self.output / next(iter(manifest['files']))
        blob.write_bytes(blob.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'Changed archived content'):
            archive.verify_archive(self.output)
        blob.unlink()
        with self.assertRaisesRegex(ValueError, 'inventory'):
            archive.verify_archive(self.output)

    def test_verification_rejects_traversal_symlinks_and_omitted_required_inputs(self):
        current, _ = self.run_record()
        archive.archive_run(current, self.output, workflow)
        manifest = self.read_manifest()
        original = json.loads(json.dumps(manifest))
        value = manifest['inputs'].pop(str(current.parent / 'parse.log'))
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'input'):
            archive.verify_archive(self.output)
        manifest = json.loads(json.dumps(original))
        manifest['runs'][str(current)]['record'] = '../escape.json'
        manifest['inputs'][str(current)] = '../escape.json'
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'portable reference'):
            archive.verify_archive(self.output)
        self.write_manifest(original)
        blob = self.output / value
        external = self.root / 'external'
        blob.rename(external)
        blob.symlink_to(external)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            archive.verify_archive(self.output)

    def test_manifest_source_traversal_rejected_without_copying(self):
        current, record = self.run_record()
        record['source']['files']['../escape.gd'] = 'a' * 64
        record['source']['digest'] = workflow.encoded_hash(record['source']['files'])
        workflow.save(current, record)
        with self.assertRaisesRegex(ValueError, 'portable reference'):
            archive.archive_run(current, self.output, workflow)

    def test_retained_observation_cannot_disappear_from_graph_indices(self):
        current, data = self.run_record()
        observation, record = self.observation(current, data)
        record['outcome'] = 'fail'
        workflow.save(observation, record)
        archive.archive_run(current, self.output, workflow)
        manifest = self.read_manifest()
        manifest['runs'][str(current)]['observations'] = []
        manifest['observations'] = {}
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'Retained observation inputs'):
            archive.verify_archive(self.output)
        # Removing the now-unvisited capture must not hide the retained failed
        # observation and its still-recorded required capture reference.
        capture = record['artifacts'][0]['path']
        reference = manifest['inputs'].pop(capture)
        manifest['files'].pop(reference)
        (self.output / reference).unlink()
        manifest['runs'][str(current)]['supplemental'] = [
            extra for extra in manifest['runs'][str(current)]['supplemental'] if extra['original_path'] != capture]
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'Retained observation inputs'):
            archive.verify_archive(self.output)

    def test_previous_attempt_cannot_disappear_from_graph_index(self):
        prior, _ = self.run_record('prior')
        current, _ = self.run_record(previous=prior)
        archive.archive_run(current, self.output, workflow)
        manifest = self.read_manifest()
        del manifest['runs'][str(prior)]
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'attempt history'):
            archive.verify_archive(self.output)

    def test_retained_observation_blob_cannot_become_an_unmapped_orphan(self):
        current, data = self.run_record()
        observation, record = self.observation(current, data)
        archive.archive_run(current, self.output, workflow)
        manifest = self.read_manifest()
        manifest['runs'][str(current)]['observations'] = []
        manifest['observations'] = {}
        manifest['inputs'].pop(str(observation))
        capture = record['artifacts'][0]['path']
        reference = manifest['inputs'].pop(capture)
        manifest['files'].pop(reference)
        (self.output / reference).unlink()
        manifest['runs'][str(current)]['supplemental'] = [
            extra for extra in manifest['runs'][str(current)]['supplemental'] if extra['original_path'] != capture]
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'Retained files differ from original input inventory'):
            archive.verify_archive(self.output)

    def test_output_inside_any_earlier_run_directory_rejects_before_scanning_itself(self):
        prior, _ = self.run_record('prior')
        current, _ = self.run_record(previous=prior)
        captures = prior.parent / 'captures'
        captures.mkdir()
        output = captures / 'bundle'
        original_prior = prior.read_bytes()
        with self.assertRaisesRegex(ValueError, 'outside every historical run directory'):
            archive.archive_run(current, output, workflow)
        self.assertFalse(output.exists())
        self.assertTrue(captures.is_dir())
        self.assertEqual(prior.read_bytes(), original_prior)

    def test_retained_supplemental_input_cannot_disappear_from_run_inventory(self):
        current, _ = self.run_record()
        acquisition = current.parent / 'editor.log'
        acquisition.write_text('Editor opened\n')
        archive.archive_run(current, self.output, workflow)
        manifest = self.read_manifest()
        manifest['runs'][str(current)]['supplemental'] = [
            extra for extra in manifest['runs'][str(current)]['supplemental'] if extra['original_path'] != str(acquisition)]
        self.write_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'Retained supplemental inputs'):
            archive.verify_archive(self.output)

    def test_dangling_supplemental_log_symlink_rejects_archival(self):
        current, _ = self.run_record()
        (current.parent / 'lost-acquisition.log').symlink_to(current.parent / 'nonexistent.log')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            archive.archive_run(current, self.output, workflow)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO fixture requires POSIX')
    def test_special_source_file_rejects_before_hashing_source(self):
        current, _ = self.run_record()
        os.mkfifo(self.project / 'unexpected.pipe')
        with mock.patch.object(workflow, 'source_manifest', side_effect=AssertionError('must not read FIFO')):
            with self.assertRaisesRegex(ValueError, 'Special source file'):
                archive.archive_run(current, self.output, workflow)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO fixture requires POSIX')
    def test_special_unindexed_archive_file_rejects(self):
        current, _ = self.run_record()
        archive.archive_run(current, self.output, workflow)
        os.mkfifo(self.output / 'unexpected.pipe')
        with self.assertRaisesRegex(ValueError, 'Special archive file'):
            archive.verify_archive(self.output)


if __name__ == '__main__':
    unittest.main()
