"""Check the initial documentation structure; this is not a software test suite."""
from pathlib import Path
import argparse
import re
import sys

REQUIRED_FILES = [
    'README.md', 'CONTRIBUTING.md', 'docs/README.md',
    'docs/governance/team.md', '.github/PULL_REQUEST_TEMPLATE.md',
]
TEMPLATES = {
    '01-user-story.md': ['用户故事', '验收标准', '补充说明'],
    '02-bug-report.md': ['问题描述', '复现步骤', '预期与实际', '验收'],
    '03-task.md': ['目标', '任务清单', '完成标准'],
    '04-change-request.md': ['变更内容', '影响范围', '评审结论', '实施检查'],
}

def check(root):
    errors = []
    def read(relative):
        path = root / relative
        if not path.is_file():
            errors.append(f'Missing file: {relative}')
            return None
        try:
            content = path.read_text(encoding='utf-8-sig')
        except UnicodeError:
            errors.append(f'Not UTF-8: {relative}')
            return None
        if not content.strip():
            errors.append(f'Empty file: {relative}')
        return content

    for relative in REQUIRED_FILES:
        read(relative)
    for filename, sections in TEMPLATES.items():
        relative = '.github/ISSUE_TEMPLATE/' + filename
        content = read(relative)
        if content is None:
            continue
        front = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', content, re.S)
        if not front:
            errors.append(f'Missing template frontmatter: {relative}')
        else:
            for key in ['name', 'about', 'title', 'labels']:
                if not re.search(rf'^{key}:\s*\S', front.group(1), re.M):
                    errors.append(f'Missing template metadata {key}: {relative}')
        headings = set(re.findall(r'^##\s+(.+?)\s*$', content, re.M))
        for section in sections:
            if section not in headings:
                errors.append(f'Missing section {section}: {relative}')
    return errors

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        print('\n'.join(errors))
        sys.exit(1)
    print('Documentation structure checks passed.')
