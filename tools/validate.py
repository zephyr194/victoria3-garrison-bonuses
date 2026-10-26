"""Static structural checks, NOT validation of the Paradox engine schema."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]|[^\s{}#]+', text.lstrip('\ufeff'))
    depth = 0
    for token in tokens:
        if token.startswith('#'):
            continue
        depth += (token == '{') - (token == '}')
        if depth < 0:
            raise ValueError('Unexpected closing brace')
    if depth:
        raise ValueError('Unbalanced braces')


def main():
    subprocess.run([sys.executable, str(ROOT / 'tools/generate.py'), '--check'], check=True)
    count = 0
    definitions = {}
    references = set()
    for file in sorted((ROOT / 'mod/common').rglob('*.txt')):
        content = file.read_text(encoding='utf-8-sig')
        parse(content)
        for key in re.findall(r'^((?:gs_|building_gs_|pm_gs_|pmg_gs_)\w+)\s*=', content, re.M):
            if key in definitions:
                raise ValueError(f'Duplicate top-level definition: {key}')
            definitions[key] = file
        # Namespaced custom keys used as effect / trigger / numeric references.
        references.update(re.findall(r'\b(?:gs_|building_gs_|pm_gs_|pmg_gs_)\w+\b', re.sub(r'#[^\n]*', '', content)))
        count += 1
    runtime_vars = {'gs_service_months', 'gs_service_owner', 'gs_staff', 'gs_relief'}
    missing = references - definitions.keys() - runtime_vars
    if missing:
        raise ValueError('Unresolved custom keys: ' + ', '.join(sorted(missing)))
    for lang in ['simp_chinese', 'english']:
        file = ROOT / f'mod/localization/{lang}/gs_garrison_l_{lang}.yml'
        data = file.read_bytes()
        if not data.startswith(b'\xef\xbb\xbf'):
            raise ValueError('Localization requires UTF-8 BOM')
        keys = re.findall(r'^ (\w+):0 ', data.decode('utf-8-sig'), re.M)
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate localization keys')
        required = {x for x in definitions if x.startswith(('building_gs_', 'pm_gs_', 'pmg_gs_', 'gs_order_'))}
        if required - set(keys):
            raise ValueError('Missing localization: ' + ', '.join(required - set(keys)))
    print(f'{count} script files passed structural checks; engine loading remains untested')

if __name__ == '__main__':
    main()
