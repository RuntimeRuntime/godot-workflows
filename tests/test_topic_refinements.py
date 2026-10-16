import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('import_research', ROOT / 'tools/import_research.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


class TopicRefinementTests(unittest.TestCase):
    def setUp(self):
        self.topics = [{'id': 'D2-01', 'native_types': ['TileMapLayer'],
                        'native_workflow': 'Use the chosen native workflow.',
                        'pitfalls': ['Keep intentional procedural content.'],
                        'verification': ['Inspect the saved result.']},
                       {'id': 'SH-03', 'native_types': ['InputEvent'],
                        'native_workflow': 'Use saved bindings.',
                        'pitfalls': [], 'verification': ['Exercise an action.']}]

    def test_appending_refinement_preserves_original_exceptions_and_source(self):
        original = copy.deepcopy(self.topics)
        result = importer.refined_topics(self.topics, {'format_version': 1, 'topics': {
            'D2-01': {'pitfalls_append': ['Composite may span cells.'],
                      'verification_append': ['Verify actual stamp.'],
                      'approach_append': 'Keep the authored footprint.'}}})
        self.assertEqual(self.topics, original)
        self.assertEqual(result[0]['pitfalls'], original[0]['pitfalls'] + ['Composite may span cells.'])
        self.assertEqual(result[0]['verification'], original[0]['verification'] + ['Verify actual stamp.'])
        self.assertEqual(result[1], original[1])

    def test_explicit_input_refinement_survives_repeated_generation(self):
        refinement = {'format_version': 1, 'topics': {'SH-03': {
            'native_types': ['InputEventKey'], 'verification': ['Inject fixed expected physical press and release.'],
            'sources_append': [{'title': 'InputEventKey', 'url': 'https://example.invalid/input',
                                'limits': 'Engine routing only.'}]}}}
        first = importer.refined_topics(self.topics, refinement)
        second = importer.refined_topics(self.topics, refinement)
        self.assertEqual(first, second)
        self.assertEqual(first[1]['native_types'], ['InputEventKey'])
        self.assertEqual(first[1]['verification'], refinement['topics']['SH-03']['verification'])
        self.assertEqual(first[1]['refinement_sources'], refinement['topics']['SH-03']['sources_append'])

    def test_unknown_topic_or_field_fails_instead_of_losing_a_refinement(self):
        for changes in [{'missing': {'verification_append': ['case']}},
                        {'D2-01': {'verificaton_append': ['case']}}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                importer.refined_topics(self.topics, {'format_version': 1, 'topics': changes})

    def test_unsupported_format_is_not_silently_imported(self):
        with self.assertRaises(ValueError):
            importer.refined_topics(self.topics, {'format_version': 2, 'topics': {}})


if __name__ == '__main__':
    unittest.main()
