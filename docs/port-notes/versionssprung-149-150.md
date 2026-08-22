# Versionssprung 149 → 150

**Status:** abgeschlossen
**Von:** 149.0.7827.238
**Auf:** 150.0.7871.249

---

## Ergebnis vorweg

Der Sprung war deutlich einfacher als befürchtet. Sechs der neun Patches greifen
unverändert, drei brauchten kleine Anpassungen, und die eigentliche Arbeit lag in
**einer Zeile** für Manifest V2.

Was funktioniert: Erweiterungen, MV2, Laden mit Fortschritt, Tab-Switcher,
Branding, Web Store, Startzeit, keine Deprecation-Hinweise.

---

## Ablauf

**Zweig für 149 anlegen**, bevor irgendetwas angefasst wird. Der Chromium-Baum
wird beim Sprung zurückgesetzt; alles, was nicht in den Patches steht, ist danach
weg.

**Tag wechseln.** Der Checkout ist nicht flach (`git rev-parse
--is-shallow-repository` → `false`), ein Wechsel ist also unproblematisch.

**Vorher vom Zweig lösen.** `gclient` versucht sonst, den lokalen Zweig auf den
neuen Tag zu **rebasen**, und bricht mit einem Konflikt ab:

```
_____ src : Attempting rebase onto 150.0.7871.249...
Error: Conflict while rebasing this branch.
```

Abhilfe: `git rebase --abort`, dann `git checkout --detach`. Mit losgelöstem HEAD
checkt `gclient` hart aus.

**Dann:** `CHROMIUM_TARGET` und die `.gclient`-URL auf den neuen Tag, `gclient
sync --jobs 4`.

---

## Stolpersteine

### V8-Profile kommen nicht automatisch mit

Nach gut einer Stunde Bauzeit:

```
Fatal error
Rejected profile data for RecordWriteSaveFP due to function change.
```

Die PGO-Profile für V8 stammen noch von der alten Version. Abhilfe sofort:

```
python3 v8/tools/builtins-pgo/download_profiles.py download --depot-tools <pfad>
```

Dauerhaft gehört in die `.gclient`:

```python
"custom_vars": {"checkout_pgo_profiles": True},
```

Der Bau nimmt danach dort wieder auf, wo er abgebrochen ist.

### Trockenprüfung von Patches ist unzuverlässig

`git apply --3way --check` meldete **alle neun** Patches als sauber. Beim
tatsächlichen Anwenden scheiterten drei. Wer wissen will, was wirklich passt,
muss anwenden — notfalls in einem Zustand, den man danach verwirft.

### Flag-Verfall macht Patches still wirkungslos

Chromium versieht Flags mit einem Verfallsdatum. Nach dem Sprung sind die Flags
der Vorgängerversion abgelaufen und werden zwangsweise zurückgesetzt, egal was im
Quelltext steht. Ein Patch, der an Flags ansetzt, wendet sauber an, baut durch
und **tut nichts**.

Erkennbar daran, dass `#temporary-unexpire-flags-m149` das Verhalten
wiederherstellt. Das ist eine Diagnose, keine Lösung — die Lösung ist, nicht an
Flags anzusetzen.

---

## Die drei Konflikte

**`chrome/app/chromium_strings.grd` und `settings_chromium_strings.grdp`** aus
9005. Nicht zusammenführen — die Dateien werden von einem Script erzeugt. Auf den
neuen Stand zurücksetzen und die Scripts aus `scripts/9005-branding/` erneut
laufen lassen.

**`extension_info_generator.cc`** aus 9007. Das Feld
`did_acknowledge_mv2_deprecation_notice` existiert nicht mehr; von unserer
Änderung bleibt nur die Zuweisung `is_affected_by_mv2_deprecation = false`.

**`extension_features.cc`** aus 9001. `kExtensionManifestV2Disabled` ist
entfernt; die Zeile entfällt ersatzlos.

---

## Was danach noch zu tun war

Der Einzeiler für MV2 in `manifest_v2_experiment_manager.cc` — Details in der
Notiz zu 9001. Dazu die neue Datei in die Patchgruppe von 9001 aufnehmen, sonst
fehlt sie beim nächsten Sprung.

**Kontrolle:** `grep -c "^diff --git"` auf die erzeugten Patches. Die Zahl muss
der erwarteten Dateizahl entsprechen. Bei 9001 waren es zunächst drei statt vier
— die neue Datei war nicht in der Gruppe.

---

## Prüfliste nach dem Bau

| Bereich | Was |
|---|---|
| MV2 | uBlock lädt, ist aktiv, blockt, übersteht Neustarts |
| Extensions | Puzzle-Menü ohne Absturz, Untermenü vollständig |
| Laden | Fortschritt mit Prozenten, nur ein Verzeichnis je Quelle |
| Tab-Switcher | Kartenansicht und Umschalter unter Tabs |
| Web Store | Desktop-Fassung, Installation läuft |
| Branding | Name, Icon, keine Chromium-Texte, kein BismuthOS |
| Deprecation | keine Warnbanner, keine Hinweise in den Details |
| Konto | Anmeldung ohne Absturz, Konto erscheint |
| Startzeit | mit uBlock etwa drei Sekunden |
| Alltag | ein Tag Surfen ohne Absturz |

---

## Zeitaufwand

Ein Vollbau nach dem Sprung dauert mehrere Stunden, weil `ccache` kaum etwas
wiederverwenden kann. Zwei Bauabbrüche kamen dazu — die V8-Profile und der
MV2-Einzeiler. Realistisch ist ein Tag, wenn nichts Größeres bricht.
