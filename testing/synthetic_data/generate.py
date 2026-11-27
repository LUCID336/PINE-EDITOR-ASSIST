"""Deterministic synthetic OHLCV generator (no market data rights involved).
Writes CSV: time_utc_ms,open,high,low,close,volume. Usage: python generate.py OUT.csv --tf-min 15 --bars 2880 --seed 7"""
import argparse, csv, random
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--tf-min', type=int, default=15)
ap.add_argument('--bars', type=int, default=2880); ap.add_argument('--seed', type=int, default=7)
ap.add_argument('--start-ms', type=int, default=1704067200000)  # 2024-01-01T00:00:00Z
ap.add_argument('--drift', type=float, default=0.0); ap.add_argument('--vol', type=float, default=0.004)
a = ap.parse_args(); rnd = random.Random(a.seed); p = 100.0
with open(a.out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['time', 'open', 'high', 'low', 'close', 'volume'])
    for i in range(a.bars):
        regime = 1.0 if (i // 400) % 2 == 0 else -1.0          # alternating trend regimes
        o = p; c = max(1.0, o * (1 + a.drift * regime + rnd.gauss(0, a.vol)))
        h = max(o, c) * (1 + abs(rnd.gauss(0, a.vol / 2))); l = min(o, c) * (1 - abs(rnd.gauss(0, a.vol / 2)))
        w.writerow([a.start_ms + i * a.tf_min * 60000, round(o, 4), round(h, 4), round(l, 4), round(c, 4), round(1000 + rnd.random() * 500, 2)])
        p = c
