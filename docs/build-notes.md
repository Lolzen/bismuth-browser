# build-notes.md

Umgebungs- und Buildwissen, das in keiner Chromium-Anleitung steht.

---

## Umgebung

| | |
|---|---|
| Host | Void Linux, glibc |
| Checkout | `/home/gee/kiwi-rebase/build/chromium/src` |
| Speicher | `/dev/nvme0n1p2`, 3,6 TB, f2fs, per Bind-Mount eingehängt |
| Ziel | Chromium 149.0.7827.238, `target_cpu = "arm64"` |
| Erster Vollbuild | rund 5 Stunden |

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
"url": "https://chromium.googlesource.com/chromium/src.git@149.0.7827.238",
"managed": True,
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
[FATAL:components/input/render_input_router.cc:712] kGestureScrollBegin should not be sent again…
```

Chromium koppelt `dcheck_always_on` an `is_official_build`.

**`enable_java_asserts = false`** aus demselben Grund. Drei Abstürze beim
Tab-Switcher waren `AssertionError` aus `assumeNonNull` — Fehler, die es in einem
offiziellen Build nie gegeben hätte. Echte Fehler wie `ClassCastException`
bleiben davon unberührt.

**`use_remoteexec = false`** ist Pflicht, Remote-Execution steht nur
Google-Mitarbeitern offen.

Vor dem ersten Build den Cache großzügig setzen:

```
ccache -M 100G
```

---

## Offizieller Build

`is_official_build = true` schaltet PGO und LTO ein. Drei Stolpersteine:

**Die V8-Builtins-Profile fehlen**, wenn die Hooks nicht liefen:

```
"../../v8/tools/builtins-pgo/profiles/x64.profile", needed by "gen/v8/embedded.S", missing
```

**Der Chrome-PGO-Zielname lautet `android-desktop-arm64`**, nicht
`android-arm64` — eine Folge von `is_desktop_android`. Die Datei
`chrome/build/android-arm64.pgo.txt` existiert gar nicht.

Beides erledigt `gclient runhooks`. Notfalls geht es auch ohne PGO:

```gn
chrome_pgo_phase = 0
```

**Das APK ist danach nicht mehr debuggable.** `adb shell run-as` scheitert mit
`package not debuggable`, und die Kommandozeilendatei unter
`/data/local/tmp/chrome-command-line` wird ignoriert. Für Entwicklungsbuilds
deshalb zusätzlich:

```gn
debuggable_apks = true
```

Für eine Veröffentlichung gehört die Zeile wieder heraus — ein debuggable APK
erlaubt jedem mit ADB-Zugang Einblick in die App-Daten.

**Geschwindigkeit:** Der Unterschied ist auf dem Gerät kaum spürbar.
Speedometer 3.1 liegt bei rund 14,7 auf einem ROG Phone 7, also im normalen
Bereich. Der eigentliche Gewinn ist, dass der Build dem entspricht, was Chrome
selbst ausliefert.

---

## API-Keys

```gn
google_api_key = "…"
google_default_client_id = "…"
google_default_client_secret = "…"
use_official_google_api_keys = false
```

Ohne sie fehlen Sync, Safe Browsing und Standortdienste. Die `args.gn` gehört in
die `.gitignore`; eingecheckt wird nur `args.gn.template` mit Platzhaltern.

**Der Discover-Feed lässt sich damit nicht beleben.**
`gn refs out/Ext //components/feed/core/v2:core` liefert nichts — unter
`is_desktop_android` wird der Feed-Code gar nicht kompiliert, weil auf die
Desktop-Produktvariante geschaltet wird. Extensions und Feed schließen sich
derzeit aus.

---

## WebUI

**Chromium lintet die Stylesheets mit stylelint.** Ein doppelter Selektor in
derselben Datei bricht den Build ab:

```
manager.css
  107:1  ✖  Unexpected duplicate selector "#loadProgressLabel", first used at line 77
```

Beim Anhängen von Regeln also auf Dubletten achten — besonders, wenn ein Script
mehrfach läuft.

**Die TypeScript-Typen für `developerPrivate` stammen nicht aus dem WebIDL**,
sondern aus der handgepflegten Datei
`tools/typescript/definitions/developer_private.d.ts`. Wer ein Ereignis im
Schema ergänzt, muss es dort ebenfalls eintragen, sonst bricht der
TypeScript-Schritt.

Das Schema selbst liegt seit 149 als `.webidl` vor, nicht mehr als `.idl` oder
`.json`.

---

## SAF-Eigenheiten

Zwei Verhaltensweisen, die auf einem gewöhnlichen Dateisystem nicht auftreten
und beim Versionssprung stillen Bruch verursachen können.

**Der Datei-Aufzähler steigt nur mit `DIRECTORIES` ab.** Über SAF reicht
`ListContentUriDirectory` den angeforderten `file_type_` an die Auflistung durch.
Eine rekursive Aufzählung mit `FILES` allein bekommt keine Unterverzeichnisse zu
sehen und bleibt deshalb auf der obersten Ebene stehen — ohne Fehlermeldung.
Richtig ist `FILES | DIRECTORIES` mit eigener Prüfung auf `IsDirectory()`.

**`base::CopyDirectory` funktioniert nicht.** Es öffnet Quelldateien mit dem
rohen Syscall `open()`, was bei einem `/SAF/`-Pfad scheitert. `base::File` zum
Lesen und `base::WriteFile` zum Schreiben sind dagegen SAF-fähig.

---

## DRM / Widevine

Am Vanilla-Build geprüft: Widevine ist vorhanden, die Wiedergabe funktioniert.
Ein Sicherheitslevel wird nicht angezeigt, vermutlich L3.

Auf Android kommt Widevine über die `MediaDrm`-API des Geräts, nicht über ein
mitgeliefertes CDM. Nötig sind nur `proprietary_codecs = true` und
`ffmpeg_branding = "Chrome"`.

---

## Debugging auf dem Gerät

`adb` braucht **kein Root**, nur USB-Debugging — und ein debuggable APK, siehe
oben.

```
adb shell "echo 'chrome --enable-logging=stderr --v=1' > /data/local/tmp/chrome-command-line"
```

Ohne das leitet Chromium `console.log` aus Erweiterungen nicht an den Logcat
weiter. **Das Einschalten dieses Loggings war der Wendepunkt der gesamten
Extensions-Fehlersuche** — davor elf im Quelltext geprüfte und verworfene
Hypothesen, danach nannte der Logcat die Ursache beim Namen.

Logcat immer erst in eine Datei schreiben, dann greppen:

```
adb logcat -c && adb logcat -v time > /tmp/x.log
```

Nachträgliches `adb logcat -d` verliert den Absturz, wenn der Puffer schon
übergelaufen ist. Für Abstürze gibt es einen eigenen Puffer, der länger hält:

```
adb logcat -b crash -d > /tmp/crash.log
```

Der `Caused by`-Block steht am **Ende** des Java-Stacks:

```
grep -n "E AndroidRuntime" /tmp/x.log | grep "Caused by"
```

SharedPreferences lassen sich bei einem debuggable Build ohne Root lesen:

```
adb shell run-as org.bismuth.browser cat shared_prefs/org.bismuth.browser_preferences.xml
```

---

## Werkzeug, das sich am meisten bewährt hat

```
gn refs out/Ext //pfad/zur/datei.cc
gn path out/Ext //chrome/android:chrome_public_apk //pfad:target
```

Das erste beantwortet in Sekunden, ob eine Datei überhaupt im Build-Graphen
liegt. Das zweite, ob ein Target vom APK aus erreichbar ist. Zusammen haben sie
viermal eine falsche Fährte beendet: bei `extension_features.cc`, bei
`chrome_process_manager_delegate.cc`, beim Discover-Feed und beim
Extensions-Toolbar.

---

## Vorgehen, das sich bewährt hat

Bei einem Fehler, der sich nicht sofort erklärt, **erst instrumentieren, dann
urteilen**. Drei Log-Zeilen an der richtigen Stelle haben in diesem Projekt
mehrfach eine Frage beantwortet, an der vier Hypothesen gescheitert waren — beim
Extensions-Laden, beim Einstellungsschalter und beim Kopierfehler.

Umgekehrt gilt: Wer eine Vermutung baut statt sie zu messen, baut oft an der
falschen Stelle. Der Kopierfehler in 9003 hat vier Hypothesen und ebenso viele
Umbauten gekostet, bis eine Zwischenmeldung im Kopierlauf zeigte, was tatsächlich
passierte.
