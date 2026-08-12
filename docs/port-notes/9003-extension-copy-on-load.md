# 9003 — Erweiterungen in den App-Speicher übernehmen

**Status:** funktioniert, ein sporadischer Fehler offen
**Patch:** `patches/9003-extension-copy-on-load.patch`
**Umfang:** 2 Dateien, rund 118 Zeilen

---

## Absicht

Eine über den Android-Ordnerpicker geladene Erweiterung soll **nicht dauerhaft hinter dem Storage Access Framework laufen**, sondern beim Laden einmalig in den App-Speicher übernommen werden.

---

## Warum das nötig ist

Zwei Gründe, und der zweite wog schwerer als erwartet.

**Geschwindigkeit.** Jeder Dateizugriff über SAF kostet einen Binder-IPC an den Document Provider. uBlock Origin besteht aus 655 Dateien, und Chromium prüft entpackte Erweiterungen bei jedem Start.

```
mit uBlock ueber SAF     33 Sekunden Startzeit
ohne uBlock               1 Sekunde
mit uBlock im App-Speicher  3 Sekunden
```

**Beständigkeit.** SAF-Pfade überleben einen Neustart nicht. Im Startlog steht dann:

```
Fehler beim Laden der Erweiterung aus: /SAF/com.android.externalstorage.documents/tree/…
Manifest-Datei fehlt oder ist nicht lesbar
```

Kiwi hatte dieses Problem nie — dort kamen Erweiterungen aus dem Store und lagen im Profilverzeichnis. Seit der Store MV2 nicht mehr ausliefert, ist der lokale Ladeweg der einzige, und damit wird die Übernahme in den App-Speicher zur Voraussetzung dafür, dass Erweiterungen überhaupt bestehen bleiben.

---

## Umsetzung

`chrome/browser/extensions/api/developer_private/developer_private_functions.cc`

`DeveloperPrivateLoadUnpackedFunction::StartFileLoad` wird in zwei Hälften geteilt:

```
StartFileLoad        loest die content-URI in einen /SAF/-Pfad auf,
                     stoesst das Kopieren im Thread-Pool an
OnCopyComplete       Rueckruf, ruft ContinueFileLoad mit dem Zielpfad
ContinueFileLoad     der urspruengliche Rumpf mit UnpackedInstaller
```

Das Kopieren **darf nicht im UI-Thread laufen** — 655 Dateien über SAF hätten sonst einen ANR ausgelöst. Deshalb `base::ThreadPool::PostTaskAndReplyWithResult`.

Zielverzeichnis:

```
<profil>/UnpackedExtensions/<PersistentHash des Quellpfads>
```

Der Hash macht das Ziel stabil: Derselbe Quellordner landet immer im selben Verzeichnis, ein erneutes Laden überschreibt statt Dubletten anzulegen. Und er umgeht das Bereinigen von SAF-Pfaden, die `%3A` und `%2F` enthalten.

### Staging

Erste Fassung löschte das Ziel und kopierte hinein. Scheiterte der Kopiervorgang, war die vorher funktionierende Kopie weg und ein leeres Verzeichnis blieb zurück — die Erweiterung verschwand aus der Liste.

Jetzt wird in ein Nebenverzeichnis kopiert und erst bei Erfolg umbenannt:

```cpp
const base::FilePath staging = to.AddExtensionASCII("staging");
…
base::DeletePathRecursively(to);
if (!base::Move(staging, to)) { … }
```

Ein Fehlschlag lässt den bestehenden Stand damit unangetastet.

### Warum keine Standardfunktion

`base::CopyDirectory` scheidet aus: Es öffnet Quelldateien mit dem rohen Syscall `open()`, was bei einem `/SAF/`-Pfad scheitert. Die eigene Schleife benutzt `base::File` zum Lesen und `base::WriteFile` zum Schreiben — beide sind SAF-fähig, wie `base/files/file_posix.cc` und `file_util_posix.cc` zeigen.

---

## Erster Anlauf, der scheiterte

Die frühere Fassung ließ die Erweiterung im Zustand „neu laden" hängen. Die Ursache wurde nie geklärt, weil ohne Fortschrittsausgabe nicht zu unterscheiden war, ob sie hängt oder nur langsam ist.

> **Lehre:** Bei einem Vorgang, der Minuten dauern kann, gehört die Instrumentierung in die erste Fassung, nicht in die zweite.

---

## Offen

- **Sporadischer Fehlschlag beim ersten Laden**, meist direkt nach dem Einspielen eines neuen APK. Im Log erscheint `OnCopyComplete success=0` ohne vorangehende Fehlermeldung. Die drei stillen Rückgabepfade sind inzwischen mit `[COPYDBG]` instrumentiert; die Ausgaben bleiben drin, bis der Fehler wieder auftritt. Eine Wiederholung des Ladevorgangs behebt es.
- **Fortschrittsanzeige** fehlt. Der Kopiervorgang dauert rund eine Minute ohne sichtbare Rückmeldung. Vorschlag: ein Hinweis beim Start und einer beim Abschluss statt eines gepflegten UI-Zustands.
