---
id: M09
version: 6
status: TOC_MAPPED_REVIEW_REQUIRED
source: https://www.tradingview.com/pine-script-docs/language/variable-declarations/
---
# Variable declarations — Agent instruction

**What / where:** Language / Variable declarations; use this sheet when the implementation or review touches this topic.

**How / when:** Use = for declaration, := for reassignment, var for persistent state, varip only for intentional intrabar tracking; use typed na.

**Why:** Accidental local shadowing or rollback changes state semantics.

**Verification / acceptance:** Test initialization, consecutive bars, live tick and reload.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/language/variable-declarations/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `TOC_MAPPED_REVIEW_REQUIRED`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
