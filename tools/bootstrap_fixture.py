#!/usr/bin/env python3
"""Fetch the locked GUT addon into the ignored fixture cache; never alter games."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def addon_hash(directory):
    if not directory.is_dir() or directory.is_symlink() or any(p.is_symlink() for p in directory.rglob('*')):
        raise ValueError('Fixture GUT must be a real directory without symlinks')
    files = {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(directory.rglob('*')) if p.is_file()}
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def verify_addon(directory, pin):
    if addon_hash(directory) != pin['addon_tree_sha256']:
        raise ValueError('Fixture GUT content differs from the locked dependency; reconcile the cache before continuing')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Use an existing checkout of the locked commit')
    args = parser.parse_args()
    pin = json.loads((ROOT / 'validation/dependencies.json').read_text())['gut']
    dest = ROOT / 'validation/fixture/addons/gut'
    if dest.exists() or dest.is_symlink():
        verify_addon(dest, pin)
        print('Fixture addon content verified against the locked dependency.')
        return
    with tempfile.TemporaryDirectory(prefix='godot-workflows-gut-') as tmp:
        checkout = args.source.resolve() if args.source else Path(tmp) / 'gut'
        if not args.source:
            subprocess.run(['git', 'clone', '--depth', '1', '--branch', pin['tag'], pin['repository'], str(checkout)], check=True)
        commit = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        dirty = subprocess.check_output(['git', '-C', str(checkout), 'status', '--porcelain'], text=True).strip()
        if commit != pin['commit'] or dirty:
            raise SystemExit('GUT checkout differs from the clean locked commit')
        staged = Path(tmp) / 'verified-addon'
        shutil.copytree(checkout / 'addons/gut', staged)
        for name in ('LICENSE', 'LICENSE.md', 'LICENSE.txt'):
            if (checkout / name).is_file() and not (staged / name).exists():
                shutil.copy2(checkout / name, staged / name)
        verify_addon(staged, pin)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staged, dest)
        print('Fixture GUT pinned at ' + commit)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc))
