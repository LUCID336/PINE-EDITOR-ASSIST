"""Create instrumented copies of a Gold Multi-Setup script for regression testing (not for delivery).
Appends data-window plots of the trade-engine state and redirects alert(...) calls to log.info so the
webhook payloads become observable on historical bars (alert() does not fire historically)."""
import re, sys
from pathlib import Path

def instrument(src: str) -> str:
    out = re.sub(r'alert\((.*), alert\.freq_once_per_bar_close\)', r'log.info("{0}", \1)', src)
    lines = ['', '// ---- regression instrumentation ----']
    for k in range(5):
        for name in ('sDir', 'sStage', 'stR', 'stN', 'stW'):
            lines.append(f'plot({name}.get({k}), "{name}_{k}", display = display.data_window)')
    lines.append('plot(dayCnt, "dayCnt", display = display.data_window)')
    return out + '\n'.join(lines) + '\n'

if __name__ == '__main__':
    Path(sys.argv[2]).write_text(instrument(Path(sys.argv[1]).read_text()))
