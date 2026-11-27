"""Convert a MetaTrader 5 bar export into the lab CSV (time[ms UTC],open,high,low,close,volume).

MT5: Symbol window -> Bars -> Export (tab-separated, header
<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>, date 2024.01.02, time 01:05:00).
MT5 timestamps are BROKER SERVER time. Choose how to map them to UTC:
  --server-tz nyclose   (default; most FX/CFD brokers: server = New York time + 7 h, i.e. UTC+2 winter / UTC+3 summer)
  --server-tz +2        (fixed offset in hours, e.g. +2, +3, 0)
  --server-tz Europe/Athens (any IANA zone)
Wrong time mapping shifts every session filter of the strategy (NY 12-17 UTC etc.), so check the report.

Usage: python tools/convert_mt5.py XAUUSD_M5.csv data/xauusd_m5_utc.csv [--server-tz nyclose] [--volume tick|real]
Prints a JSON report (rows, range, interval, duplicates, gaps, spread stats). Never overwrites an existing output.
Data stays local; the lab does not upload it anywhere.
"""
import argparse
import csv
import io
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo('America/New_York')


def _to_utc_ms(local: datetime, server_tz: str) -> int:
    if server_tz == 'nyclose':
        ny = (local - timedelta(hours=7)).replace(tzinfo=NY)
        return int(ny.timestamp() * 1000)
    try:
        off = float(server_tz)
        return int((local - timedelta(hours=off)).replace(tzinfo=timezone.utc).timestamp() * 1000)
    except ValueError:
        return int(local.replace(tzinfo=ZoneInfo(server_tz)).timestamp() * 1000)


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ('utf-16', 'utf-8-sig') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else ('utf-8-sig', 'cp1252'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError('cannot decode file (expected UTF-8 or UTF-16 MT5 export)')


def convert(src: Path, server_tz: str = 'nyclose', volume: str = 'tick'):
    text = _read_text(src)
    first = text.splitlines()[0] if text else ''
    delim = '\t' if '\t' in first else (';' if ';' in first else ',')
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    head = [h.strip().strip('<>').upper() for h in rows[0]]
    need = ['DATE', 'TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE']
    if not all(n in head for n in need):
        raise ValueError(f'unexpected header {rows[0]!r}; expected MT5 bar export with {need}')
    ix = {n: head.index(n) for n in head}
    vcol = 'TICKVOL' if volume == 'tick' else 'VOL'
    out, spreads, bad = [], [], 0
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        try:
            local = datetime.strptime(r[ix['DATE']].strip() + ' ' + r[ix['TIME']].strip(), '%Y.%m.%d %H:%M:%S')
        except ValueError:
            local = datetime.strptime(r[ix['DATE']].strip() + ' ' + r[ix['TIME']].strip(), '%Y.%m.%d %H:%M')
        o, h, l, c = (float(r[ix[k]]) for k in ('OPEN', 'HIGH', 'LOW', 'CLOSE'))
        if not (l <= min(o, c) and h >= max(o, c) and l > 0):
            bad += 1
            continue
        v = float(r[ix[vcol]]) if vcol in ix else 0.0
        if 'SPREAD' in ix:
            spreads.append(float(r[ix['SPREAD']]))
        out.append((_to_utc_ms(local, server_tz), o, h, l, c, v))
    out.sort()
    dedup, dups = [], 0
    for row in out:
        if dedup and row[0] == dedup[-1][0]:
            dups += 1
            continue
        dedup.append(row)
    if len(dedup) < 2:
        raise ValueError('fewer than 2 valid bars')
    deltas = [b[0] - a[0] for a, b in zip(dedup, dedup[1:])]
    step = statistics.mode(deltas)
    gaps = [d for d in deltas if d > step]
    weekend = sum(1 for d in gaps if d >= 40 * 3600 * 1000)
    report = {
        'rows': len(dedup), 'invalid_ohlc_dropped': bad, 'duplicate_times_dropped': dups,
        'interval_minutes': step / 60000, 'non_uniform_intervals': sum(1 for d in deltas if d % step),
        'first_utc': datetime.fromtimestamp(dedup[0][0] / 1000, timezone.utc).isoformat(),
        'last_utc': datetime.fromtimestamp(dedup[-1][0] / 1000, timezone.utc).isoformat(),
        'gaps': len(gaps), 'weekend_gaps': weekend, 'longest_gap_hours': round(max(gaps, default=0) / 3.6e6, 2),
        'server_tz': server_tz, 'volume': vcol,
        'spread_points': ({'median': statistics.median(spreads), 'p90': sorted(spreads)[int(0.9 * (len(spreads) - 1))],
                           'max': max(spreads)} if spreads else None),
        'note': 'Check first_utc/last_utc and session hours against your broker. Spread is in MT5 points '
                '(XAUUSD usually 0.01 $ per point): median * 0.01 $ ~ costs per oz per round trip.',
    }
    return dedup, report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src', type=Path)
    ap.add_argument('dst', type=Path)
    ap.add_argument('--server-tz', default='nyclose')
    ap.add_argument('--volume', choices=['tick', 'real'], default='tick')
    a = ap.parse_args(argv)
    if a.dst.exists():
        print(json.dumps({'status': 'FAILED', 'error': f'{a.dst} exists (never overwritten)'}))
        return 1
    try:
        rows, report = convert(a.src, a.server_tz, a.volume)
    except (OSError, ValueError) as e:
        print(json.dumps({'status': 'FAILED', 'error': str(e)}))
        return 1
    a.dst.parent.mkdir(parents=True, exist_ok=True)
    with open(a.dst, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['time', 'open', 'high', 'low', 'close', 'volume'])
        for t, o, h, l, c, v in rows:
            w.writerow([t, repr(o), repr(h), repr(l), repr(c), repr(v)])
    print(json.dumps({'status': 'OK', 'output': str(a.dst), **report}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
