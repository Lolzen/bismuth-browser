# 9003 — Erweiterungen in den App-Speicher übernehmen

**Status:** fertig, auf 151 bestätigt
**Patch:** `patches/9003-extension-copy-on-load.patch`
**Umfang:** 2 Dateien

---

## Absicht

Eine über den Android-Ordnerpicker geladene Erweiterung soll **nicht dauerhaft
hinter dem Storage Access Framework laufen**, sondern beim Laden einmalig in den
App-Speicher übernommen werden.

---

## Warum das nötig ist

**Geschwindigkeit.** Jeder Dateizugriff über SAF kostet einen Binder-IPC an den
Document Provider. uBlock Origin besteht aus 655 Dateien, und Chromium prüft
entpackte Erweiterungen bei jedem Start.

```
mit uBlock ueber SAF        33 Sekunden Startzeit
ohne uBlock                  1 Sekunde
mit uBlock im App-Speicher   3 Sekunden
```

**Beständigkeit.** SAF-Pfade überleben einen Neustart nicht.

Kiwi hatte dieses Problem nie — dort kamen Erweiterungen aus dem Store. Seit der
Store MV2 nicht mehr ausliefert, ist der lokale Ladeweg der einzige.

---

## Wohin kopiert wird

```
app_chrome/BismuthExtensions/<hash>-<zeitstempel>
```

**Eine Ebene über dem Profil**, neben Chromiums eigenen Komponentenverzeichnissen
wie `OriginTrials` und `OptimizationHints`.

Das war nicht immer so, und der Weg dorthin hat drei Versionen gedauert. Bis 151
lag das Ziel unter `<Profil>/UnpackedExtensions` — und dort verschwanden die
Kopien immer wieder. Mal nach Stunden, mal nach einem Neustart, ohne eine
einzige Chromium-Zeile im Protokoll. Auf 151 war das Verzeichnis nach
mehrmaligem Ab- und Anschalten schlicht leer.

Das Profil ist Chromiums Revier, und es räumt dort auf, was es nicht kennt. Seit
der Umzug eine Ebene höher erfolgt ist, hält es.

**Nebenwirkung:** Ein Wechsel des Zielpfads entwertet alle bisherigen
Registrierungen. Erweiterungen müssen danach einmal neu geladen werden.

---

## Aufbauen wie ein CRX

Der Kopiervorgang legt die Dateien in `<Profil>/Temp/<name>` an und setzt sie erst
am Ende mit einem einzigen `base::Move` an ihren Platz.

Das ist der Ablauf, den Chromium beim Installieren eines CRX verwendet
(`extensions/common/file_util.cc`, `InstallExtension`): außerhalb des
Zielbereichs aufbauen, dann mit einem Umbenennen einsetzen.

Wird direkt im Ziel aufgebaut, verschwinden Teile der Kopie noch während des
Kopierens. Der Zähler meldete 655 geschriebene Dateien, im Ziel lagen
anschließend vier Verzeichnisse. Eine Zwischenmeldung zeigte, dass
`manifest.json` nach dem Schreiben zunächst existierte und im Verlauf verschwand.

---

## Umsetzung

`DeveloperPrivateLoadUnpackedFunction::StartFileLoad` ist in drei Teile zerlegt:

```
StartFileLoad        loest die content-URI auf, vergibt die Retry-Kennung,
                     stoesst das Kopieren im Thread-Pool an
OnCopyComplete       Rueckruf, ruft ContinueFileLoad mit dem Zielpfad
ContinueFileLoad     der urspruengliche Rumpf mit UnpackedInstaller
```

Das Kopieren darf nicht im UI-Thread laufen — 655 Dateien über SAF hätten einen
ANR ausgelöst.

**`base::CopyDirectory` scheidet aus:** Es öffnet Quelldateien mit dem rohen
Syscall `open()`, was bei einem `/SAF/`-Pfad scheitert. Die eigene Schleife
benutzt `base::File` zum Lesen und `base::WriteFile` zum Schreiben.

Vor jedem Schreibvorgang wird `base::CreateDirectory(target.DirName())`
aufgerufen, weil der Aufzähler keine Reihenfolge garantiert.

---

## Verwaiste Kopien aufräumen

Chromium löscht das Verzeichnis einer entpackten Erweiterung beim Entfernen
nicht. Da jeder Ladevorgang einen eigenen Zeitstempel bekommt, sammelten sich die
Verzeichnisse an — in einem Protokoll scheiterten beim Start fünf Ladeversuche
aus verwaisten Ordnern.

Nach erfolgreichem Verschieben werden deshalb Geschwisterverzeichnisse mit
demselben Hash entfernt.

**Nicht erfasst:** Verzeichnisse von Erweiterungen, die ganz entfernt wurden.
Dafür bräuchte es die Liste der installierten Erweiterungen aus dem UI-Thread.

---

## Fortschrittsmeldung

Vor dem Kopieren zählt ein eigener Durchlauf die Dateien, danach meldet die
Schleife alle zehn Dateien den Stand über den UI-Thread. Die Anzeige gehört zu
9009.

**Der Zähldurchlauf muss `FILES | DIRECTORIES` anfordern.** Über SAF reicht
`ListContentUriDirectory` den `file_type_` an die Auflistung durch — mit `FILES`
allein kommen keine Unterverzeichnisse zurück, die Rekursion bleibt aus, und
gezählt werden nur die Dateien der obersten Ebene. Der Fehler ist still.

---

## Sackgassen

**Staging im Zielverzeichnis.** Erster Versuch: ein Nebenverzeichnis
`<hash>.staging` neben dem Ziel, danach `base::Move`. Lag im selben gefährdeten
Bereich; das Umbenennen meldete Erfolg und hinterließ eine unvollständige Kopie.

**Eindeutiges Zielverzeichnis allein.** Der Zeitstempel verhindert Kollisionen —
den Fehler behob er nicht. Er bleibt, weil er nichts kostet und den Aufräumlauf
erst möglich macht.

**Zweiter Durchgang über die Wurzeldateien.** Notlösung, die das Symptom milderte
und nicht die Ursache traf. Entfernt.

---

## Offen

**Sporadischer Fehlschlag beim ersten Laden.** Eine Wiederholung behebt es.

---

## Lehre

Zweimal wurde hier die falsche Ursache repariert, weil eine Vermutung schneller
war als eine Messung. Beim Kopierfehler kostete das vier Umbauten; beim
Verschwinden der Verzeichnisse drei Versionen. Beide Male brachte erst eine
Beobachtung die Wende — eine Zwischenmeldung im Kopierlauf, und die schlichte
Frage, ob das Verzeichnis vor oder nach dem verdächtigen Ereignis leer war.
