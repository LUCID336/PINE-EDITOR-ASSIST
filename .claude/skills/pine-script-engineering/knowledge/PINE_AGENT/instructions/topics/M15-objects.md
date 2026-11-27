---
id: M15
version: 6
status: TOC_MAPPED_REVIEW_REQUIRED
source: https://www.tradingview.com/pine-script-docs/language/objects/
---
# Objects — Agent instruction

**What / where:** Language / Objects; use this sheet when the implementation or review touches this topic.

**How / when:** Use UDTs for named state; treat assignments as references unless explicit copy semantics are verified.

**Why:** Aliasing and rollback can change multiple apparent objects.

**Verification / acceptance:** Mutate an alias and a separate object in a controlled probe.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/language/objects/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `TOC_MAPPED_REVIEW_REQUIRED`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
