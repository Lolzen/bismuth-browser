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

**`install-build-deps.sh` ist unbrauchbar.** Das Script kann nur `apt`. Für einen Android-Build ist das aber kein Verlust: Clang, JDK, Android-SDK, NDK, Node und siso kommen alle über DEPS und die Hooks. Der GTK-, X11- und 32-Bit-Block betrifft nur Linux-Desktop-Builds.

Vorhanden sein müssen lediglich: `git`, `python3`, `pkg-config`, `gperf`, `ninja`, `cmake`, `unzip`, `zip`, `xz`, `rsync`, `bzip2`, `lsb_release`, `ccache`.

**protobuf muss auf 3.20.3 festgenagelt werden.**

```
python3 -m pip install --user 'protobuf==3.20.3'
```

Ohne protobuf scheitert `gen_on_device_proto_descriptors.py` mit `ModuleNotFoundError`. Mit einer neueren Version scheitert stattdessen `compile_resources.py` an `Descriptors cannot be created directly` — Chromiums vorgenerierte `_pb2.py` unter `build/android/gyp/proto/` stammen von einem `protoc` vor 3.19 und vertragen sich nicht mit protobuf 4.x oder 5.x. 3.20.3 erfüllt beide Anforderungen.

Unter Ubuntu fällt das nicht auf, weil `install-build-deps.sh` dort automatisch die passende Distro-Version zieht.

**`conda deactivate` vor dem Build.** Conda setzt `PYTHONPATH` und `LD_LIBRARY_PATH` eigenständig und kann Chromiums Buildscripts an unerwarteten Stellen stören.

---

## Checkout

Den Tag direkt in die `.gclient`-URL schreiben, nicht nachträglich auschecken:

```python
"url": "https://chromium.googlesource.com/chromium/src.git@149.0.7827.238",
"managed": True,
```

Wird `src` erst auf `main` geklont und danach auf einen Tag geschoben, versucht `gclient` die Abhängigkeiten zu rebasen statt hart auszuchecken. Bei Dawn führt das zu einem Konflikt über hunderte Dateien.

**HTTP 429 ist normal.** Googles Server begrenzt anonyme Zugriffe. Mit `--jobs 4` statt der Voreinstellung läuft der Sync durch; er nimmt jederzeit dort wieder auf, wo er abgebrochen ist.

`_bad_scm`-Warnungen sind harmlos: `gclient` räumt halbfertige Checkouts beiseite und legt sie neu an. Erst nach erfolgreichem Sync aufräumen.

---

## Wichtige GN-Args

```gn
dcheck_always_on = false
```

**Der wichtigste Eintrag.** Ohne ihn laufen Debug-Assertions mit, die im offiziellen Chrome wegkompiliert sind. Auf derstandard.at führte das reproduzierbar zu „Aw Snap":

```
[FATAL:cc/trees/property_tree.cc:2587]
  Attempting to animate non existent transform node
[FATAL:components/input/render_input_router.cc:712]
  kGestureScrollBegin should not be sent again when kTouchscreen is in gesture scroll
```

Beides harmlose Grenzfälle beim Scrollen und Animieren, die im Release stillschweigend durchlaufen. Chromium koppelt `dcheck_always_on` an `is_official_build`, und der steht auf `false`.

Kiwi hatte `is_official_build = true` — deshalb stürzte Kiwi an dieser Stelle nicht ab. Der Vergleich war nie „105 gegen 149", sondern „official gegen non-official".

Weitere Args, die sich bewährt haben:

```gn
treat_warnings_as_errors = false
disable_android_lint = true
cc_wrapper = "ccache"
use_remoteexec = false
```

`use_remoteexec = false` ist Pflicht — Remote-Execution steht nur Google-Mitarbeitern offen.

Vor dem ersten Build den Cache großzügig setzen, sonst verdrängt ein Chromium-Lauf alles Vorherige:

```
ccache -M 100G
```

---

## Merkposten für den nächsten neuen Build

- [ ] `dcheck_always_on = false`
- [ ] Eigene Google-API-Keys eintragen: `google_api_key`, `google_default_client_id`, `google_default_client_secret`, dazu `use_official_google_api_keys = false`
- [ ] `args.gn` in die `.gitignore`, `args.gn.template` mit Platzhaltern einchecken

---

## DRM / Widevine

Am Vanilla-Build geprüft: **Widevine ist vorhanden und die Wiedergabe funktioniert.** Ein Sicherheitslevel wird nicht angezeigt, was normal ist — die meisten Testseiten fragen nur ab, ob das Key-System verfügbar ist.

Vermutlich L3, also SD. Für L1 und damit HD-Streaming bräuchte es eine Signatur, die die Dienste akzeptieren; bei einem selbstsignierten Fork ist das unwahrscheinlich.

Wichtig: Auf Android kommt Widevine über die `MediaDrm`-API des Geräts, nicht über ein mitgeliefertes CDM. Die Gitlinks unter `third_party/widevine/cdm/` sind für Android ohnehin leer. Nötig sind lediglich:

```gn
proprietary_codecs = true
ffmpeg_branding = "Chrome"
```

---

## Debugging auf dem Gerät

`adb` braucht **kein Root**, nur die Entwickleroptionen und USB-Debugging.

```
export PATH="…/third_party/android_sdk/public/platform-tools:$PATH"
adb logcat -v time > /tmp/crash.log
```

Nach einem Absturz filtern nach `SIGSEGV`, `Fatal signal`, `FATAL:`, `lmkd`, `Out of memory`. Ein `FATAL:` mit CHECK-Text nennt Datei und Zeile direkt.

`Crash upload URL is not configured` in den Logs ist erwartbar und harmlos — Crashpad hat ohne API-Keys kein Ziel zum Hochladen.
