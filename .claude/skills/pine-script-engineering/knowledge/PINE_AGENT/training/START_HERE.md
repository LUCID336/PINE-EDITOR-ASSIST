# Pine Agent Academy — executable learning protocol

This module is an original training curriculum, not a copy of a course. Start with `COURSE_REVIEW.md` and `SOURCES.md`. New code uses v6; legacy examples are migration exercises. A language model does not update weights from reading this pack; persist reviewed findings, test artifacts and progress as files in a task workspace.

## Sequence
- Foundation L01–L05: series, types, state, collections, functions.
- Intermediate L06–L10: MTF, pivot observation, human presentation and AI features.
- Advanced L11–L15: strategy, sizing, profiling, migration, quant experiments.
- Capstone L16: end-to-end feature architecture, paper-only/sink-only.

## Learn → implement → test → challenge → repair → retest
1. Select the lowest unpassed prerequisite via `python tools/pine_training.py next`. Read the lab and cited version-matched docs. Retrieve V2 sheets using the specified `pine_lookup.py route`.
2. Write an independent solution and predict outputs before reading reference solution. Log API signatures and assumptions. Use `training/fixtures/synthetic.json` only for deterministic offline logic, never as Pine runtime evidence.
3. Compile via the official editor if authorized and available; record actual logs, symbol/feed, timezone, timeframe, settings, bar types, dates, and script hash. Perform each acceptance criterion including realtime/refresh if applicable. When not available, mark BLOCKED/NOT_RUN.
4. Review the reference solution; explain divergences, add one adversarial test, fix root cause and repeat affected checks. Use source hierarchy. Record what worked and what failed in the evidence template.
5. Score with RUBRIC.md. Progress to next lab only with reviewed evidence for mandatory gates; no self-attestation based on reading alone. Keep progress file outside the immutable release. `next --progress FILE` reads recorded status; it does not certify external evidence.
6. Promote findings only after source/behavior review, include exact source and build, observed limits and reproducible evidence. Revisit failed or outdated lessons; trigger on version changes or regression. Never store credentials.

## Quick commands
```bash
python tools/pine_training.py list
python tools/pine_training.py show L06
python tools/pine_training.py tips repaint
python tools/pine_training.py next
python tools/pine_training.py next --progress /path/to/progress.json
python -m unittest discover -s tests -v
```

No network or paid course access is required for offline labs. Official references and official editor are required for full Pine-specific acceptance. This release's Pine solutions have not been compiled.
