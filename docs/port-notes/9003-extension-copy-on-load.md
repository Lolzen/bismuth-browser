# 9003 — Erweiterungen in den App-Speicher übernehmen

**Status:** fertig
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

**Beständigkeit.** SAF-Pfade überleben einen Neustart nicht:

```
Fehler beim Laden der Erweiterung aus: /SAF/com.android.externalstorage.documents/tree/…
Manifest-Datei fehlt oder ist nicht lesbar
```

Kiwi hatte dieses Problem nie — dort kamen Erweiterungen aus dem Store und lagen
im Profilverzeichnis. Seit der Store MV2 nicht mehr ausliefert, ist der lokale
Ladeweg der einzige, und damit wird die Übernahme in den App-Speicher zur
Voraussetzung dafür, dass Erweiterungen überhaupt bestehen bleiben.

---

## Umsetzung

`chrome/browser/extensions/api/developer_private/developer_private_functions.cc`

`DeveloperPrivateLoadUnpackedFunction::StartFileLoad` wird in drei Teile zerlegt:

```
StartFileLoad        loest die content-URI in einen /SAF/-Pfad auf, vergibt
                     die Retry-Kennung und stoesst das Kopieren im Thread-Pool an
OnCopyComplete       Rueckruf, ruft ContinueFileLoad mit dem Zielpfad
ContinueFileLoad     der urspruengliche Rumpf mit UnpackedInstaller
```

Das Kopieren **darf nicht im UI-Thread laufen** — 655 Dateien über SAF hätten
sonst einen ANR ausgelöst. Deshalb
`base::ThreadPool::PostTaskAndReplyWithResult`.

### Aufbauen wie ein CRX

Der Kopiervorgang legt die Dateien **in `<Profil>/Temp/<name>` an** und setzt sie
erst am Ende mit einem einzigen `base::Move` an ihren Platz unter
`<Profil>/UnpackedExtensions/<hash>-<zeitstempel>`.

Das ist genau der Ablauf, den Chromium beim Installieren eines CRX verwendet
(`extensions/common/file_util.cc`, `InstallExtension`): außerhalb des
Zielbereichs aufbauen, dann mit einem Umbenennen einsetzen.

**Warum das zwingend ist:** Wird direkt im Zielbereich aufgebaut, verschwinden
Teile der Kopie noch während des Kopierens wieder. Der Zähler meldete 655
geschriebene Dateien, im Ziel lagen anschließend vier Verzeichnisse. Eine
Zwischenmeldung zeigte, dass `manifest.json` nach dem Schreiben zunächst
existierte und im Verlauf verschwand — alles vor einem bestimmten Zeitpunkt war
weg, alles danach blieb.

Reproduzierbar war das nur **direkt nach einem inkrementellen APK-Update**, also
genau dann, wenn vorher eine Erweiterung entfernt und neu geladen wurde. Der
Verursacher ließ sich im Protokoll nicht nachweisen; im fraglichen Zeitfenster
stand keine einzige Chromium-Zeile. Mit dem Aufbau außerhalb des Zielbereichs
tritt der Fehler nicht mehr auf.

### Verwaiste Kopien aufräumen

Chromium löscht das Verzeichnis einer entpackten Erweiterung beim Entfernen
**nicht** — normalerweise gehört es dem Nutzer. Bei uns gehört es der App, und
da jeder Ladevorgang einen eigenen Zeitstempel bekommt, sammelten sich die
Verzeichnisse an. In einem Protokoll scheiterten beim Start bereits fünf
Ladeversuche aus verwaisten Ordnern.

Nach erfolgreichem Verschieben werden deshalb alle Geschwisterverzeichnisse
gelöscht, deren Name mit demselben Hash beginnt. Das erfasst die wiederholten
Zeitstempel-Varianten derselben Quelle, ohne Zugriff auf die
Erweiterungsverwaltung zu brauchen.

**Nicht erfasst:** Verzeichnisse von Erweiterungen, die ganz entfernt wurden.
Dafür bräuchte es die Liste der installierten Erweiterungen, und die ist nur im
UI-Thread erreichbar.

### Warum keine Standardfunktion

`base::CopyDirectory` scheidet aus: Es öffnet Quelldateien mit dem rohen Syscall
`open()`, was bei einem `/SAF/`-Pfad scheitert. Die eigene Schleife benutzt
`base::File` zum Lesen und `base::WriteFile` zum Schreiben — beide sind
SAF-fähig.

Zusätzlich wird vor jedem Schreibvorgang `base::CreateDirectory(target.DirName())`
aufgerufen, weil der Aufzähler keine Reihenfolge garantiert.

### Fortschrittsmeldung

Vor dem Kopieren zählt ein eigener Durchlauf die Dateien, danach meldet die
Schleife alle zehn Dateien den Stand über den UI-Thread. Die Anzeige selbst
gehört zu 9009.

**Der Zähldurchlauf muss `FILES | DIRECTORIES` anfordern.** Über SAF reicht
`ListContentUriDirectory` den `file_type_` an die Auflistung durch — mit `FILES`
allein kommen keine Unterverzeichnisse zurück, die Rekursion bleibt aus, und
gezählt werden nur die Dateien der obersten Ebene. Der Fehler ist still: keine
Meldung, nur eine zu kleine Zahl.

---

## Sackgassen

**Staging im Zielverzeichnis.** Erster Versuch war ein Nebenverzeichnis
`<hash>.staging` direkt neben dem Ziel, danach `base::Move`. Es lag damit im
selben gefährdeten Bereich; das Umbenennen meldete Erfolg und hinterließ
trotzdem eine unvollständige Kopie.

**Eindeutiges Zielverzeichnis allein.** Der Zeitstempel im Namen verhindert
Kollisionen mit einer nachlaufenden Löschung des Vorgängers — den Fehler behob er
nicht. Er bleibt drin, weil er nichts kostet und den Aufräumlauf erst möglich
macht.

**Zweiter Durchgang über die Wurzeldateien.** Eine Notlösung, die das Symptom
milderte, aber nicht die Ursache traf. Nach dem CRX-Umbau entfernt.

---

## Offen

**Sporadischer Fehlschlag beim ersten Laden.** Eine Wiederholung behebt es.

---

## Lehre

Der Fehler steckte nicht in der Kopierschleife, sondern in der Wahl des Ortes.
Vier Hypothesen und ebenso viele Umbauten gingen daneben, weil jeweils eine
Vermutung gebaut statt gemessen wurde. Erst eine Zwischenmeldung, die bei jeder
25. Datei prüfte, ob `manifest.json` noch existiert, zeigte das tatsächliche
Verhalten — und damit, dass die Suche nach dem Löscher aussichtslos war und die
Lösung darin lag, ihm auszuweichen.
