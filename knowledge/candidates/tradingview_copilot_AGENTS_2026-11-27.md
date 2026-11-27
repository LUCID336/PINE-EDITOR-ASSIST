# CANDIDATE knowledge — TradingView AI Copilot "AGENTS.md" (2026-11-27)

Status: **CANDIDATE, not verified knowledge.** Source: TradingView AI Copilot answer, personal use by the operator,
chart VANTAGE:XAUUSD 1h. Not used for model training. Each claim must be checked against the official v6 ledger
(`knowledge/reference/v6-api-ledger.json`) or the Pine manual before promotion to `learning/`.

## Verification of key claims (Claude, 2026-11-27)
| Section | Claim | Check | Result |
|---|---|---|---|
| 1.2 | `valid:true` can appear together with filled `errors[]` | Round-3 T8a–c (relayed) | CONFIRMED as observed channel behaviour (contradicts docs' "valid plus errors"); always judge by `errors[]` |
| 2 | Four message templates | Round-3 T7/T8 | CONFIRMED (A) → `knowledge/reference/tv_compiler_messages_2026-11-27.json` |
| 3.2 | "many ta.* `length` params require simple int" | Ledger | PARTIAL: ta.ema/ta.rsi/ta.atr = simple int; **ta.sma and ta.highest accept series int** in v6 |
| 3.5 | v6 `and`/`or` are lazy | V3 sheet + lab L02 | consistent with V3 knowledge; ledger has no operator semantics → keep as documented-elsewhere |
| 4.2 | `var` rolled back on open realtime bar, `varip` not | Manual (execution model) | consistent with official docs |
| 4.4 | `barstate.isclosed` does not exist | T8c + ledger | CONFIRMED |
| 4.5 | `once` behaviour "unknown" | Official conditional-structures page | RESOLVED: a not-yet-fired `once` re-executes on each tick of an open realtime bar (rollback); only execution on a closing tick deactivates it. Counter 5 is expected. |
| 5.1 | ta.ema first non-na on bar 19 | T1 | CONFIRMED (TV = PineTS) |
| 5.3 | ta.rsi of constant series = 100 | T2 | CONFIRMED (last bar) |
| 5.4/5.5 | built-ins reflect requested context; global runtime.error not raised | T3 + T3b | CONFIRMED (inference for "only expression evaluated" is strong) |
| 5.6 | 7/234 mismatches question repaint-freedom of the close[1]+lookahead_on idiom | T6b | RE-INTERPRETED: mismatches sit at weekend/holiday session irregularities; htfPrev matched the actual last close, the lookahead_off reference was stale → probe artefact, not idiom repaint |
| 6.1 | pivot value = high[rightBars], reported rightBars later | T10 | CONFIRMED |
| 6.2 | equal-neighbour case exists | T10 | CONFIRMED; tie side still unknown |
| 7.1/7.2 | next-bar-open fills; percent commission per side | T9 | CONFIRMED |
| 7.4 | process_orders_on_close fills at signal-bar close | Strategies manual | consistent with docs; not executed |
| 8.1 | max_bars_back up to 5000 | Ledger: `max_bars_back` is `const int` | limit value NOT verified here |
| 9.1 | camelCase, `Input` suffix | V3 style-guide sheet (M45) | consistent with official style guide |

## Verbatim Copilot text

# AGENTS.md – Pine Script v6 Engineering

Kennzeichnung: [A] = per Compiler oder Lauf in dieser Sitzung geprüft, [B] = Wert vom Chart abgelesen, [D] = Wissen ohne Prüfung. „unbekannt" heißt: nicht sicher, nicht geraten.
Testumgebung der geprüften Punkte: ein CFD-Goldchart, 1h.

## 1. Arbeitsablauf
1. Schreiben: Skript beginnt mit `//@version=6` und einer Deklaration (`indicator`, `strategy` oder `library`). [D]
2. Validieren: Das Ergebnis immer vollständig lesen. `valid: true` kann zusammen mit einem befüllten `errors[]` auftreten, also `errors[]` und `warnings[]` einzeln prüfen. [A]
3. Fehler an Zeile und Spalte beheben, dann erneut validieren, bis `errors[]` leer ist. [D]
4. Auf den Chart legen und die Plot-Werte der letzten Bars prüfen, nicht nur die Optik. [B]
5. Strategien: erst Report lesen (Trades, Profit Factor, Drawdown), dann Trades und Equity. Unter ca. 30 Trades sind die Kennzahlen kaum aussagekräftig. [D]
6. Aufrufe sparen: Nur wenige, gezielte Aufrufe pro Runde, mehrere Skripte in einem Durchgang prüfen. Beim Reparieren eine Änderung pro Runde. [D]
7. Debug-Plots mit `display = display.data_window` verwenden, wenn Werte nur ausgelesen und nicht gezeichnet werden sollen. [D]

## 2. Katalog: Compiler-Meldungen
Die Texte enthalten unaufgelöste Platzhalter in geschweiften Klammern, so wie sie zurückkamen.

| Meldung (wörtlich) | Fundort | Ursache | Korrektur |
|---|---|---|---|
| `Undeclared identifier "{identifier}"` | 3:6 (`plot(barstate.isclosed ? 1 : 0)`) [A] | Name existiert nicht. Hier ist `barstate.isclosed` nicht vorhanden, `barstate.isconfirmed` schon. | Namen gegen die Referenz prüfen. |
| `The "{signature}" function does not have an argument with the name "{name}"` | 3:13 (`plot(close, linewidth2 = 3)`) [A] | Benanntes Argument existiert nicht. | Parameter korrekt schreiben (`linewidth`). |
| `Cannot assign a value of the "{assignedValueType}" type to the "{variableName}" variable. The variable is declared with the "{ownValueType}" type.` | 3:1 (`int x = "abc"`) [A] | Literal passt nicht zum deklarierten Typ. | Typ oder Wert anpassen. |
| `The function "{functionName}" should be called on each calculation for consistency. It is recommended to extract the call from this scope` (Warnung) | 5:10 (`x := ta.ema(close, 10)` in einem `if`) [A] | Zustandsbehaftete Funktion in bedingtem Block. | Aufruf vor die Bedingung ziehen und das Ergebnis im Block verwenden. |

Weitere typische Meldungen (Wortlaut ungeprüft, daher unbekannt): Qualifier-Konflikt „series int statt simple int" bei `length`-Argumenten, „Mismatched input", Schleifen- und Einrückungsfehler. [D]

## 3. Typen und Qualifier
1. Reihenfolge der Qualifier: `const` → `input` → `simple` → `series`. Ein höherer Qualifier ersetzt keinen niedrigeren. [D]
2. Viele `ta.*`-Parameter wie `length` verlangen `simple int`. Ein Wert aus `input.int` passt, ein Wert aus Kursdaten (series) nicht. [D]
3. Lösung bei series-Längen: feste Länge verwenden oder die Berechnung selbst schreiben. [D]
4. `na`-Werte mit `na()` prüfen, nicht mit `== na`. [D]
5. In v6 werden `and`/`or` lazy ausgewertet. Zustandsbehaftete Funktionen deshalb vor der Bedingung berechnen. [D]
6. `na` nicht durch 0 ersetzen, wenn 0 eine eigene Bedeutung hat (zum Beispiel Kurswert). [D]

## 4. Ausführungsmodell
1. Historische Bars laufen einmal je Bar. Der Echtzeit-Bar läuft bei jedem Tick neu, Variablen werden vor jedem Tick auf den Stand des letzten Bar-Abschlusses zurückgesetzt (Rollback). [D]
2. `var` behält den Wert über Bars, wird aber auf dem offenen Echtzeit-Bar zurückgesetzt. `varip` behält ihn über Ticks. [D]
3. Mit `barstate.isconfirmed` lassen sich Signale auf geschlossene Bars beschränken. [D]
4. `barstate.isclosed` existiert nicht. [A]
5. `once` und `calc_on_every_history_tick` kompilieren in v6. Das Verhalten von `once` ist unbekannt: Der Zähler stand auf dem laufenden Bar nach kurzer Zeit bei 5, ohne Klärung der Ursache. [A][B]
6. `aggressor_side` und mehrzeilige Strings kompilieren. Die Semantik ist ungeprüft. [A]
7. `calc_on_every_tick` betrifft nur Strategien auf Echtzeit-Bars. Details unbekannt. [D]

## 5. Repainting und Multi-Timeframe
1. `ta.ema(close, 20)` liefert den ersten Wert ungleich `na` auf Bar 19, nicht auf Bar 0. [B]
2. Eine selbst gebaute EMA mit dem ersten Kurs als Startwert weicht davon ab (Differenz auf Bar 19: 8,48 in diesem Test). [B]
3. `ta.rsi` einer konstanten Reihe liefert auf dem letzten Bar 100. Das Verhalten in der Anlaufphase ist ungeprüft. [B]
4. Innerhalb von `request.security(..., "D", ...)` liefert `timeframe.in_seconds()` 86400, im Hauptkontext 3600. [B]
5. Ein globales `if timeframe.in_seconds() > 3600` mit `runtime.error` löste auf dem 1h-Chart keinen Fehler aus. Der Fehler wurde nicht im Tageskontext ausgelöst. Deutung (kein Beleg): Im HTF-Kontext läuft nur der übergebene Ausdruck. [B][D]
6. `request.security(..., "D", close[1], lookahead = barmerge.lookahead_on)` ist das Standard-Idiom für den Vortagswert. Gegen `dClose[1]` gab es in unserem Test 7 Abweichungen bei 234 Tageswechseln. Die Ursache ist unbekannt, ebenso, ob das ein Idiom-Problem oder ein Testartefakt ist. Eine Garantie für Repaint-Freiheit ist damit nicht belegt. [B]
7. Im Echtzeit-Test blieb `htfPrev` innerhalb des Tages gleich (0 Änderungen), nur kurze Beobachtung. [B]
8. Wochenenden, Sessionwechsel und Lücken (4 Stunden Abstand beim letzten Treffer) verändern, wann ein neuer Tag beginnt. Pine-Wochentage laufen in der Börsenzeitzone. [B][D]
9. `request.security_lower_tf` liefert ein Array je Chart-Bar. Details und Limits sind unbekannt. [D]
10. Für Wiederholbarkeit zusätzlich `barstate.isconfirmed` verwenden. [D]

## 6. Pivots und Marktstruktur
1. `ta.pivothigh(high, 2, 2)` liefert den Wert erst zwei Bars nach dem Kandidaten. Der Wert entsprach in 728 Fällen `high[2]`. [B]
2. Im Test gab es keinen Pivot mit höherem Nachbarn. Ein Fall mit gleichem Nachbarn trat auf, die Seite ist unbekannt. [B]
3. Beim Zeichnen vom Bestätigungsbar zurück zum Kandidaten (`bar_index - rightBars`) verschieben, aber nie so handeln, als wäre der Pivot dort schon bekannt. [D]
4. Pivots können sich auf dem offenen Echtzeit-Bar ändern, deshalb nur auf `barstate.isconfirmed` bestätigen. [D]

## 7. Strategien
1. Market-Orders füllen auf dem Open des nächsten Bars: 87 Trades, keiner außerhalb, Einstiegskurs gleich Open. [B]
2. Prozentuale Kommission: `Kommission = Prozentsatz · Menge · (Einstieg + Ausstieg)`, ohne Abweichung geprüft. [B]
3. Slippage war im Test 0. Wirkung ungeprüft. [D]
4. `process_orders_on_close = true` füllt auf dem Schlusskurs des Signal-Bars. Das ist optimistisch, ungeprüft. [D]
5. Bar-Magnifier und Bar-Detalization: Funktion und Planabhängigkeit unbekannt. [D]
6. Pyramiding ist standardmäßig 1. Im Test wurde mit `strategy.position_size == 0` abgesichert, Pyramiding selbst nicht geprüft. [D]
7. Typische Fallen: Repainting durch Lookahead, zu wenige Trades, ignorierte Kosten, Optimierung auf der Testhistorie, Equity gegen Buy-and-Hold. [D]

## 8. Grenzen und Performance
Zahlen nur, wo ich sicher bin. Alles hier ist [D], sonst unbekannt.
1. `max_bars_back` kann bis 5000 gesetzt werden. Der Wert wurde im Test gesetzt, die Grenze selbst nicht geprüft.
2. Anzahl `request.*`-Aufrufe, Zeichnungsobjekt-Limits (`max_lines_count` usw.), Plot-Anzahl und Laufzeit-Timeouts: unbekannt.
3. Schleifen sparsam einsetzen und `for`-Bereiche klein halten. Rechenintensive Berechnungen nicht in Schleifen über die ganze Historie legen. [D]
4. Bei `compile_timeout` nicht wiederholen, sondern melden und Skript vereinfachen. [D]

## 9. Stil und Lesbarkeit
1. Namen in camelCase, Inputs mit Suffix `Input`. [D]
2. Typen explizit deklarieren (`float`, `int`, `bool`). [D]
3. Inputs gruppieren (`group`) und mit `tooltip` und sinnvollen `minval`/`maxval` versehen. [D]
4. Aufbau: Deklaration → Inputs → Berechnung → Signale → Plots und Zeichnungen. [D]
5. Kommentare zu Annahmen, nicht zu Offensichtlichem. [D]
6. Jede wichtige Zahl im Skript erklärbar machen (Eingabe oder benannte Konstante). [D]

## 10. Checkliste vor Auslieferung
1. `//@version=6` und Deklaration vorhanden.
2. Letzte Validierung mit leerem `errors[]` gelesen, nicht nur `valid`.
3. Alle Warnungen gelesen und begründet behoben oder dokumentiert.
4. Zustandsbehaftete `ta.*`-Aufrufe außerhalb bedingter Blöcke.
5. `na`-Behandlung geprüft.
6. Keine Namen, die es nicht gibt (zum Beispiel `barstate.isclosed`).
7. Qualifier und `length`-Argumente geprüft.
8. Signale auf `barstate.isconfirmed` beschränkt, wo Echtzeit relevant ist.
9. `request.security`: Lookahead bewusst gewählt und getestet.
10. Pivots nicht zum Bestätigungsbar zurückdatiert gehandelt.
11. Plot-Werte auf den letzten Bars abgelesen.
12. Strategie: Kommission, Slippage, Pyramiding und Order-Zeitpunkt gesetzt.
13. Strategie: Report gelesen, Trade-Anzahl und Drawdown beurteilt.
14. Inputs gruppiert, mit Tooltips und sinnvollen Grenzen.
15. Aussagen ohne Prüfung als „ungeprüft" oder „unbekannt" markiert.
