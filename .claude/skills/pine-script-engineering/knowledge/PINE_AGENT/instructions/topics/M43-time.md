---
id: M43
version: 6
status: TOC_MAPPED_REVIEW_REQUIRED
source: https://www.tradingview.com/pine-script-docs/concepts/time/
---
# Time — Agent instruction

**What / where:** Concepts / Time; use this sheet when the implementation or review touches this topic.

**How / when:** Treat timestamps as Unix milliseconds, format with explicit timezone; distinguish bar open, close and observation time.

**Why:** Time zone display and event ordering are different.

**Verification / acceptance:** Test DST, gaps and missing close time on non-time bars.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/concepts/time/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `TOC_MAPPED_REVIEW_REQUIRED`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
