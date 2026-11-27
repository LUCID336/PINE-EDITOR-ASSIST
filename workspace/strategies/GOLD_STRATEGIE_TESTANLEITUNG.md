# Gold Multi-Setup v7 – Strategie testen (Anleitung)

Datei: `releases/txt/gold_multi_setup_v07_strategy_v01.txt` (Pine v6, Strategie).
Status: lokal validiert (PineTS, synthetische Daten). **In TradingView noch nicht kompiliert und nicht getestet.**

## A) In TradingView (Strategy Tester)

1. Pine Editor öffnen → kompletten Inhalt der TXT einfügen → „Zum Chart hinzufügen".
2. Chart: **XAUUSD, 5 Minuten, normale Kerzen** (kein Heikin Ashi/Renko). Nimm möglichst das Symbol deines Brokers.
3. Einstellungen → Eigenschaften prüfen:
   - Kommission: 0.10 pro Kontrakt je Seite ≈ 2 Pips Spread pro Runde. An deinen echten Spread anpassen.
   - Slippage: 0 (Stresstest siehe Schritt 6).
   - Falls verfügbar: **Bar Magnifier** einschalten (bei 5m mit engen Stops entscheidet die Reihenfolge in der Kerze über TP1 oder SL).
4. Einstellungen → Eingaben:
   - **„Out-of-Sample ab"** VOR dem Anschauen der Ergebnisse auf ein Datum etwa in der Mitte der geladenen Historie setzen und notieren.
   - Mengen-Schritt: 1 (= 0.01 Lot bei 100 oz/Lot). Risiko je Trade: 100 $.
5. Ablesen:
   - Dashboard: pro Setup Trades, Gewinn-%, **Ø R ± 95 %** und Urteil (nur OOS, erst ab 100 Trades).
   - Strategy Tester: Übersicht und Liste der Trades. Jeder Teil-Ausstieg ist eine eigene Zeile (4 Zeilen pro Trade).
6. Kosten-Stresstest: Kommission auf 0.20 und 0.30 setzen, dann Slippage 3 Ticks. Bleibt Ø R im OOS positiv?
7. Wichtig: Parameter nicht anhand der OOS-Spalten verändern. Sonst ist das OOS kein OOS mehr.

Hinweise:
- Ohne Deep Backtesting lädt TradingView auf 5m nur begrenzte Historie. Erscheint „Keine In-Sample-Trades", liegt das OOS-Datum vor dem Datenbeginn.
- Ohne Deep Backtesting behält TradingView nur die letzten 9000 Trades (etwa 2250 Setup-Trades).

### Prompt für den TradingView AI Copilot (nur Kompilieren, nichts ändern)

```
Kompiliere bitte das folgende Pine-v6-Skript unverändert als Strategie und gib mir
1) alle Fehler und Warnungen wörtlich mit Zeile/Spalte,
2) ob es ohne Fehler auf XAUUSD 5m geladen werden kann,
3) falls du einen Backtest ausführen kannst: Netto-Gewinn, Anzahl geschlossener Trades, Profit-Faktor,
   Max-Drawdown und die Werte der Data-Window-Plots net_R_total, trades_counted, wins_counted,
   conflicts_skipped, entries_rejected am letzten Bar.
Ändere den Code nicht und schlage keine Parameteroptimierung vor.
<hier den Inhalt der TXT einfügen>
```

## B) Lokal mit deinen MT5-Daten (kostenlos, ohne TradingView)

1. MT5: Symbol XAUUSD → Rechtsklick „Symbole" → Balken → Zeitraum M5 → Abfragen → **Exportieren** (CSV).
2. Konvertieren (Serverzeit → UTC; die meisten Broker: New-York-Zeit + 7 h):
   ```
   python tools/convert_mt5.py XAUUSD_M5.csv data/xauusd_m5_utc.csv --server-tz nyclose
   ```
   Den Bericht prüfen: `first_utc`/`last_utc`, `gaps`, `spread_points.median` (Spread in Punkten; × 0.01 $ = Kosten pro oz und Runde).
3. Backtest (22 Monate ≈ 130 000 Bars brauchen etwa 2 Minuten und 6 GB RAM):
   ```
   python tools/pinelab.py run_backtest workspace/strategies/gold_multi_setup_v07_strategy.pine --data data/xauusd_m5_utc.csv --base-tf 5 --tf 5 --mintick 0.01 --heap-mb 6144 --timeout-s 600 --inputs "{\"Out-of-Sample ab\": 1735689600000}" --pretty
   ```
   (Den Wert für „Out-of-Sample ab" in Millisekunden UTC angeben, z. B. 1735689600000 = 01.01.2025.)

Grenzen des lokalen Laufs:
- PineTS ist nicht TradingView.
- Die 1h-EMA wird auf einem 24/7-UTC-Raster aus den 5m-Daten gebildet.
- Keine Bar-Magnifier-Daten: Fills innerhalb einer Kerze sind angenommen.
- Ergebnisse auf Broker-Daten gelten nur für diesen Broker-Feed.
