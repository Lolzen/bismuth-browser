# build-notes.md

Umgebungs- und Buildwissen, das in keiner Chromium-Anleitung steht.

---

## Umgebung

| | |
|---|---|
| Host | Void Linux, glibc |
| Checkout | `/home/gee/kiwi-rebase/build/chromium/src` |
| Speicher | `/dev/nvme0n1p2`, 3,6 TB, f2fs, per Bind-Mount eingehängt |
| Ziel | Chromium 150.0.7871.249, `target_cpu = "arm64"` |
| Erster Vollbau | rund 5 Stunden |

Der Bind-Mount hält den Pfad `/home/gee/kiwi-rebase/build` stabil, obwohl die
Daten auf der großen Platte liegen. Sauberer als ein Symlink, weil Chromiums
Werkzeuge Pfade teilweise auflösen.

Case-Sensitivity wurde geprüft und ist gegeben. f2fs kann optional
case-insensitive arbeiten — das würde einen Chromium-Checkout stillschweigend
zerstören.

---

## Void-spezifisch

**`install-build-deps.sh` ist unbrauchbar** — kann nur `apt`. Für einen
Android-Build kein Verlust: Clang, JDK, SDK, NDK, Node und siso kommen über DEPS
und die Hooks. Vorhanden sein müssen `git`, `python3`, `pkg-config`, `gperf`,
`ninja`, `cmake`, `unzip`, `zip`, `xz`, `rsync`, `bzip2`, `lsb_release`,
`ccache`.

**protobuf muss auf 3.20.3 festgenagelt werden.**

```
python3 -m pip install --user 'protobuf==3.20.3'
```

Ohne protobuf scheitert `gen_on_device_proto_descriptors.py`. Mit 4.x oder neuer
scheitert stattdessen `compile_resources.py` an `Descriptors cannot be created
directly` — Chromiums vorgenerierte `_pb2.py` stammen von einem `protoc` vor
3.19.

**`conda deactivate` vor dem Build.** Conda setzt `PYTHONPATH` und
`LD_LIBRARY_PATH` und stört Chromiums Buildscripts.

---

## Checkout

Den Tag direkt in die `.gclient`-URL schreiben:

```python
"url": "https://chromium.googlesource.com/chromium/src.git@150.0.7871.249",
"managed": True,
"custom_vars": {"checkout_pgo_profiles": True},
```

Wird `src` erst auf `main` geklont und danach auf einen Tag geschoben, versucht
`gclient` die Abhängigkeiten zu rebasen statt hart auszuchecken. Bei Dawn führt
das zu einem Konflikt über hunderte Dateien.

**HTTP 429 ist normal.** Mit `--jobs 4` läuft der Sync durch; er nimmt jederzeit
dort wieder auf, wo er abgebrochen ist. `_bad_scm`-Warnungen sind harmlos.

**`gclient runhooks` nicht überspringen.** Wer mit `--nohooks` synchronisiert,
muss es nachholen — sonst fehlen unter anderem die PGO-Profile, und ein
offizieller Build bricht mitten im V8-Schritt ab. Der Aufruf muss im Verzeichnis
mit der `.gclient` erfolgen, nicht in `src`.

---

## Versionssprung

**Vom Zweig lösen, bevor der Tag gewechselt wird.** Sonst versucht `gclient`, den
lokalen Zweig auf den neuen Tag zu rebasen, und bricht ab:

```
_____ src : Attempting rebase onto 150.0.7871.249...
Error: Conflict while rebasing this branch.
```

Abhilfe: `git rebase --abort`, dann `git checkout --detach`, dann erneut
synchronisieren.

**Die V8-Builtins-Profile kommen nicht automatisch mit.** Nach einer Stunde
Bauzeit:

```
Rejected profile data for RecordWriteSaveFP due to function change.
```

Sofort behebbar mit

```
python3 v8/tools/builtins-pgo/download_profiles.py download --depot-tools <pfad>
```

Dauerhaft durch `"checkout_pgo_profiles": True` in den `custom_vars` der
`.gclient`. Der Bau nimmt danach dort wieder auf, wo er abgebrochen ist.

**`git apply --3way --check` ist unzuverlässig.** Es meldete alle neun Patches
als sauber; beim tatsächlichen Anwenden scheiterten drei. Wer wissen will, was
passt, muss anwenden.

**Flags verfallen.** Chromium versieht Flags mit einem Verfallsdatum und setzt
sie danach zwangsweise zurück, unabhängig vom Quelltext. Ein Patch, der an Flags
ansetzt, wendet sauber an, baut durch und tut nichts. Erkennbar daran, dass
`#temporary-unexpire-flags-mNNN` das alte Verhalten wiederherstellt. Das ist eine
Diagnose, keine Lösung — Eingriffe gehören an die Entscheidungsstelle im Code,
nicht an Flags.

---

## Wichtige GN-Args

```gn
is_desktop_android = true      # aktiviert das Extensions-System
enable_service_discovery = false
dcheck_always_on = false
enable_java_asserts = false
treat_warnings_as_errors = false
disable_android_lint = true
cc_wrapper = "ccache"
use_remoteexec = false
proprietary_codecs = true
ffmpeg_branding = "Chrome"
```

**`dcheck_always_on = false` ist der wichtigste Eintrag.** Ohne ihn laufen
Debug-Assertions mit, die im offiziellen Chrome wegkompiliert sind. Auf
derstandard.at führte das reproduzierbar zu „Aw Snap":

```
[FATAL:cc/trees/property_tree.cc:2587] Attempting to animate non existent transform node
```

Chromium koppelt `dcheck_always_on` an `is_official_build`.

**`enable_java_asserts = false`** aus demselben Grund. Drei Abstürze beim
Tab-Switcher waren `AssertionError` aus `assumeNonNull` — Fehler, die es in einem
offiziellen Build nie gegeben hätte.

**`use_remoteexec = false`** ist Pflicht, Remote-Execution steht nur
Google-Mitarbeitern offen.

Vor dem ersten Build den Cache großzügig setzen: `ccache -M 100G`.

---

## Offizieller Build

`is_official_build = true` schaltet PGO und LTO ein. Drei Stolpersteine:

**Der Chrome-PGO-Zielname lautet `android-desktop-arm64`**, nicht
`android-arm64` — eine Folge von `is_desktop_android`.

**Die V8-Profile** siehe oben. Notfalls geht es auch ohne PGO:
`chrome_pgo_phase = 0`.

**Das APK ist nicht mehr debuggable.** `adb shell run-as` scheitert mit
`package not debuggable`, und die Kommandozeilendatei wird ignoriert. Für
Entwicklungsbuilds deshalb zusätzlich `debuggable_apks = true`. Für eine
Veröffentlichung gehört die Zeile wieder heraus.

**`Log.i` wird wegoptimiert.** Eine eingebaute Messung schien mehrfach zu
belegen, dass eine Methode nie aufgerufen wird — tatsächlich war nur die Ausgabe
unsichtbar. Für Diagnosezwecke immer `Log.e` benutzen.

---

## API-Keys

```gn
google_api_key = "…"
google_default_client_id = "…"
google_default_client_secret = "…"
use_official_google_api_keys = false
```

Die `args.gn` gehört in die `.gitignore`; eingecheckt wird nur
`args.gn.template` mit Platzhaltern.

**Der Discover-Feed lässt sich damit nicht beleben.** Unter
`is_desktop_android` wird der Feed-Code gar nicht kompiliert. Extensions und Feed
schließen sich derzeit aus.

---

## WebUI

**Chromium lintet die Stylesheets mit stylelint.** Ein doppelter Selektor in
derselben Datei bricht den Build ab.

**Die TypeScript-Typen für `developerPrivate` stammen nicht aus dem WebIDL**,
sondern aus `tools/typescript/definitions/developer_private.d.ts`. Wer ein
Ereignis im Schema ergänzt, muss es dort ebenfalls eintragen.

Das Schema selbst liegt seit 149 als `.webidl` vor.

---

## SAF-Eigenheiten

**Der Datei-Aufzähler steigt nur mit `DIRECTORIES` ab.** Über SAF reicht
`ListContentUriDirectory` den angeforderten `file_type_` an die Auflistung durch.
Eine rekursive Aufzählung mit `FILES` allein bleibt auf der obersten Ebene
stehen — ohne Fehlermeldung. Richtig ist `FILES | DIRECTORIES` mit eigener
Prüfung auf `IsDirectory()`.

**`base::CopyDirectory` funktioniert nicht.** Es öffnet Quelldateien mit dem
rohen Syscall `open()`, was bei einem `/SAF/`-Pfad scheitert. `base::File` zum
Lesen und `base::WriteFile` zum Schreiben sind dagegen SAF-fähig.

---

## Debugging auf dem Gerät

`adb` braucht **kein Root**, nur USB-Debugging — und ein debuggable APK.

```
adb shell "echo 'chrome --enable-logging=stderr --v=1' > /data/local/tmp/chrome-command-line"
```

Ohne das leitet Chromium `console.log` aus Erweiterungen nicht an den Logcat
weiter. **Das Einschalten dieses Loggings war der Wendepunkt der gesamten
Extensions-Fehlersuche.**

Logcat immer erst in eine Datei schreiben, dann greppen:

```
adb logcat -c && adb logcat -v time > /tmp/x.log
```

Für Abstürze gibt es einen eigenen Puffer, der länger hält:

```
adb logcat -b crash -d > /tmp/crash.log
```

Der `Caused by`-Block steht am **Ende** des Java-Stacks.

---

## Werkzeug, das sich am meisten bewährt hat

```
gn refs out/Ext //pfad/zur/datei.cc
gn path out/Ext //chrome/android:chrome_public_apk //pfad:target
```

Das erste beantwortet in Sekunden, ob eine Datei überhaupt im Build-Graphen
liegt. Das zweite, ob ein Target vom APK aus erreichbar ist. Zusammen haben sie
mehrfach eine falsche Fährte beendet.

Für alte Dateien, die Google entfernt hat:

```
git ls-tree -r --name-only HEAD | grep -i <name>
git show HEAD:<pfad> > <ziel>
```

Die Referenz-Repositories unter `upstream/` sind echte Git-Repositories ohne
ausgechecktes Arbeitsverzeichnis. So kam der `SystemAccountManagerDelegate` aus
132 zurück.

---

## Vorgehen, das sich bewährt hat

Bei einem Fehler, der sich nicht sofort erklärt, **erst instrumentieren, dann
urteilen**. Drei Log-Zeilen an der richtigen Stelle haben in diesem Projekt
mehrfach eine Frage beantwortet, an der vier Hypothesen gescheitert waren.

Umgekehrt gilt: Wer eine Vermutung baut statt sie zu messen, baut oft an der
falschen Stelle. Der Kopierfehler in 9003 hat vier Hypothesen und ebenso viele
Umbauten gekostet, bis eine Zwischenmeldung zeigte, was tatsächlich passierte.
