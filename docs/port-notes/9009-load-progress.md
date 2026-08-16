# 9009 — Fortschrittsanzeige beim Laden

**Status:** fertig
**Patch:** `patches/9009-load-progress.patch`
**Umfang:** 8 Dateien

---

## Absicht

Das Kopieren einer Erweiterung dauert rund eine Minute. Vorher passierte in
dieser Zeit sichtbar nichts. Jetzt zeigt ein Overlay einen Balken mit
Prozentwert und der Zahl der kopierten Dateien.

---

## Aufbau

Sechs Ebenen, von unten nach oben:

| Ebene | Datei |
|---|---|
| Fortschritt melden | `developer_private_functions.cc` (Teil von 9003) |
| Ereignis deklarieren | `chrome/common/extensions/api/developer_private.webidl` |
| Typen für TypeScript | `tools/typescript/definitions/developer_private.d.ts` |
| Ereignis abholen | `chrome/browser/resources/extensions/service.ts` |
| Schnittstelle | `chrome/browser/resources/extensions/item.ts` |
| Zustand und Anzeige | `manager.ts`, `manager.html.ts`, `manager.css` |
| Auslöser | `toolbar.ts` |

Die Werkzeugleiste meldet per Ereignis `load-progress` mit wahr oder falsch, wann
geladen wird. Der Manager hält den Zustand und zeichnet das Overlay. Der
Prozentwert kommt getrennt davon über das neue `developerPrivate`-Ereignis
`onCopyProgress` mit `copied` und `total`.

---

## Stolpersteine

**Das Schema liegt als `.webidl` vor.** Seit 149 nicht mehr als `.idl` oder
`.json` — Suchen nach dem alten Format laufen ins Leere.

**Die TypeScript-Typen kommen nicht aus dem Schema.** Sie stehen in der
handgepflegten Datei `tools/typescript/definitions/developer_private.d.ts`. Wer
das Schema ergänzt und diese Datei vergisst, bekommt drei Fehler im
TypeScript-Schritt.

**Die Schnittstelle wird in `item.ts` deklariert**, nicht in `service.ts`. Dort
steht auch eine Platzhalter-Implementierung, die mit ergänzt werden muss, sonst
schlägt die Typprüfung fehl.

**Das Ereignis muss nicht über den `DeveloperPrivateEventRouter` laufen.** Ein
`EventRouter::Get(browser_context())->BroadcastEvent(...)` direkt aus der
Funktion spart zwei angefasste Dateien. Als Histogrammwert wird ein vorhandener
mitbenutzt, damit `extension_event_histogram_value.h` unberührt bleibt — die
Statistik wertet hier ohnehin niemand aus.

---

## Positionierung

Der erste Entwurf war ein Overlay mit `position: fixed` und `inset: 0`. Auf dem
Telefon saß es außerhalb des sichtbaren Ausschnitts.

Ein `cr-dialog` half nicht: Ein `<dialog>` zentriert sich im **Layout**-Ansichts-
fenster, nicht im sichtbaren. Die Erweiterungsseite ist für Desktop gebaut und
damit breiter als der Bildschirm; die Mitte der Seite liegt außerhalb dessen, was
man sieht. Chromiums eigene Dialoge verhalten sich genauso — der Fehlerdialog
erscheint ebenso abgeschnitten.

Die Lösung ist eigener Code: Das Overlay wird per JavaScript an
`window.visualViewport` ausgerichtet.

```ts
overlay.style.left = `${viewport.offsetLeft}px`;
overlay.style.top = `${viewport.offsetTop}px`;
overlay.style.width = `${viewport.width}px`;
overlay.style.height = `${viewport.height}px`;
```

Dazu Zuhörer auf `resize` und `scroll` des `visualViewport`, solange die Anzeige
läuft. Damit deckt das Overlay genau den sichtbaren Bereich ab und zieht beim
Zoomen und Verschieben mit.

Das ist ein Eingriff, den Chromium nirgends macht — dafür ist es eigener Code an
einer Stelle ohne fremde Struktur, und der lässt sich beim Versionssprung besser
übertragen als eine angepasste Fremdkomponente.

---

## Gesamtzahl der Dateien

Ein Zähldurchlauf vor dem Kopieren liefert `total`. Er kostet drei bis vier
Sekunden; solange bleibt der Balken unbestimmt, danach springt er auf echte
Prozente.

**Der Durchlauf muss `FILES | DIRECTORIES` anfordern.** Mit `FILES` allein zählt
er über SAF nur die oberste Ebene — im Test 23 statt 655 — weil
`ListContentUriDirectory` den `file_type_` durchreicht und ohne Verzeichnisse
keine Rekursion stattfindet.

---

## Anmerkung zum Zuschnitt

Ursprünglich waren zwei Patches geplant: unbestimmter Balken und Prozentanzeige
getrennt, damit beim Versionssprung nicht beides auf einmal bricht. Das ließ sich
nicht durchhalten — die Aufteilung erfolgt nach Dateien, und beide Teile teilen
sich `manager.*`. Der C++-Anteil der Fortschrittsmeldung liegt deshalb in 9003,
alles Übrige in 9009.
