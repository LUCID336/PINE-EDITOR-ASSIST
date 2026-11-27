# Testplan — tatsächliche Runtime-Abnahme offen
| Gate | Test | Erwartung / Nachweis |
|---|---|---|
| T01 | Jeden API-Aufruf im offiziellen Reference Manual nachschlagen | versionierte Signatur, Overload, Qualifier, Status im Ledger |
| T02 | Alle vier .pine-Dateien separat im Pine Editor kompilieren | keine Fehler, Warnungen bewertet, Build/Datum dokumentiert |
| T03 | Hybrid auf 5m/60m/D mit HTF D bzw. W testen | HTF > Chart-TF; gleich/kleiner führt bewusst zu Fehler |
| T04 | offene Bar, Live-Barclose, Reload | bestätigte Features gleich außer Feed-Revision; provisional dokumentiert |
| T05 | Missing volume/zu kurze History | null/NA, MISSING, keine Aktion |
| T06 | Wechsel Chart/Session/Timezone, DST, Feiertag, 24/7 und Overnight | Unix-ms-Zeit und Source-Konsistenz |
| T07 | Human/AI-Modus gleiche Inputs und identischer Zeitraum | gleiches Feature CSV, UI nur Presentation |
| T08 | Dark/Light, Desktop/Mobile, Pane/Overlay, Chart Scaling | Text lesbar, keine Plot-Skalierungsverzerrung, keine überfüllten Labels |
| T09 | Alert auf alert() calls, Barclose, Webhook-Test | parsebares Schema; Snapshot neu erstellen nach Input-/Codeänderung |
| T10 | Duplikate, null, stale, out-of-order, HTTP-/Queue-Ausfall | Quarantäne, dedup, Reconcile, kein Live-Trade |
| T11 | Strategy auf Standard-OHLC, mit/ohne Bar Magnifier | Fill-Abweichungen erklärt, Gebühren/Slippage/Positionen überprüft |
| T12 | Chronologischer OOS, Parameter-Sensitivity, Kosten-Stress | vollständiges Trial-Ledger; keine Profitbehauptung ohne Beleg |
| T13 | Footprint auf berechtigtem und nicht berechtigtem Feed | Feature nur bei Daten; Tarif/fehlende Bars dokumentiert |
| T14 | Profiler für lange Historie, Limits für Plots/Requests | Ressourcenbudget eingehalten |
| T15 | Migration v1→v6 schrittweise an echten Legacy-Fixtures | Vergleichs-CSV nach jeder Version, keine stille Semantikänderung |

Lokale Tests T10 teilweise (Schema-/Semantik und Dedup), Quellen- und statische Checks durchgeführt. T01 vollständig, T02–T09, T11–T15 nicht als bestanden behaupten. Keine TradingView-Session mit Compiler oder Daten vorhanden. T12 benötigt reale Daten. Jeder Test muss mit Symbol, Exchange, TF, Datum, Script-Hash, Settings und beobachtetem Resultat dokumentiert werden.
