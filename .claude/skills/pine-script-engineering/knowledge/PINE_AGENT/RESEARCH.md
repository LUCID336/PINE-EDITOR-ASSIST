# Pine Script Research — Engineering Handbook
Stand: 27.11.2026 | Ziel: autonomer, quellengestützter Coding-Agent | Primärsprache Deutsch, API-Namen Englisch.

## 1. Ziel, Erkenntnis und Grenzen
Pine ist eine spezialisierte Sprache für TradingView. Ein Script berechnet Marktmerkmale entlang einer Zeitreihe; es ist keine frei programmierbare Python-Laufzeit. **Was?** Indikatoren visualisieren oder emittieren Features; Strategien simulieren Orders; Libraries kapseln wiederverwendbare Funktionen und Typen. **Wo?** Pine Editor und TradingView-Server, mit Chart-, Alert-, Screener- und Backtest-Kontexten. **Warum?** Schneller Zugang zu Chartdaten und visuellen Experimenten. **Wozu nicht?** Beliebige HTTP-Anfragen, Dateisystem, dauerhafte Datenbank, echte Orderbuch-Rekonstruktion, ML-Training oder unabhängiges Broker-Risikomanagement. **Wie?** Version, Deklaration, Inputs, Berechnung, Outputs; die Plattform steuert die Ausführung. **Woher?** Offizielles Handbuch und versionspezifische Referenz (S01–S04). Kein garantiertes Alpha aus einem einzelnen API-Feature.

Entscheidung: v6 als Standard, v1–v5 als Legacy-Support. Eine vollständige Aufzählung aller historischen Overloads ist nicht belegt; das interaktive Referenzhandbuch war nicht vollständig extrahierbar. Der Agent muss fehlende Einträge einzeln verifizieren. Die Inhaltsnavigation ist vollständig indexiert; diese Aussage bezieht sich nur auf die sichtbaren 78 Einträge des v6-Handbuchs, nicht auf jedes Wort oder jeden Built-in.

## 2. Versionsgeschichte und Migrationsmatrix
| Version | Wichtige Merkmale / Risiko | Handlung |
|---|---|---|
| v1 | Frühe Syntax, historisches security-Verhalten | Altcode konservieren, via v2 migrieren; Referenzzugriff für v1 nicht bestätigt |
| v2 | Legacy security mit Lookahead-Verhalten; ältere Syntax | Vergleich von Zeitreihen; v3-Migration zwingend |
| v3 | Standard für security auf lookahead_off geändert | Audit jedes HTF-Requests und rekursiver Altvariablen |
| v4 | Typ-/Namespace- und Deklarationsänderungen, Zeichnungsobjekte | Migration guide und Referenz nutzen; Altfarben und Inputs prüfen |
| v5 | indicator statt study, ta/math/request/str u.a.; spezialisierte input.*; Libraries und neue Typen | Mapping nach API, named constants, color.new statt transp, Session-Tage prüfen |
| v6 | bool zweizuständig, lazy and/or, dynamische Requests standardmäßig, veränderte Strategie-Defaults, dynamische for-Grenze | Bool-NA durch expliziten Status ersetzen; historische Funktionen unbedingt auf jedem Bar auswerten; Margin und Exit-Semantik explizit setzen |

Warum sequenziell? Compilerkonversion kann Syntax ändern, aber keine semantische Gleichheit garantieren. Baseline mit symbol, timeframe, sessions, chart type, settings, Date Range und Plot-CSV speichern. Nach jeder Version Compile, Feature- und Signalvergleich, Abweichungen erklären. v1/v2 Legacy-Dokumentation ggf. nur über historische Guides zugänglich. v6-Release-Notes regelmäßig abrufen: z.B. bid/ask auf 1T, Footprint-Funktionen, Änderungen am Screener. Versionsnummer alleine pinnt nicht den Server-Compilerstand. Quellen S02, S03, S04, S05.

## 3. Sprache und Zeitreihenmodell
- Syntax: `//@version=6`, genau eine `indicator(...)`, `strategy(...)` oder `library(...)`; identifizierbare Namen, Einrückung für lokale Blöcke, `//` für Kommentar. `=` deklariert, `:=` weist neu zu, `+=` usw. ändern. Tuple-Destrukturierung `[a,b] = ...`; keine generischen Tuple-Objekte voraussetzen.
- Typen: int, float, bool, color, string; IDs für Objekte, chart.point, line/box/label/table/polyline/linefill, Arrays/Matrizen/Maps, UDT, enum. Referenztypen unterscheiden sich von skalaren Werten; Objektzuweisung kopiert oft nur die ID. Expliziter Typ bei `na`-Initialisierung (`float x = na`). `na(x)` statt Gleichheit mit `na`; `nz` nur bei sinnvoller Ersatzsemantik. Zero ist kein allgemeiner Missing-Wert.
- Qualifier: const < input < simple < series. Der stärkste abhängige Qualifier bestimmt das Ergebnis; eine series-Länge funktioniert nicht überall. Prüfe jede Signatur. `int` zu `float` oft implizit, `bool` in v6 nicht automatisch aus numerischen Werten. Nutze explizite Casts und Bedingungen.
- Historie: `x[1]` ist der vorige Bar-Wert der Serie, nicht Arrayindex. `array.get(a, i)` für Collection. Erste Bars sind oft unbestimmt; `bar_index` startet bei 0. `max_bars_back` bei dynamischen Offsets überprüfen, keine unnötig großen Puffer.
- Funktionen `f(x) => ...`, letzter Ausdruck Rückgabe, ggf. Tuple; lokale Variablen, explizite Parameter und Typen. Funktionen nicht rekursiv entwerfen; globalen skalaren Zustand nicht innerhalb UDF mutieren. Methoden mit getyptem erstem Parameter; exported functions nach Library-Regeln. UDT-Objekte sind nützlich für komplexe Zustände; enums verhindern String-Tippfehler. Arrays 0-basiert, vor Zugriff Größe prüfen; Maps für Keys; Matrizen für numerische Raster, keine grenzenlosen historischen Samples.
- Kontrollfluss: `if`, `else`, `switch`, `for`, `while`, `for ... in`, `break`, `continue`; Pine v6 short-circuit kann eine historienabhängige Berechnung überspringen, daher `cross = ta.crossover(a,b)` global, danach `if ready and cross`. Mutation der Schleifenendbedingung in v6 prüfen. Plot- und bestimmte Alert-Deklarationen müssen global bleiben; dynamische Sichtbarkeit über `na` oder Farbe lösen.

## 4. Runtime, Realtime, Rollback und Repainting
Auf historischen Bars entsteht üblicherweise eine Ausführung je Bar; Indikatoren rechnen auf Realtime-Updates erneut. Vor offenen-Bar-Updates rollt der Runtime-Zustand typischerweise zum bestätigten Zustand zurück. `var` initialisiert einmal pro Scope-Ausführung und persistiert barübergreifend, `varip` kann intrabar Änderungen behalten, die nach Reload aus OHLC-Historie nicht rekonstruierbar sind. Strategien rechnen standardmäßig am Barclose; abweichende Optionen beeinflussen Realtime und Broker-Emulator. Quellen S06–S08.

| Status | Verwendung | Gefahr |
|---|---|---|
| barstate.isfirst | Initialisierung | keine Aussage über erste Session |
| barstate.isnew | neuer Bar/alle historischen Bars | nicht gleich Barclose |
| barstate.isconfirmed | bestätigte Chartbar | nicht innerhalb request.security als HTF-Bestätigung einsetzen |
| barstate.islast | letzter Chartbar, UI | kann vielfach pro Bar laufen |
| barstate.isrealtime / ishistory | Ausführungsumgebung | kein vollständiger Tick-Replay |
| barstate.islastconfirmedhistory | schwere einmalige Analyse | Markt offen/geschlossen beachten |

Repainting-Taxonomie: (1) normale offene-Bar-Schwankung, (2) unbestätigte HTF-Werte, (3) echte Zukunftsleckage durch Lookahead ohne Offset, (4) rückdatierte Pivot-Marker, (5) intrabar-Zustand, (6) Feed-Revisionen oder andere Start-Historie, (7) synthetische Chartdaten. Bestätigung bedeutet nicht absolut unveränderliche Feedhistorie. Kennzeichne provisional und confirmed, teste reload und forward. Pivots mit right bars werden erst nach deren Ablauf bekannt: visualisiere Ursprung und Erkennungszeit getrennt, nie auf der Ursprungsbar handeln.

## 5. Multi-Timeframe und Datenquellen
`request.security` bewertet Ausdruck im Zielkontext, nicht bloß eine fertige Chartserie umskalieren. Für strikt höhere TF: `request.security(syminfo.tickerid, htf, close[1], lookahead=barmerge.lookahead_on)`; HTF per `timeframe.in_seconds` > Chart-TF absichern. Das ist der letzte bestätigte HTF-Bar; bewusst verzögert. `lookahead_off` ohne Offset verhindert nicht jede Realtime-Abweichung. `gaps_on` macht Lücken sichtbar, `gaps_off` füllt nach Kontext; nicht ungeprüft forward-fill für Feature Freshness einsetzen. Für niedrigere TF nutze `request.security_lower_tf` mit Arrays, prüfe leere Arrays, Intrabar-Coverage und History. Nicht jeden Tick rekonstruieren. Dynamische Requests: historisch alle später benötigten Kontexte zugänglich machen; neue Kontexte erst live können fehlschlagen. Batching mit Tupeln, deduplizierte Requests, Limits beachten.

| Familie | Zweck | Daten-/Zeitrisiko |
|---|---|---|
| request.security | andere TF/Symbole | Kontext, Sessions, Währung, verzögerte Feeds |
| request.security_lower_tf | Intrabar-Arrays | begrenzte Coverage, leere Arrays |
| request.currency_rate | FX-Konvertierung | tägliche Rate, kein tickgenauer Spread |
| request.financial / economic | Fundamentaldaten/Makro | Veröffentlichung, Revisionen, Point-in-time prüfen |
| request.dividends / splits / earnings | Corporate Actions | Ankündigungszeit vs Ereigniszeit; Adjustments |
| request.seed | vorhandene benutzergepflegte EOD-Feeds | kein allgemeines HTTP; Verfügbarkeit und Regeln prüfen |
| request.footprint | Footprint-Objekt, Reihen, Delta | Feed, Tarif, fehlende Bars, Klassifikation, nur eine Footprint-Anfrage pro Script gemäß aktueller Referenz |

Zeit: `time` ist Baröffnung, `time_close` Barende (auf manchen offenen nicht zeitbasierten Bars unbekannt). Unix ms; `syminfo.timezone` ist Exchange-Zeitzone, Chart-Anzeige nicht automatisch Script-Zeitzone. `time()` mit Session und IANA-Zone, `timeframe.change` für Reset; DST und Overnight-Sessions testen. TF-Strings unterscheiden Minuten und Monate (`60`, `1D`, `1M`); `timeframe.in_seconds` nur bei sinnvoll vergleichbaren TF. `ticker.*` konfiguriert Tickerkontext (Sessions, Adjustments, Heikin Ashi etc.); bei synthetischen Charts nicht aus synthetischem Preis realistische Fills ableiten. Quellen S08–S10.

## 6. Market Intelligence: Merkmale statt magischer Signale
| Merkmal | Berechnung/Definition | Nutzen-Hypothese / Gegenargument |
|---|---|---|
| Trend/EMA/SMA | Glättung von Preis, Steigung ATR-normalisiert | Trendfilter; lag, whipsaw |
| Momentum | ROC, RSI, MACD, Stochastik | Fortsetzung/Reversal abhängig vom Regime |
| Volatilität | TR, ATR, stdev, Bollinger/Keltner, Range/Preis | Skalierung; sprunghafte Volatilität, nicht Richtung |
| Volumen/RVOL | volume / rollender Durchschnitt bei >0; session-relative Vergleichbarkeit | Aktivitätsanomalie, keine Aggressor-Information |
| VWAP | kumuliertes Preis×Volumen / kumuliertes Volumen mit definiertem Anchor | Referenz für Intraday-Preis; kein fairer Wert garantiert |
| Market structure | bestätigte Swing highs/lows; BOS/CHOCH als explizite Break-Regeln | struktureller Kontext; Pivot-Lag, Definitionsabhängigkeit |
| Liquidity proxy | Equal highs/lows mit Tick-/ATR-Toleranz, prior session extremes, Sweep = Durchbruch + Reentry | Hypothese über Stops; keine Kenntnis realer Stop-Orders |
| S/R und Zonen | bestätigte Pivots, Rangegrenzen, Abstände und Retest | Level-Kontext; subjektive Parametrisierung |
| FVG proxy | bullish `low > high[2]`, bearish `high < low[2]`, Mindestgröße und Fill-Regel | Preisungleichgewicht als Kerzenmuster, keine Orderbuchlücke |
| Order block proxy | dokumentierte letzte Gegenkerze vor Impuls, invalidiert durch feste Regel | Hypothese, keine Beobachtung institutioneller Orders |
| Delta/CVD | Summe klassifizierter buy minus sell Volumes, CVD mit definiertem Reset | Aktivitätsasymmetrie; Feed und Klassifikation können Resultate ändern |
| Footprint | POC, Value Area, Imbalance, Delta je Preisreihe | Preis/Volumen-Aktivität; nicht DOM oder Liquidation Heatmap |
| OI | Feedwert, Veränderung, Einheit und Kontrakt berücksichtigen | Positionierungsänderung; keine eindeutige Long/Short-Richtung |
| Funding/Basis | Funding-Zeitplan bzw. (perp−spot)/spot | Carry und Stress; Venue-spezifisch, Rate und Einheit prüfen |
| Korrelation/Relative strength | Renditen synchronisieren, rolling corr, Beta/Spread | Kontext, kein Kausalbeweis; Regimewechsel |
| Session/Events | Asia/Europe/US, Opening Range, bekannte Ereignisse | Zeitabhängige Liquidität; DST, Feiertage, Kalender-Revisionen |

Weitere Feature-Kandidaten: ADX/DMI, Supertrend, Ichimoku (Displacement beachten), Donchian, Aroon, MFI, OBV, CMF, regression slope, z-score, percentile rank, entropy/autocorrelation (extern gegenprüfen), anchored VWAP, prior day/week levels, gap statistics, relative strength, realized volatility. Ein Feature muss eine konkrete Hypothese mit Ablation, Kosten und OOS-Test tragen. Stark korrelierte Indikatoren sind keine unabhängige Confluence. Keine pauschalen Gewichte.

### Native vs Proxy vs External
OHLCV und Symbolmetadaten sind nativ im Feed, fehlende volume-Werte möglich. Footprint seit v6 als API verfügbar (S11), klassifiziert laut Pine-Dokumentation Intrabar-Volumen nach Preisbewegung; nicht automatisch exchange-seitiges Aggressor-Delta. Die Plattform hat auch tickbasierte Modi bei bestimmten Daten/Indikatoren (S12); nicht ungeprüft auf Pine übertragen. `bid`/`ask` auf 1T sind keine L2-Historie. OI, Funding und Liquidation-Symbole nur bei nachweislich verfügbaren Feeds und korrekter Zeit/Einheit verwenden. Extern: echte L2/L3-Orderbooks, Trades mit Aggressor, Liquidation-Events, venueübergreifende Heatmaps, News und ML-Features. Feeds über autorisierte Exchange-APIs/Provider extern synchronisieren. Pine kann keine beliebigen REST-Feeds konsumieren. Keine Schätzung als echte Messung labeln. Datenqualität pro Feature: NATIVE / PROXY / EXTERNAL / MISSING, Methodik, Zeit, Einheit, Venue und Freshness.

## 7. Quantitative Strategieentwicklung
Hypothese vor Test festlegen. Signal-Zeit und Order-Zeit unterscheiden. Beispiel: Trendfilter auf bestätigtem HTF, LTF-Crossover als Trigger, SL/TP aus vorab festgelegter Regel, invalidiert bei Strukturbruch. Das ist nur ein Testkandidat. `strategy.entry` kann Positionen umkehren; `strategy.order` hat andere Netting-Semantik; `strategy.exit` erzeugt preisbasierte Exits, `strategy.close`/`close_all` Markt-Exits; `strategy.cancel` entfernt offene Orders. Achte auf Entry-ID, OCA, reservierte Teilmengen, Pyramiding, `strategy.position_size`, Tickgröße, Pointvalue, Margin und Mindest-Lot. Stop-Limit ist nicht Stop plus Take-Profit. Relative Exit-Distanzen sind in Ticks; absolute `stop`/`limit` sind Preise. Prüfe v6-Migration, wenn beide Varianten angegeben sind.

Broker emulator arbeitet mit OHLC-Annahmen, Market Orders standardmäßig am nächsten verfügbaren Tick (historisch oft nächster Open). `process_orders_on_close`, `calc_on_every_tick`, `calc_on_order_fills`, `use_bar_magnifier` nur bewusst aktivieren; Bar Magnifier hat begrenzte LTF-Daten und keine echte Queue-Simulation. Gebühren, Slippage in Ticks, Funding, Spread, Liquidations-/Marginregeln und Limit-Fill-Annahmen sind getrennt zu modellieren. Stop kann bei Gaps schlechter ausgeführt werden. Kein Produktions-Risk über simulierte Orders.

Sizing: Cash-Risk = equity × risk_fraction; theoretische Menge = Cash-Risk / (abs(entry−stop) × pointvalue × FX-Faktor), anschließend Lot abrunden, Gebühren, Margin, Leverage und instrument-spezifische PnL-Formeln berücksichtigen (inverse Kontrakte nicht linear). Null-/NA-Abstände blockieren. R:R = reward/risk vor Kosten, netto gesondert. Max drawdown aus Equity-Höchststand; Expectancy = Mittel der Netto-PnL je Trade oder R; Profit Factor = Bruttogewinn / abs(Bruttoverlust), undefiniert ohne Verlust; Sharpe/Sortino nur mit definierter Renditefrequenz, rf, Annualisierung und Abhängigkeiten. Winrate ohne Auszahlungsverhältnis nutzlos. Keine Kennzahl ohne Stichprobengröße.

Validierung: chronologische Train/Validation/Test-Splits, Walk-forward mit festen Parametern pro Fenster, Label-Overlaps purgen/embargo wenn relevant, Holdout nur einmal verwenden, alle Versuche loggen. Benchmark Buy&Hold plus einfache Regeln. Ablation einzelner Features, Parameter-Nachbarschaft, Kosten- und Slippage-Stress, verschiedene Symbole/Regimes, Block-Bootstrap bei Autokorrelation. PBO und Deflated Sharpe berücksichtigen die Such-/Auswahlverzerrung (S17/S18); keine automatisch garantierte Signifikanz. Externe Statistik berechnen, nicht vortäuschen. Forward/Paper-Test mit Live/Backtest-Differenz. Acceptance vorher definieren: Kostenannahmen, Mindeststichprobe, Drawdown, OOS-Vorteil, Datenvollständigkeit und Robustheit; keine universelle Schwelle. Falls nicht nachgewiesen: NO TRADE.

## 8. Human vs AI — eine Feature-Engine, zwei Ausgabeformen
HUMAN: Overlay für wenige relevante Levels/Trigger; separate Pane für nicht preisgleiche Einheiten; maximal eine kompakte Status-Tabelle, Details optional. Nicht Farbe allein nutzen; beschriftete Long/Short/Neutral/No data. Transparenz, Linienbreite, Dark/Light-Kontrast, Tooltips, konsistente Rundung. Inputs in Gruppen (Data, Signal, Risk, Visuals, Debug), `minval`/`maxval`/`step` und sprechende Defaults. Keine überzeichneten historischen Labels; limitierte Objekte und explizite Löschung. Tabelle mit `var table`, Update auf `barstate.islast`; Berechnungen außerhalb des UI-Blocks. `plot`, `plotshape`, `plotchar`, `plotarrow`, `plotbar`, `plotcandle`, `hline`, `fill`, `bgcolor`, `barcolor`, line/box/label/polyline/linefill für verschiedene Darstellungsebenen. Plot titles stabil, `force_overlay` bei Bedarf verifizieren. Quellen S13/S14.

AI: Stable feature IDs, numerische Rohdaten statt Screenshot-Erkennung; separate Spalten für Wert, Einheit, Quelle, Quality und Timestamp. `display.data_window` für Inspektion und Plot-CSV, `display.none` für versteckte Plots/Platzhalter oder externe Input-Verwendung; prüfe Exportverhalten pro Chart. `input.source` koppelt ausgewählte Plots, kein beliebiger bidirektionaler Datentransfer. `alert()` mit dynamischem JSON, bestätigter Barclose als Default. `alertcondition` global, const message und Platzhalter; Strategien haben Orderfill-Alerts. Alert muss vom Nutzer erstellt werden, ist ein Snapshot von Script/Inputs/Chart; nach Änderung neu erstellen. Webhook outbound, kein Pine-HTTP-Client. CSV für historischen Backfill, Webhook für Live-Ingestion; Abgleich mit eindeutigen Keys, Backfill und Replay. Keine Annahme lückenloser Delivery. Extern: queue → schema validation → dedup → persistent event log → feature store → agent → optional risk gateway. Secrets nie in Pine oder Payload; keine direkte Orderaktion aus ungeprüftem Alert.

Pine Screener: Scan über unterstützte Symboluniversen/TF, Plots als Filter/Spalten, letzte 500 Bars laut Support; jüngste offizielle Ankündigung hebt Request-Limit auf 40 an (S15), ältere 5-Call-Angaben nicht blind übernehmen. Plan-/Feature-Gating und tatsächliche UI prüfen. Screener ist keine unbeschränkte Streaming-Datenbank. Siehe AI_PROTOCOL für Vertrag und Beispiele.

## 9. Performance, Tests, Fehler und Bibliotheken
Ressourcenbudget: nach aktueller offizieller Limit-Seite bis 64 Plot-Counts (nicht 64 Funktionen), 40 eindeutige request-Aufrufe bzw. 64 auf Ultimate, 127 Tuple-Elemente über Requests, 100000 Collection-Elemente (Map-Key/Value zählen getrennt), 500 ms Loop je Bar plus Gesamtzeitlimit; tatsächliche Grenzen sind plan-/versionsabhängig (S16). Begrenze Requests, batch tuples, nutze built-in ta-Funktionen statt unnötiger Schleifen, setze `calc_bars_count` bedacht, bounded queues, Zeichnungsobjekte updaten statt unendlich neu erstellen. Profiler und Pine Logs sind Messinstrumente; Debug-Ausgaben abschaltbar. `runtime.error` für ungültige Konfiguration, nicht für gewöhnliche Datenlücken. Lint ersetzt keine tatsächliche Kompilierung.

Libraries: `library`, `export` getypte Parameter, Dokumentationsannotationen, import mit Version, Dependency-Ledger. Tests müssen Nutzerkontext und Bibliothekskontext abdecken. Keine unlizenzierte Wiederverwendung; offene Scripts sind nicht automatisch gemeinfrei. Dokumentiere Inputs, side effects, version, units, complexity, warm-up, `na`, example, expected result. Publishing-Rules vor Veröffentlichung prüfen.

## 10. W-Fragen für jeden neuen Built-in / jedes Feature
Was ist der Zweck? Wie lautet die exakte Signatur und welcher Overload? Wie und wann wird gerechnet? Welche Typen/Qualifier sind zulässig? Wo gilt der Scope? Woher stammen Daten? Welcher Markt/Plan/Version? Wieso ist die Funktion hier besser als Alternativen? Warum könnte sie fehlschlagen? Wann ist Output verfügbar? Wieviel Historie, Latenz, Ressourcen? Woran erkennt man korrekte Ergebnisse? Welche Edge Cases, `na`, Null, Repaint, Side Effects? Wofür ist sie ungeeignet? Wie verifiziert man Output unabhängig? Welche Änderung bricht Kompatibilität? Das muss je benutztem Symbol im API-Ledger beantwortet werden, nicht aus Modellgedächtnis geraten.

## 11. Lernprogramm und Fertigstellung
Stufe A: Pine-Typen und Runtime anhand kleiner Scripts; B: sämtliche Manual-Kapitel über Index, UDF/Collections/Visuals; C: alle benutzten Built-ins einzeln gegen Referenz; D: MTF, Repaint, Alerts und Datenqualität; E: Strategie- und Statistik-Validierung; F: Human/AI-Parität und Release. Für jede Stufe Testbeleg und Fehlerjournal. Die 6 Audit-Pässe dieses Pakets stehen in `audit/LOOPS.md`; noch ausstehende vollständige Symbolinventarisierung, Referenzprüfung und TradingView-Tests in `audit/OPEN_ITEMS.md`. Kein 100%-Label, wenn Quellen oder Tests fehlen.
