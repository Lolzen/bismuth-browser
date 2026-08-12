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

Der Bind-Mount hält den Pfad `/home/gee/kiwi-rebase/build` stabil, obwohl die Daten auf der großen Platte liegen. Sauberer als ein Symlink, weil Chromiums Werkzeuge Pfade teilweise auflösen.

Case-Sensitivity wurde geprüft und ist gegeben. f2fs kann optional case-insensitive arbeiten — das würde einen Chromium-Checkout stillschweigend zerstören.

---

## Void-spezifisch

**`install-build-deps.sh` ist unbrauchbar** — kann nur `apt`. Für einen Android-Build kein Verlust: Clang, JDK, SDK, NDK, Node und siso kommen über DEPS und die Hooks. Vorhanden sein müssen `git`, `python3`, `pkg-config`, `gperf`, `ninja`, `cmake`, `unzip`, `zip`, `xz`, `rsync`, `bzip2`, `lsb_release`, `ccache`.

**protobuf muss auf 3.20.3 festgenagelt werden.**

```
python3 -m pip install --user 'protobuf==3.20.3'
```

Ohne protobuf scheitert `gen_on_device_proto_descriptors.py`. Mit 4.x oder neuer scheitert stattdessen `compile_resources.py` an `Descriptors cannot be created directly` — Chromiums vorgenerierte `_pb2.py` stammen von einem `protoc` vor 3.19.

**`conda deactivate` vor dem Build.** Conda setzt `PYTHONPATH` und `LD_LIBRARY_PATH` und stört Chromiums Buildscripts.

---

## Checkout

Den Tag direkt in die `.gclient`-URL schreiben:

```python
"url": "https://chromium.googlesource.com/chromium/src.git@149.0.7827.238",
"managed": True,
```

Wird `src` erst auf `main` geklont und danach auf einen Tag geschoben, versucht `gclient` die Abhängigkeiten zu rebasen statt hart auszuchecken. Bei Dawn führt das zu einem Konflikt über hunderte Dateien.

**HTTP 429 ist normal.** Mit `--jobs 4` läuft der Sync durch; er nimmt jederzeit dort wieder auf, wo er abgebrochen ist. `_bad_scm`-Warnungen sind harmlos.

**`gclient runhooks` nicht überspringen.** Wer mit `--nohooks` synchronisiert, muss es nachholen — sonst fehlen unter anderem die PGO-Profile, und ein offizieller Build bricht mitten im V8-Schritt ab. Der Aufruf muss im Verzeichnis mit der `.gclient` erfolgen, nicht in `src`.

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

**`dcheck_always_on = false` ist der wichtigste Eintrag.** Ohne ihn laufen Debug-Assertions mit, die im offiziellen Chrome wegkompiliert sind. Auf derstandard.at führte das reproduzierbar zu „Aw Snap":

```
[FATAL:cc/trees/property_tree.cc:2587] Attempting to animate non existent transform node
[FATAL:components/input/render_input_router.cc:712] kGestureScrollBegin should not be sent again…
```

Chromium koppelt `dcheck_always_on` an `is_official_build`.

**`enable_java_asserts = false`** aus demselben Grund. Drei Abstürze beim Tab-Switcher waren `AssertionError` aus `assumeNonNull` — Fehler, die es in einem offiziellen Build nie gegeben hätte. Echte Fehler wie `ClassCastException` bleiben davon unberührt.

**`use_remoteexec = false`** ist Pflicht, Remote-Execution steht nur Google-Mitarbeitern offen.

Vor dem ersten Build den Cache großzügig setzen:

```
ccache -M 100G
```

---

## Offizieller Build

`is_official_build = true` schaltet PGO und LTO ein. Zwei Stolpersteine:

**Die V8-Builtins-Profile fehlen**, wenn die Hooks nicht liefen:

```
"../../v8/tools/builtins-pgo/profiles/x64.profile", needed by "gen/v8/embedded.S", missing
```

**Der Chrome-PGO-Zielname lautet `android-desktop-arm64`**, nicht `android-arm64` — eine Folge von `is_desktop_android`. Die Datei `chrome/build/android-arm64.pgo.txt` existiert gar nicht.

Beides erledigt `gclient runhooks`. Notfalls geht es auch ohne PGO:

```gn
chrome_pgo_phase = 0
```

Damit bleiben LTO und die übrigen Vorteile erhalten, der Build wird deutlich kürzer.

---

## API-Keys

```gn
google_api_key = "…"
google_default_client_id = "…"
google_default_client_secret = "…"
use_official_google_api_keys = false
```

Ohne sie fehlen Sync, Safe Browsing und Standortdienste. Die `args.gn` gehört in die `.gitignore`; eingecheckt wird nur `args.gn.template` mit Platzhaltern.

**Der Discover-Feed lässt sich damit nicht beleben.** `gn refs out/Ext //components/feed/core/v2:core` liefert nichts — unter `is_desktop_android` wird der Feed-Code gar nicht kompiliert, weil auf die Desktop-Produktvariante geschaltet wird. Extensions und Feed schließen sich derzeit aus.

---

## DRM / Widevine

Am Vanilla-Build geprüft: Widevine ist vorhanden, die Wiedergabe funktioniert. Ein Sicherheitslevel wird nicht angezeigt, vermutlich L3.

Auf Android kommt Widevine über die `MediaDrm`-API des Geräts, nicht über ein mitgeliefertes CDM. Nötig sind nur `proprietary_codecs = true` und `ffmpeg_branding = "Chrome"`.

---

## Debugging auf dem Gerät

`adb` braucht **kein Root**, nur USB-Debugging.

```
adb shell "echo 'chrome --enable-logging=stderr --v=1' > /data/local/tmp/chrome-command-line"
```

Ohne das leitet Chromium `console.log` aus Erweiterungen nicht an den Logcat weiter. **Das Einschalten dieses Loggings war der Wendepunkt der gesamten Extensions-Fehlersuche** — davor elf im Quelltext geprüfte und verworfene Hypothesen, danach nannte der Logcat die Ursache beim Namen.

Logcat immer erst in eine Datei schreiben, dann greppen:

```
adb logcat -c && adb logcat -v time > /tmp/x.log
```

Nachträgliches `adb logcat -d` verliert den Absturz, wenn der Puffer schon übergelaufen ist. Der `Caused by`-Block steht am **Ende** des Java-Stacks:

```
grep -n "E AndroidRuntime" /tmp/x.log | grep "Caused by"
```

SharedPreferences lassen sich bei einem debuggable-Build ohne Root lesen:

```
adb shell run-as org.chromium.chrome cat shared_prefs/org.chromium.chrome_preferences.xml
```

---

## Werkzeug, das sich am meisten bewährt hat

```
gn refs out/Ext //pfad/zur/datei.cc
```

Beantwortet in Sekunden, ob eine Datei überhaupt im Build-Graphen liegt. Hat dreimal eine falsche Fährte beendet: bei `extension_features.cc`, bei `chrome_process_manager_delegate.cc` und beim Discover-Feed.
