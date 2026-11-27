"""Static API check for Pine Script v6 source against the official reference ledger.

NOT a compiler. Detects: unknown built-in functions/namespace members, named
arguments that no official overload accepts, version-annotation problems,
a few known v5->v6 pitfalls. Type checking, qualifier checking, scoping and
runtime behavior are NOT covered; a clean result is not a compile PASS.

Usage: python pine_static_check.py FILE [FILE ...] [--json]
Exit code: 0 = no errors, 1 = errors found, 2 = usage problem.
"""
import json
import re
import sys
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / 'knowledge' / 'reference' / 'v6-api-ledger.json'

KEYWORDS = {'if', 'else', 'for', 'to', 'by', 'in', 'while', 'switch', 'var', 'varip', 'and', 'or',
            'not', 'true', 'false', 'na', 'import', 'export', 'method', 'type', 'enum', 'return',
            'continue', 'break', 'series', 'simple', 'const', 'input', 'once', 'int', 'float', 'bool',
            'string', 'color', 'line', 'label', 'box', 'table', 'linefill', 'polyline', 'array',
            'matrix', 'map', 'chart.point', 'footprint', 'volume_row'}
TYPE_NAMES = {'int', 'float', 'bool', 'string', 'color', 'line', 'label', 'box', 'table', 'linefill',
              'polyline', 'footprint', 'volume_row'}


def load_ledger(path=LEDGER):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    funcs, members = {}, set()
    for e in data['entries']:
        name = re.sub(r'<[^>]*>', '', e['name'])
        if e['kind'] == 'fun':
            funcs.setdefault(name, []).extend(e['overload_params'] or [[]])
        elif e['kind'] in ('var', 'const', 'type'):
            members.add(name)
    namespaces = {n.split('.')[0] for n in list(funcs) + list(members) if '.' in n}
    return funcs, members, namespaces


def strip_code(src):
    """Blank out comments and string literals, keep line/column structure."""
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith('//', i):
            j = src.find('\n', i)
            j = n if j < 0 else j
            out.append(' ' * (j - i)); i = j
        elif src.startswith('"""', i) or src.startswith("'''", i):
            q = src[i:i + 3]; j = src.find(q, i + 3); j = n if j < 0 else j + 3
            out.append(re.sub(r'[^\n]', ' ', src[i:j])); i = j
        elif src[i] in '"\'':
            q = src[i]; j = i + 1
            while j < n and src[j] != q and src[j] != '\n':
                j += 2 if src[j] == '\\' else 1
            j = min(j + 1, n)
            out.append('"' + ' ' * (j - i - 2) + '"' if j - i >= 2 else ' ' * (j - i)); i = j
        else:
            out.append(src[i]); i += 1
    return ''.join(out)


def call_args(code, open_idx):
    """Return top-level named-argument identifiers of the call starting at '('."""
    depth, i, names, start = 0, open_idx, [], open_idx + 1
    seg_starts = [open_idx + 1]
    while i < len(code):
        c = code[i]
        if c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
            if depth == 0:
                break
        elif c == ',' and depth == 1:
            seg_starts.append(i + 1)
        i += 1
    end = i
    for k, s in enumerate(seg_starts):
        e = seg_starts[k + 1] - 1 if k + 1 < len(seg_starts) else end
        m = re.match(r'\s*([A-Za-z_]\w*)\s*=(?!=)', code[s:e])
        if m:
            names.append(m.group(1))
    return names


def check(src, ledger):
    funcs, members, namespaces = ledger
    findings = []
    def add(sev, line, msg):
        findings.append({'severity': sev, 'line': line, 'message': msg})

    raw_lines = src.splitlines()
    versions = [i + 1 for i, l in enumerate(raw_lines) if re.match(r'^\s*//@version\s*=\s*\d+\s*$', l)]
    if len(versions) != 1:
        add('ERROR', versions[0] if versions else 1, f'expected exactly one //@version annotation, found {len(versions)}')
    elif not re.match(r'^\s*//@version\s*=\s*6\s*$', raw_lines[versions[0] - 1]):
        add('WARN', versions[0], 'not version 6; ledger covers v6 only, results not applicable')

    code = strip_code(src)
    line_of = lambda idx: code.count('\n', 0, idx) + 1

    # user-defined names
    udf = set(re.findall(r'^\s*(?:export\s+)?(?:method\s+)?([A-Za-z_]\w*)\s*\([^\n]*\)\s*=>', code, re.M))
    methods = set(re.findall(r'^\s*(?:export\s+)?method\s+([A-Za-z_]\w*)\s*\(', code, re.M))
    udts = set(re.findall(r'^\s*(?:export\s+)?(?:type|enum)\s+([A-Za-z_]\w*)', code, re.M))
    imports = set(re.findall(r'^\s*import\s+[\w/.]+\s+as\s+(\w+)', code, re.M))
    imports |= {m.split('/')[1] for m in re.findall(r'^\s*import\s+(\w+/\w+)/\d+\s*$', code, re.M)}
    # Declarations/reassignments start a statement (line start or after `if`/`=>` etc. is rare);
    # named arguments inside calls must NOT count as declarations (root cause of an earlier miss).
    declared = set(re.findall(
        r'^[ \t]*(?:var[ \t]+|varip[ \t]+)?(?:(?:series|simple|const)[ \t]+)?'
        r'(?:[A-Za-z_][\w.]*(?:<[\w\s,.<>]*>)?(?:\[\])?[ \t]+)?([A-Za-z_]\w*)[ \t]*(?::=|=(?![=>])|\+=|-=|\*=|/=)',
        code, re.M))
    declared |= set(re.findall(r'\bfor\s+(?:\[\s*(\w+)\s*,\s*)?(\w+)', code) and
                    [x for t in re.findall(r'\bfor\s+(?:\[\s*(\w+)\s*,\s*)?(\w+)', code) for x in t if x])
    for m in re.finditer(r'^\s*\[([^\]]*)\]\s*=', code, re.M):
        declared |= {v.strip() for v in m.group(1).split(',') if v.strip()}
    for m in re.finditer(r'=>|\(([^()]*)\)\s*=>', code):
        if m.group(1):
            for p in m.group(1).split(','):
                w = re.findall(r'[A-Za-z_]\w*', p.split('=')[0])
                if w:
                    declared.add(w[-1])
    method_names = {n.split('.')[-1] for n in funcs if '.' in n} | methods

    # calls
    for m in re.finditer(r'(?<![\w.])((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*)(\s*<[\w\s,.<>]*>)?\s*\(', code):
        name, start = m.group(1), m.start(1)
        if name in KEYWORDS and name not in funcs:
            continue
        parts = name.split('.')
        head = parts[0]
        if name in funcs:
            sigs = funcs[name]
            allowed = {re.sub(r'\W', '', p) for sig in sigs for p in sig}
            for a in call_args(code, m.end() - 1):
                if allowed and a not in allowed:
                    add('ERROR', line_of(start), f'{name}(): named argument "{a}" not in any official overload {sorted(allowed)}')
            continue
        if len(parts) == 1:
            if name in udf or name in udts or name in declared:
                continue
            add('ERROR', line_of(start), f'unknown function "{name}()" (not a v6 built-in, not user-defined in file)')
            continue
        if head in udts or head in imports:
            continue
        if parts[-1] == 'new' and (head in udts or head in TYPE_NAMES):
            continue
        if head in namespaces and head not in declared:
            add('ERROR', line_of(start), f'unknown built-in "{name}()" in namespace "{head}"')
            continue
        # method-style call on an object: verify the method name exists somewhere
        if parts[-1] not in method_names and parts[-1] not in udf and parts[-1] != 'new':
            add('WARN', line_of(start), f'method "{parts[-1]}" in "{name}()" matches no built-in or user method')

    # namespace members (non-call)
    for m in re.finditer(r'(?<![\w.])([a-z_]\w*(?:\.[A-Za-z_]\w*)+)(?![\w.]|\s*[(<])', code):
        name = m.group(1)
        head = name.split('.')[0]
        if head not in namespaces or head in declared or head in udts or head in imports:
            continue
        if name in members or name in funcs:
            continue
        # NOTE: a former blanket exemption "any member.<x>" let every color.<typo> pass because
        # `color` is also a type entry (mutation test 2026-11-27: 60% -> see learning log).
        add('ERROR', line_of(m.start(1)), f'unknown built-in variable/constant "{name}"')

    # literal type mismatches in explicitly typed declarations (PineTS accepts these silently)
    lit = {'string': r'"[ ]*"', 'bool': r'(?:true|false)\b', 'float': r'-?\d+\.\d*|-?\.\d+', 'int': r'-?\d+(?![.\d])',
           'color': r'#[0-9A-Fa-f]{6}'}
    for m in re.finditer(r'^[ \t]*(?:var[ \t]+|varip[ \t]+|const[ \t]+)*(int|float|bool|string|color)[ \t]+[A-Za-z_]\w*[ \t]*=[ \t]*'
                         r'("[ ]*"|true\b|false\b|#[0-9A-Fa-f]{6}|-?\d+\.\d*|-?\.\d+|-?\d+)(?=[ \t]*$)', code, re.M):
        declared_type, value = m.group(1), m.group(2)
        kind = next(k for k, rx in lit.items() if re.fullmatch(rx, value))
        ok = kind == declared_type or (declared_type == 'float' and kind == 'int')
        if not ok:
            add('ERROR', line_of(m.start()), f'type mismatch: "{declared_type}" declared but {kind} literal assigned')

    # TradingView consistency warning (observed T7, 2026-11-27): history-dependent ta.* call inside a conditional
    # local block (if/else/for/while/switch), not inside a function body.
    stack = []  # (indent, kind)
    for ln_no, ln in enumerate(code.split('\n'), 1):
        if not ln.strip():
            continue
        ind = len(ln) - len(ln.lstrip(' \t'))
        while stack and ind <= stack[-1][0]:
            stack.pop()
        body = ln.strip()
        if any(k == 'cond' for _, k in stack):
            for m in re.finditer(r'(?<![\w.])(ta\.\w+)\s*\(', body):
                add('WARN', ln_no, f'{m.group(1)}() inside a conditional block: TradingView warns "The function ... should be '
                                   'called on each calculation for consistency"; compute it unconditionally')
        if re.search(r'=>\s*$', body):
            stack.append((ind, 'func'))
        elif re.match(r'(?:else\b|if\b|for\b|while\b|switch\b)|.*(?:=|:=)\s*(?:if|switch|for|while)\b', body):
            stack.append((ind, 'cond'))

    # v6 pitfalls (documented in migration guide)
    for m in re.finditer(r'\btransp\s*=', code):
        add('ERROR', line_of(m.start()), '"transp" parameter removed; use color.new() transparency')
    for m in re.finditer(r'(?<![\w.])(study|security)\s*\(', code):
        add('ERROR', line_of(m.start()), f'"{m.group(1)}()" is pre-v5 syntax')
    return sorted(findings, key=lambda f: (f['line'], f['severity']))


def main(argv):
    as_json = '--json' in argv
    files = [a for a in argv if a != '--json']
    if not files:
        print(__doc__); return 2
    ledger = load_ledger()
    report, errors = {}, 0
    for f in files:
        res = check(Path(f).read_text(encoding='utf-8-sig'), ledger)
        report[f] = res
        errors += sum(1 for r in res if r['severity'] == 'ERROR')
    if as_json:
        print(json.dumps(report, indent=1))
    else:
        for f, res in report.items():
            status = 'STATIC-FAIL' if any(r['severity'] == 'ERROR' for r in res) else 'STATIC-PASS'
            print(f'{status}  {f}')
            for r in res:
                print(f"  {r['severity']:5} L{r['line']}: {r['message']}")
        print('Note: static API check only; TradingView compile/runtime NOT RUN.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
