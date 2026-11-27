---
id: M37
version: 6
status: TOC_MAPPED_REVIEW_REQUIRED
source: https://www.tradingview.com/pine-script-docs/concepts/non-standard-charts-data/
---
# Non-standard charts data — Agent instruction

**What / where:** Concepts / Non-standard charts data; use this sheet when the implementation or review touches this topic.

**How / when:** Use ticker constructors only with explicit synthetic context; request standard prices when needed.

**Why:** Heikin Ashi/Renko/etc. are not equivalent to tradeable OHLC.

**Verification / acceptance:** Compare synthetic vs standard data and prohibit naive fill claims.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/concepts/non-standard-charts-data/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `TOC_MAPPED_REVIEW_REQUIRED`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
