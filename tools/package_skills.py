#!/usr/bin/env python3
"""Build standalone skills; install owned generated files into the personal Skills repo."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = '.godot-workflows-package.json'


def hashes(directory):
    if any(p.is_symlink() for p in directory.rglob('*')):
        raise ValueError('Symlinked package files need explicit reconciliation')
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob('*')) if p.is_file() and p.name != MANIFEST}


def validate_links(directory):
    problems = []
    for page in directory.rglob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)', page.read_text()):
            link = unquote(link.split('#')[0].strip('<>'))
            if not link or re.match(r'^[a-z]+:', link):
                continue
            target = (page.parent / link).resolve()
            if not target.is_relative_to(directory.resolve()) or not target.exists():
                problems.append(str(page.relative_to(directory)) + ': ' + link)
    if problems:
        raise ValueError('Broken/nonportable links: ' + '; '.join(problems))


def build(output):
    if output.exists():
        raise ValueError('Build output must be a new directory: ' + str(output))
    output.mkdir(parents=True)
    metadata = json.loads((ROOT / 'toolkit.json').read_text())
    for name in metadata['skills']:
        dest = output / name
        shutil.copytree(ROOT / 'skills' / name, dest)
        shutil.copytree(ROOT / 'references', dest / 'references')
        shutil.copytree(ROOT / 'templates', dest / 'templates')
        (dest / 'scripts').mkdir(exist_ok=True)
        shutil.copy2(ROOT / 'tools/godot_workflow.py', dest / 'scripts/godot_workflow.py')
        validate_links(dest)
        (dest / MANIFEST).write_text(json.dumps({
            'generator': 'godot-workflows', 'version': metadata['version'],
            'source': 'godot-workflows toolkit; edit sources and regenerate',
            'files': hashes(dest)}, indent=2) + '\n')
    return metadata['skills']


def install(packages, skills_repo, apply=False):
    if not (skills_repo / 'scripts/skills.js').is_file() or not (skills_repo / 'skills.json').is_file():
        raise ValueError('Expected personal Skills manager repository')
    plan = []
    for source in sorted(packages.iterdir()):
        if not source.is_dir():
            continue
        metadata = json.loads((source / MANIFEST).read_text())
        if hashes(source) != metadata['files']:
            raise ValueError('Package files changed after build: ' + source.name)
        validate_links(source)
        dest = skills_repo / 'local' / source.name
        if dest.is_symlink():
            raise ValueError('Destination is a symlink: ' + str(dest))
        if dest.exists():
            owned = dest / MANIFEST
            if not owned.is_file():
                raise ValueError('Existing destination is not owned by this generator: ' + str(dest))
            previous = json.loads(owned.read_text())
            if previous.get('generator') != 'godot-workflows' or hashes(dest) != previous['files']:
                raise ValueError('Generated destination has local edits; reconcile before updating: ' + str(dest))
        plan.append((source, dest))
    # Preflight every destination before the first write.
    if apply:
        for source, dest in plan:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.godot-workflows-stage-', dir=str(dest.parent)) as tmp:
                staged = Path(tmp) / dest.name
                shutil.copytree(source, staged)
                backup = Path(tmp) / 'previous'
                if dest.exists():
                    dest.rename(backup)
                try:
                    staged.rename(dest)
                except OSError:
                    if backup.exists():
                        backup.rename(dest)
                    raise
    return {'applied': apply, 'destinations': [str(d) for _, d in plan],
            'activation': ['npm run enable -- local/' + s.name for s, _ in plan]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    b = sub.add_parser('build')
    b.add_argument('--output', type=Path)
    i = sub.add_parser('install')
    i.add_argument('--packages', required=True, type=Path)
    i.add_argument('--skills-repo', required=True, type=Path)
    i.add_argument('--apply', action='store_true')
    args = p.parse_args()
    try:
        if args.command == 'build':
            output = (args.output or ROOT / 'dist' / ('skills-' + __import__('uuid').uuid4().hex[:8])).resolve()
            print(json.dumps({'output': str(output), 'skills': build(output)}, indent=2))
        else:
            print(json.dumps(install(args.packages.resolve(), args.skills_repo.resolve(), args.apply), indent=2))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print('Package error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
