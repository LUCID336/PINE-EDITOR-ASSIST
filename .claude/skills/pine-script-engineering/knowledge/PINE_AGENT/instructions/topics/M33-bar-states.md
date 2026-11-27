---
id: M33
version: 6
status: TOC_MAPPED_REVIEW_REQUIRED
source: https://www.tradingview.com/pine-script-docs/concepts/bar-states/
---
# Bar states — Agent instruction

**What / where:** Concepts / Bar states; use this sheet when the implementation or review touches this topic.

**How / when:** Use barstate flags according to historical/live lifecycle; distinguish last from confirmed; do not rely on isconfirmed inside request.security.

**Why:** A chart bar confirmation does not confirm a higher timeframe bar.

**Verification / acceptance:** Test first, historical, last and closing live bar.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/concepts/bar-states/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `TOC_MAPPED_REVIEW_REQUIRED`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
