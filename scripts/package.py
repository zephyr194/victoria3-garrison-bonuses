"""Build version-specific development packages, blocking unverified stable releases."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=['1.13', '1.14'], required=True)
    parser.add_argument('--experimental', action='store_true')
    args = parser.parse_args()
    status = json.loads((ROOT / 'compatibility.json').read_text())['targets'][args.target]
    if not status['game_verified'] and not args.experimental:
        parser.error('No game verification recorded; only --experimental packaging is permitted')
    subprocess.run([sys.executable, str(ROOT / 'tools/validate.py')], check=True)
    version = json.loads((ROOT / 'balance.json').read_text())['mod_version']
    suffix = '-experimental' if args.experimental else ''
    descriptor = f'''name="Garrison Bonuses {args.target}{suffix}"
version="{version}{suffix}"
supported_version="{args.target}.*"
path="mod/gs_garrison"
tags={{ "Gameplay" "Military" }}
'''
    destination = ROOT / f'dist/gs-garrison-{args.target}{suffix}.zip'
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('gs_garrison.mod', descriptor)
        archive.writestr('gs_garrison/descriptor.mod', descriptor.replace('path="mod/gs_garrison"\n', ''))
        for file in sorted((ROOT / 'mod').rglob('*')):
            if file.is_file():
                archive.write(file, Path('gs_garrison') / file.relative_to(ROOT / 'mod'))
        archive.write(ROOT / 'docs/INSTALL_TEST.md', 'README-EXPERIMENTAL.md')
    print(destination)

if __name__ == '__main__':
    main()
