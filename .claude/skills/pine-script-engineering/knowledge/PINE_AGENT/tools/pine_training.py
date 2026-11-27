"""Offline training retrieval and recorded prerequisite routing; not a compiler or credentialing tool."""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT / 'training' / name).read_text(encoding='utf-8'))

def next_labs(progress=None):
    labs = load('curriculum.json')
    recorded = (progress or {}).get('lessons', {})
    def passed(lesson):
        row = recorded.get(lesson, {})
        return row.get('status') == 'PASS' and isinstance(row.get('evidence'), str) and bool(row['evidence'].strip())
    return [lab for lab in labs if not passed(lab['id']) and all(passed(x) for x in lab['prerequisites'])]

def lookup_tips(query):
    needle = query.casefold().strip()
    return [x for x in load('tips.json') if needle and needle in ' '.join(str(v) for v in x.values()).casefold()]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    show = sub.add_parser('show'); show.add_argument('id')
    tips = sub.add_parser('tips'); tips.add_argument('query')
    nxt = sub.add_parser('next'); nxt.add_argument('--progress', type=Path)
    args = parser.parse_args()
    labs = load('curriculum.json')
    if args.command == 'list': result = labs
    elif args.command == 'show':
        result = next((x for x in labs if x['id'].casefold() == args.id.casefold()), None)
        if result is None:
            parser.error('unknown lesson ID')
        print((ROOT / result['path']).read_text(encoding='utf-8')); return 0
    elif args.command == 'tips': result = lookup_tips(args.query)
    else:
        progress = json.loads(args.progress.read_text(encoding='utf-8')) if args.progress else None
        result = next_labs(progress)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
