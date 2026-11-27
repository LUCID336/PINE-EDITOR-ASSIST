---
id: M14
version: 6
status: SOURCE_ACCESSED_PARTIAL
source: https://www.tradingview.com/pine-script-docs/language/user-defined-functions/
---
# User-defined functions — Agent instruction

**What / where:** Language / User-defined functions; use this sheet when the implementation or review touches this topic.

**How / when:** Use typed parameters where needed, return values or tuples, avoid recursion and global scalar reassignment.

**Why:** Functions have scope and call-site history semantics.

**Verification / acceptance:** Call on every bar if history dependent; compare two independent call sites.

**Source / provenance:** [Official manual](https://www.tradingview.com/pine-script-docs/language/user-defined-functions/). Open the relevant subsection and [version-specific API reference](https://www.tradingview.com/pine-script-reference/v6/) before generating calls. This is an original engineering instruction, not a full transcription or certified exhaustive chapter summary. Source status: `SOURCE_ACCESSED_PARTIAL`. Record evidence in the task ledger. If source or runtime is unavailable, mark the corresponding gate BLOCKED / NOT_RUN.
