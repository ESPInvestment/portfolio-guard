# Portfolio Guard – Tageskurs-Versorgung (Vorbereitungsstand)

## Ist-Stand
- GitHub Pages zeigt das Dashboard; personenbezogene Daten liegen in Supabase, nicht im öffentlichen Repository.
- Die UI nimmt manuelle Einzelkurse oder CSV-Dateien (`isin,date,price,source`) entgegen.
- Es gibt **noch keinen automatischen Provider**, **keinen täglichen Job** und **keinen Server-Schlüssel**.
- Ein ISIN-Mapping ist nicht identisch mit einer validierten Kursabdeckung. Siehe `data/provider_coverage.csv`.

## Reihenfolge vor einem unbeaufsichtigten Tagesjob
1. Pro ISIN: Fondstyp, API-Symbol, Börsenplatz, Notierungswährung, eindeutigen Kurszeitstempel, verfügbare Aktualisierungsfrequenz und Nutzungsrecht durch echte API-Antwort belegen.
2. Insbesondere für DE0009770206 und LU1799928095 sind NAV-Veröffentlichungen und nicht zehnminütige Börsenkurse zu prüfen.
3. Quellen dürfen nicht heimlich gemischt werden: Kein Wechsel Börsenschluss ↔ NAV; ein Wechsel von Börsenplatz oder Währung benötigt eine neue Stop-Reihe.
4. Feeds in einer Nur-Lese-Testumgebung auf Fehlzuordnung, Nullwerte, Ausreißer, Wochenenden, fehlende Tage und Zeitstempel prüfen. Erst dann zum Import freigeben.
5. Der geplante Job soll nicht mit `service_role` direkt in private Tabellen schreiben. Stattdessen ein minimal privilegierter, serverseitig geprüfter Ingestionspfad mit Eigentümer-Zuordnung, Idempotenz und Audit-Log.
6. Bei fehlendem NAV/Kurs `stale` anzeigen, niemals einen fiktiven Preis erzeugen.
7. Kosten und Lizenzen vor Aktivierung erneut kontrollieren. Für den privaten Einsatz unter Free-Limits rechnen; keine Garantie auf 0 € bei jedem Anbieter.

## Testfälle der Stop-Engine
- Preisfolge 100,110,98 mit 10 % Abstand: Hoch 110, Stop 99, ausgelöst.
- Preis 101 am Folgetag: Alarm bleibt ausgelöst.
- Zweiter Preis mit gleichem Datum: abgewiesen.
- Älterer Kurs: abgewiesen.
- Zwei getrennte Supabase-Nutzer: keine gegenseitigen Positionsdaten.
- Wechsel der Stop-Distanz: Schwelle neu berechnen; Alarmzustand prüfen.
- Zeitverzögertes NAV: nicht als heutiger Kurs kennzeichnen.

## GitHub Actions
Ein Workflow ist derzeit absichtlich **nicht** geplant. GitHub Actions ist erst nach bestätigter Datenlizenz und validierten Symbolen für die einmal tägliche Ausführung sinnvoll. Die App funktioniert mit CSV-Fallback weiter.

## Sicherheits-Check
Der öffentliche `publishable`-Schlüssel ist kein geheimes Passwort; `service_role`, API-Secrets und Depotdaten dürfen nicht in `index.html`, GitHub-Dateien oder öffentlichen Logs liegen.
Die Supabase-RLS-Policies sollten separat geprüft werden, bevor der Job aktiviert wird.

## Anbieterentscheidung (16.11.2026)
- FMP Free: laut Anbieter nur US-Daten im Free-Paket, daher **nicht geeignet** für verlässliche kostenlose Abdeckung dieser zehn europäischen Fonds/ETFs. Quelle: https://site.financialmodelingprep.com/how-to/how-to-create-a-financial-modeling-prep-account
- EODHD Free: 20 Calls/Tag und ein Jahr EOD-Historie; laut Anbieter für Tests/Evaluation und persönliche Nutzung; das belegt **keine** Zulässigkeit des automatischen Dauerbetriebs oder vollständige ISIN/NAV-Abdeckung. Nicht aktiviert. Quellen: https://eodhd.com/help/plans und https://github.com/EodHistoricalData/eodhd-claude-skills/blob/main/skills/eodhd-api/references/subscriptions/free.md
- Kein Anbieter kann bislang für **alle zehn** Positionen auf Ebene echter API-Antworten plus Lizenzfreigabe bestätigt werden. Automatische Produktion bleibt deshalb gesperrt.

## Ohne API-Schlüssel jetzt nutzbar
- `python tools/validate_prices.py sample.csv` prüft die vorhandene CSV vor dem **manuellen** Import in die Web-App. Der Validator lädt **nichts hoch**.
- `python -m unittest discover -s tests -v` testet die Formatprüfung vollständig offline.
- Der GitHub-Workflow `check-daily-csv.yml` startet nur bei Pull Requests und manuell; **kein** täglicher Lauf, **keine** API- oder Supabase-Secrets.
- Die CSV-Prüfung verhindert Formatfehler, bestätigt aber weder Preiswahrheit noch Quellenlizenz, Währung, Umrechnung oder korrekte Kursart.
