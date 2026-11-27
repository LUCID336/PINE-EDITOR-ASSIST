# Cost assumptions (zero-subscription goal)

| Item | Cost | Mandatory? | Notes |
|---|---|---|---|
| Local core (pinelab CLI, checker, PineTS runtime, Python tests) | 0 | yes | open source, no API key, no account |
| Synthetic test data | 0 | yes | generated locally |
| Node.js, Python, pytest, jsonschema | 0 | yes | free downloads |
| Internet | existing | once | only for `npm ci` during installation and optional ledger refresh |
| Claude / Claude Code usage | existing | – | not part of the zero-subscription goal (per order) |
| TradingView plan / AI Copilot add-on (operator bought one for ~4 EUR) | optional | **no** | used only for manual reference checks (TV_VERIFIED_RELAYED). MCP access additionally requires an active paid base plan (TradingView docs). |
| Commercial PineTS licence | optional | no | only needed outside AGPL terms |
| Market data | 0 (own/allowed data) | no | user-supplied CSV; rights must be checked by the operator |

Disabled by default and requiring separate approval: any paid API, remote MCP endpoint, data subscription, live trading,
publication. `.mcp.json` points only to the local stdio wrapper.
