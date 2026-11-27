# API family: volume_row

**Agent rule:** Verify row access, missing row, price boundaries, volume units and imbalance definition.

Topics: M38 M70. Resolve IDs in `instructions/topic-index.json`.

**Discovery candidates (8):**

- `volume_row.up_price`
- `volume_row.down_price`
- `volume_row.total_volume`
- `volume_row.buy_volume`
- `volume_row.sell_volume`
- `volume_row.delta`
- `volume_row.has_buy_imbalance`
- `volume_row.has_sell_imbalance`

All names above are candidates from v1, not independently verified signatures or a full namespace inventory. Search the exact identifier in the official reference of the target version; if missing, check release notes or mark BLOCKED. Fill the API evidence ledger before coding.
