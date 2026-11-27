# Temporal correctness and data requests

Route M04 M33 M37 M38 M39 M40 M43 M44.

Choose chart timeframe data directly if no other context needed. For a strictly higher timeframe confirmed value, validate `timeframe.in_seconds(htf) > timeframe.in_seconds()` on comparable time charts; request previous HTF expression with lookahead_on. Example fragment (v6, compile required):

```pine
float priorHtf = request.security(syminfo.tickerid, htf, close[1], lookahead = barmerge.lookahead_on)
```

Offset every requested expression independently; never offset the merged chart series as a substitute. The value is from the prior completed HTF bar, not the current developing one. Reject unsupported TF inputs. For current developing HTF label provisional and exclude from close-confirmed signals unless explicitly specified. For LTF, prefer `request.security_lower_tf()` when needing intrabar arrays; empty arrays are allowed, feed and intrabar coverage differ. For same-TF external symbol align timestamps and gaps, do not apply HTF template blindly.

Define pivot occurrence separately from confirmation (right-side bars elapsed); do not timestamp a trade at the visually back-shifted pivot. Never use `lookahead_on` without safe historical offset for future-sensitive HTF values. Confirm chart signals at bar close by default; `barstate.isconfirmed` inside security is not an HTF confirmation solution. Intrabar varip state is not generally replayable from historical OHLC. Compare live confirmed events to reload; log source, feed, bar times, revisions. If data not ready, propagate null/na and block decisions.
