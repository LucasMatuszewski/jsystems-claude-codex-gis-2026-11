"""Trainer-only: sanitize a captured Jira search export, preserving its fields.

Raw inputs stay outside the repository. No network or credential access.
"""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import quote

UUID = r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}'
FAKE_CLOUD = '00000000-0000-0000-0000-000000000000'
AVATAR = 'https://example.invalid/avatar.png'


def inline(text):
    """Convert the inline subset used in the seeded descriptions, recursively."""
    nodes, pos = [], 0
    pattern = r'(`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|(?<!\w)_[^_\s](?:[^_]*?[^_\s])?_(?!\w)|\[[^\]]+\]\([^ )]+\))'
    for match in re.finditer(pattern, text):
        if match.start() > pos:
            nodes.append({'type': 'text', 'text': text[pos:match.start()]})
        token = match.group()
        if token.startswith('`'):
            children, mark = [{'type': 'text', 'text': token[1:-1]}], {'type': 'code'}
        elif token.startswith('['):
            label, href = token[1:].split('](', 1)
            children, mark = inline(label), {'type': 'link', 'attrs': {'href': href[:-1]}}
        else:
            width = 2 if token[:2] in ('**', '__') else 1
            children, mark = inline(token[width:-width]), {'type': 'strong' if width == 2 else 'em'}
        for child in children:
            child.setdefault('marks', []).append(mark)
        nodes.extend(children)
        pos = match.end()
    if pos < len(text):
        nodes.append({'type': 'text', 'text': text[pos:]})
    return nodes


def paragraph(text):
    content = []
    for index, line in enumerate(text.split('\n')):
        if index:
            content.append({'type': 'hardBreak'})
        content.extend(inline(line.rstrip()))
    return {'type': 'paragraph', 'content': content}


def markdown_to_adf(markdown):
    # The connector serialized literal backslash-n sequences into descriptions.
    markdown = markdown.replace(r'\n', '\n') if '\n' not in markdown else markdown
    lines, blocks, index = markdown.splitlines(), [], 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.lstrip().startswith('```'):
            language, code = line.strip()[3:].strip(), []
            index += 1
            while index < len(lines) and not lines[index].lstrip().startswith('```'):
                code.append(lines[index]); index += 1
            block = {'type': 'codeBlock'}
            if language:
                block['attrs'] = {'language': language}
            if code:
                block['content'] = [{'type': 'text', 'text': '\n'.join(code)}]
            blocks.append(block); index += 1
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)$', line)
        if heading:
            blocks.append({'type': 'heading', 'attrs': {'level': len(heading[1])}, 'content': inline(heading[2])})
            index += 1; continue
        if line.strip().startswith('|') and index + 1 < len(lines) and re.fullmatch(r'[| :\-]+', lines[index + 1].strip()):
            rows = []
            header = True
            while index < len(lines) and lines[index].strip().startswith('|'):
                row = lines[index].strip()
                index += 1
                if re.fullmatch(r'[| :\-]+', row):
                    continue
                cells = [{'type': 'tableHeader' if header else 'tableCell', 'content': [paragraph(cell.strip())]} for cell in row.strip('|').split('|')]
                rows.append({'type': 'tableRow', 'content': cells}); header = False
            blocks.append({'type': 'table', 'content': rows}); continue
        item = re.match(r'^\s*(?:([-+*])|(\d+)[.)])\s+(.*)$', line)
        if item:
            ordered, items = bool(item[2]), []
            start = int(item[2]) if ordered else 1
            while index < len(lines):
                item = re.match(r'^\s*(?:([-+*])|(\d+)[.)])\s+(.*)$', lines[index])
                if not item or bool(item[2]) != ordered:
                    break
                items.append({'type': 'listItem', 'content': [paragraph(item[3])]}); index += 1
            block = {'type': 'orderedList' if ordered else 'bulletList', 'content': items}
            if ordered:
                block['attrs'] = {'order': start}
            blocks.append(block); continue
        para = [line]; index += 1
        while index < len(lines) and lines[index].strip() and not re.match(r'^\s*(?:```|#{1,6}\s|\||[-+*]\s|\d+[.)]\s)', lines[index]):
            para.append(lines[index]); index += 1
        blocks.append(paragraph('\n'.join(para)))
    return {'type': 'doc', 'version': 1, 'content': blocks or [paragraph('')]}


def sanitize(raw):
    """Two passes remove identities also when repeated in URLs or free text."""
    replacements, accounts = {}, {}

    def collect(node, context=''):
        if isinstance(node, dict):
            account = node.get('accountId')
            if account:
                accounts.setdefault(account, f'712020:course-user-{len(accounts) + 1}')
                replacements[account] = account if re.fullmatch(r'712020:course-user-\d+', account) else accounts[account]
                for key in ('displayName', 'name', 'key'):
                    if isinstance(node.get(key), str) and node[key]:
                        replacements[node[key]] = 'Analityk (kurs)'
            if context == 'project' and node.get('name'):
                replacements[node['name']] = 'Projekt kursowy'
            for key, value in node.items():
                if key.lower() in ('cloudid', 'cloud_id') and isinstance(value, str):
                    replacements[value] = FAKE_CLOUD
                collect(value, key)
        elif isinstance(node, list):
            for value in node:
                collect(value, context)
        elif isinstance(node, str):
            for cloud in re.findall(r'(?:/ex/jira/|ari:cloud:jira:)(%s)' % UUID, node):
                replacements[cloud] = FAKE_CLOUD
            for email in re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', node):
                replacements[email] = '[email usunięty]'
    collect(raw)
    for old, new in list(replacements.items()):
        if quote(old, safe='') != old:
            replacements[quote(old, safe='')] = quote(new, safe='')
    pattern = re.compile('|'.join(re.escape(key) for key in sorted(replacements, key=len, reverse=True))) if replacements else None

    def scrub(text):
        if pattern:
            text = pattern.sub(lambda m: replacements[m.group()], text)
        text = re.sub('edukey.atlassian.net', 'course-site.atlassian.net', text, flags=re.I)
        return re.sub('edukey', 'Course', text, flags=re.I)

    def visit(node, context='', in_comment=False):
        if isinstance(node, dict):
            result = {}
            for key, value in node.items():
                if key == 'emailAddress':
                    continue
                if key == 'avatarUrls' and isinstance(value, dict):
                    result[key] = {size: AVATAR for size in value}
                elif key == 'body' and in_comment and isinstance(value, str):
                    result[key] = markdown_to_adf(scrub(value).replace(r'\[', '[').replace(r'\]', ']'))
                elif key == 'avatarUrl':
                    result[key] = AVATAR
                elif key == 'displayName':
                    result[key] = 'Analityk (kurs)'
                elif key == 'description' and isinstance(value, str):
                    result[key] = markdown_to_adf(scrub(value)) if context == 'fields' else scrub(value)
                else:
                    result[key] = visit(value, key, in_comment or key == 'comment')
            return result
        if isinstance(node, list):
            return [visit(item, context, in_comment) for item in node]
        if isinstance(node, str):
            text = scrub(node)
            return text.replace(r'\[', '[').replace(r'\]', ']') if in_comment else text
        return node
    return visit(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_export', type=Path)
    parser.add_argument('tickets', type=Path)
    parser.add_argument('--example', type=Path, required=True)
    parser.add_argument('--example-key', default='TEST-1')
    args = parser.parse_args(argv)
    paths = [args.raw_export.resolve(), args.tickets.resolve(), args.example.resolve()]
    if len(set(paths)) != 3:
        parser.error('Input and output paths must be distinct')
    clean = sanitize(json.loads(args.raw_export.read_text(encoding='utf-8')))
    issue = next((item for item in clean['issues'] if item['key'] == args.example_key), None)
    if issue is None:
        parser.error('Example key not present in export')
    example = {key: issue[key] for key in ('expand', 'id', 'self', 'key', 'fields')}
    for path, document in ((args.tickets, clean), (args.example, example)):
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Sanitized {len(clean["issues"])} issues; raw values were not logged.')


if __name__ == '__main__':
    main()
