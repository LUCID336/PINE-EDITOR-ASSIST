# Pine Script Research & Coding Agent | 2026-11-27
Version 2.0 — agent instruction expansion and research foundation, not a fully enumerated or compiler-certified language reference.

Start with `SKILL.md`, `AGENTS.md`, and `instructions/START_HERE.md`. Use `python tools/pine_lookup.py route indicator` or `python tools/pine_lookup.py api request.security --json`. The v2 module has 78 topic sheets, 43 API-family sheets, 612 discovery entries, six workflows and three JSON templates. Read only the relevant chunks and verify official sources. The 78-topic index covers the visible v6 manual TOC; symbol discovery is a curated starting inventory, not all official entries. The official interactive reference remains canonical. The package contains original examples, AI JSON schema and fixtures, a standard-library local audit, six audit records and an open-items register. No third-party manual is redistributed wholesale.

Install into an agent workspace by copying this directory. Keep SKILL.md and its relative files together. For Codex/Claude Code, load the skill using the platform's documented skill discovery path or explicitly instruct it to read the file; AGENTS.md is the repository-level contract. For a RAG/Obsidian vault, ingest Markdown, CSV, JSON with source/date/version metadata. Treat examples as UNCOMPILED until tested in the Pine Editor.

Run `python tools/audit.py` from any location with Python 3.10+; it uses no network. Run `python -m unittest discover -s tests -v` from this directory. For deployment, follow `references/TEST_PLAN.md` and close all applicable blockers.

Run `python tools/audit_instructions.py` for v2 package checks. V1 audit is preserved and still runs independently.

## V3 — Pine Agent Academy
Start with `training/START_HERE.md` for 16 original labs, 14 uncompiled v6 solution scripts, 40 engineering tips, 18 quiz questions and 37 resource records. `tools/pine_training.py list|show|tips|next` retrieves learning material. All V2 guidance is retained. See `audit/V3_REVIEW.md` and `audit/OPEN_ITEMS.md` for limits.
