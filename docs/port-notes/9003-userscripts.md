# 9003 — User-Scripts (PersonalizeResults)

**Status:** TBD — noch nicht untersucht
**Basis:** Chromium 149.0.7827.238

---

## Absicht

Kiwis Mechanik zum Einschleusen eigener Skripte in Seiten. Als KEEP eingestuft, weil sie überwiegend aus Eigencode besteht und damit wenig Angriffsfläche für den Versionssprung bietet.

## Kiwis Umsetzung (Chromium 105)

- 7 Commits
- Eigencode: `chrome/android/java/src/org/chromium/chrome/browser/PersonalizeResults.java`
- Der Rest ist Verdrahtung — die Injection-Punkte in Chromium-Code sind noch nicht kartiert

## Umsetzung in 149

Noch offen. Zu klären:

1. Was `PersonalizeResults.java` tatsächlich tut — Inhalt lesen, nicht vom Namen ableiten
2. Wo Kiwi die Injection anstößt: `git log b2a61e552c94..kiwi -- '*PersonalizeResults*'` in `upstream/src.next`
3. Ob die Ziel-APIs in 149 noch existieren

## Anmerkung

Sollte nach Meilenstein 9001 angegangen werden. Falls Erweiterungen laufen, deckt eine User-Script-Extension denselben Zweck möglicherweise vollständig ab — dann wäre dieser Punkt hinfällig. Vor der Umsetzung also erst prüfen, ob er noch gebraucht wird.
