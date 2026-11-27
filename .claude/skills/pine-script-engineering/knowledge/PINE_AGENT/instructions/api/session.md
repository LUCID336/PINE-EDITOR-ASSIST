# API family: session

**Agent rule:** Verify session timezone, exchange availability, overnight and DST.

Topics: M40 M43. Resolve IDs in `instructions/topic-index.json`.

**Discovery candidates (7):**

- `session.ismarket`
- `session.ispremarket`
- `session.ispostmarket`
- `session.isfirstbar`
- `session.islastbar`
- `session.isfirstbar_regular`
- `session.islastbar_regular`

All names above are candidates from v1, not independently verified signatures or a full namespace inventory. Search the exact identifier in the official reference of the target version; if missing, check release notes or mark BLOCKED. Fill the API evidence ledger before coding.
