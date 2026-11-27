---
id: M38
version: 6
status: SOURCE_ACCESSED_PARTIAL
source: https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
---
# Other timeframes and data — Agent instruction

**What / where:** Concepts / Other timeframes and data; use this sheet when the implementation or review touches this topic.

**How / when:** Choose same-TF, strictly higher-TF or lower-TF route; for confirmed HTF use offset expression with lookahead_on; for LTF use intrabar arrays where appropriate.

**Why:** Misalignment, lookahead and sparse bars can leak or distort information.

**Verification / acceptance:** Check boundary bars, gaps, no future values and empty intrabar arrays.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `SOURCE_ACCESSED_PARTIAL`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
