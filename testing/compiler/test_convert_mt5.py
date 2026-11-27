"""MT5 bar-export converter: header/encoding parsing, server-time -> UTC mapping, dedup, OHLC validation."""
import json
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / 'tools'))
import convert_mt5 as cm  # noqa: E402

HEAD = '<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n'


def _write(tmp, lines, enc='utf-8'):
    p = tmp / 'mt5.csv'
    p.write_bytes((HEAD + ''.join(lines)).encode(enc))
    return p


def test_nyclose_winter_and_summer_offsets(tmp_path):
    p = _write(tmp_path, ['2024.01.15\t09:00:00\t2050.10\t2051.00\t2049.90\t2050.50\t120\t0\t25\n',
                          '2024.01.15\t09:05:00\t2050.50\t2050.90\t2050.00\t2050.20\t110\t0\t27\n',
                          '2024.07.15\t09:00:00\t2400.00\t2401.00\t2399.00\t2400.50\t100\t0\t30\n'])
    rows, rep = cm.convert(p)
    assert rows[0][0] == 1705302000000      # 2024-01-15 07:00 UTC (server UTC+2 in winter)
    assert rows[2][0] == 1721023200000      # 2024-07-15 06:00 UTC (server UTC+3 in US summer time)
    assert rep['interval_minutes'] == 5 and rep['spread_points']['median'] == 27


def test_fixed_offset_utf16_dedup_and_invalid_rows(tmp_path):
    p = _write(tmp_path, ['2024.01.15\t09:00:00\t10\t11\t9\t10.5\t1\t0\t2\n',
                          '2024.01.15\t09:00:00\t10\t11\t9\t10.5\t1\t0\t2\n',      # duplicate
                          '2024.01.15\t09:05:00\t10\t9\t11\t10\t1\t0\t2\n',        # high < low
                          '2024.01.15\t09:10:00\t10\t11\t9\t10\t1\t0\t2\n'], enc='utf-16')
    rows, rep = cm.convert(p, server_tz='0')
    assert len(rows) == 2 and rep['duplicate_times_dropped'] == 1 and rep['invalid_ohlc_dropped'] == 1
    assert rows[0][0] == 1705309200000


def test_cli_never_overwrites(tmp_path, capsys):
    p = _write(tmp_path, ['2024.01.15\t09:00:00\t10\t11\t9\t10.5\t1\t0\t2\n', '2024.01.15\t09:05:00\t10\t11\t9\t10.5\t1\t0\t2\n'])
    out = tmp_path / 'o.csv'
    assert cm.main([str(p), str(out)]) == 0
    assert out.read_text().splitlines()[0] == 'time,open,high,low,close,volume'
    capsys.readouterr()
    assert cm.main([str(p), str(out)]) == 1
    assert json.loads(capsys.readouterr().out)['status'] == 'FAILED'
