#!/usr/bin/env python3
"""Refresh research-derived references from a deliberately selected research root."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def refined_topics(topics, refinements):
    """Apply maintained additions without changing the historical research input."""
    result = copy.deepcopy(topics)
    by_id = {topic['id']: topic for topic in result}
    if refinements.get('format_version') != 1:
        raise ValueError('Unsupported topic refinement format')
    for topic_id, changes in refinements.get('topics', {}).items():
        if topic_id not in by_id:
            raise ValueError('Unknown refinement topic: ' + topic_id)
        topic = by_id[topic_id]
        for field, value in changes.items():
            if field in ('native_types', 'verification') and isinstance(value, list):
                topic[field] = copy.deepcopy(value)
            elif field in ('pitfalls_append', 'verification_append') and isinstance(value, list):
                topic[field.removesuffix('_append')].extend(value)
            elif field == 'approach_append' and isinstance(value, str):
                topic['native_workflow'] += '\n\n' + value
            elif field == 'sources_append' and isinstance(value, list):
                topic['refinement_sources'] = copy.deepcopy(value)
            else:
                raise ValueError('Unsupported refinement field: ' + topic_id + '.' + field)
    return result


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def refresh(source):
    coverage = json.loads((source / 'godot-feature-coverage-research/coverage.json').read_text())
    refinements = json.loads((ROOT / 'provenance/topic-refinements.json').read_text())
    topics = refined_topics(coverage['topics'], refinements)
    inputs = [
        'godot-feature-coverage-research/coverage.json',
        'godot-feature-coverage-research/sources.json',
        'godot-agent-workflow-proposal/rule-mapping.json',
        'godot-research-pack/candidate-rules.json',
        'godot-research-pack/resources.json',
        'godot-agent-workflow-research/avenues/03-sources.json',
        'godot-agent-workflow-research/recommendations.json',
        'godot-agent-workflow-research/sources.json',
    ]
    manifest = []
    for relative in inputs:
        raw = (source / relative).read_bytes()
        manifest.append({'research_path': relative, 'sha256': hashlib.sha256(raw).hexdigest()})
    write_json(ROOT / 'provenance/manifest.json', {
        'research_date': '2026-10-15', 'inputs': manifest,
        'origin': 'godot-research; retained separately from the implementation',
        'refresh_command': 'python3 tools/import_research.py /path/to/godot-research',
    })
    coverage = json.loads((source / inputs[0]).read_text())
    sources = json.loads((source / inputs[1]).read_text())['sources']
    source_map = {s['id']: s for s in sources}
    rules = json.loads((source / inputs[2]).read_text())['rules']
    rule_sources = {'pack:' + s['id']: s for s in json.loads((source / inputs[4]).read_text())['sources']}
    rule_sources.update({'workflow:' + s['id']: s for s in json.loads((source / inputs[5]).read_text())})
    recommendations = json.loads((source / inputs[6]).read_text())['recommendations']
    workflow_sources = {s['id']: s for s in json.loads((source / inputs[7]).read_text())['sources']}
    rec_text = ['# Research recommendations\n\nEditorial syntheses, not installed policy.\n']
    for rec in recommendations:
        rule_sources['workflow:' + rec['id']] = {'url': 'research-recommendations.md#' + rec['id'].lower()}
        rec_text.append('## ' + rec['id'] + '\n\n' + rec['practice'] + '. '
                        + rec['recommendation_and_conditions'] + '\n\nEvidence: '
                        + ', '.join('[' + sid + '](' + workflow_sources[sid]['url'] + ')'
                                    for sid in rec['evidence_source_ids']) + '.\n')
    (ROOT / 'references/research-recommendations.md').write_text('\n'.join(rec_text))
    write_json(ROOT / 'references/rules.json', {
        'default': 'advisory until explicitly adopted by a game', 'rules': rules})
    write_json(ROOT / 'references/coverage-limitations.json', coverage['coverage_backlog'])
    write_json(ROOT / 'provenance/feature-sources.json', sources)
    write_json(ROOT / 'provenance/rule-sources.json', {
        'pack': json.loads((source / inputs[4]).read_text()),
        'workflow': json.loads((source / inputs[5]).read_text())})
    rules_text = ['# Candidate Godot policy\n\nAll 50 research treatments are preserved. '
                  'They are advisory until a game explicitly adopts a named requirement. '
                  'Research strength labels are not installed policy.\n']
    for r in rules:
        rules_text.append('## {rule_id} — {statement}\n\nTreatment: `{primary_treatment}`. '
                          '{rationale}\n\nException: {preserved_exception}\n\nEvidence: '.format(**r)
                          + ', '.join(r['check_ids']) + '. Sources: '
                          + ', '.join('[' + sid + '](' + rule_sources[sid]['url'] + ')'
                                      for sid in r['source_refs']) + '.\n')
    (ROOT / 'references/policy.md').write_text('\n'.join(rules_text))
    topic_root = ROOT / 'references/topics'
    topic_root.mkdir(exist_ok=True)
    index = ['# Native Godot topic index\n\nMatch user intent, then open only relevant briefs. '
             'This is a discovery index, not a required feature checklist. '
             'Use [official discovery](../discovery.md) for gaps and research boundaries.\n',
             '| Topic | User-visible trigger |\n| --- | --- |']
    for t in topics:
        index.append('| [{id} — {title}]({id}.md) | {trigger} |'.format(**t))
        body = ['# {id} — {title}\n\nWhen: {trigger}\n\nNative candidates: '.format(**t)
                + ', '.join('`' + n + '`' for n in t['native_types']) + '.',
                '## Approach\n\n' + t['native_workflow'], t['avoid_reimplementation'],
                '## Pitfalls\n\n' + '\n'.join('- ' + p for p in t['pitfalls']),
                '## Verify\n\n' + '\n'.join('- ' + p for p in t['verification']),
                '## Version and limits\n\n' + t['version_notes']]
        if t['id'] in ('SH-09', 'SH-11', 'SH-12'):
            body.append('Untrusted content or security-sensitive protocols require '
                        'the threat-/protocol-specific follow-up in '
                        '[discovery](../discovery.md). A topic match does not discharge it. '
                        'Trusted project-authored assets do not automatically activate that branch.')
        if t['id'] == 'XR-01' or t['id'].startswith('ED-'):
            body.append('Specialist/target behavior needs project-specific research and calibration; '
                        'also read [coverage boundaries](../discovery.md).')
        body.append('## Primary sources\n')
        for sid in t['source_ids']:
            s = source_map[sid]
            body.append('- [{id}: {title}]({url}). Scope/limits: {limitations}'.format(**s))
        for extra in t.get('refinement_sources', []):
            body.append('- [{title}]({url}). Scope/limits: {limits}'.format(**extra))
        (topic_root / (t['id'] + '.md')).write_text('\n\n'.join(body) + '\n')
    (topic_root / 'index.md').write_text('\n'.join(index) + '\n')
    print('Preserved {} rule treatments and generated {} topic briefs.'.format(len(rules), len(coverage['topics'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('research_root', type=Path)
    refresh(parser.parse_args().research_root.resolve())
