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
