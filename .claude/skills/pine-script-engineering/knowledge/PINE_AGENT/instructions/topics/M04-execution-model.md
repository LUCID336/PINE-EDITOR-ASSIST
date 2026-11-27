---
id: M04
version: 6
status: SOURCE_ACCESSED_PARTIAL
source: https://www.tradingview.com/pine-script-docs/language/execution-model/
---
# Execution model — Agent instruction

**What / where:** Language / Execution model; use this sheet when the implementation or review touches this topic.

**How / when:** Model one pass per historical bar for ordinary indicators and recalculation on live updates; distinguish committed state from intrabar rollback.

**Why:** Historical OHLC does not reconstruct all live ticks.

**Verification / acceptance:** Capture live close outputs, reload and compare; explicitly test varip behavior.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/language/execution-model/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `SOURCE_ACCESSED_PARTIAL`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
