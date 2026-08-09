# 9001 — Extensions auf Android aktivieren (inkl. MV2)

**Status:** WiP — Konfiguration steht, Build läuft, Funktionsnachweis offen
**Patch:** `patches/9001-mv2-enabled.patch`
**Branch:** `feat/mv2-enabled`
**Basis:** Chromium 149.0.7827.238

---

## Absicht

Erweiterungen sollen auf Android laufen, und zwar mit **Manifest V2**. MV2 ist harte Anforderung, nicht verhandelbar.

## Was sich gegenüber der ursprünglichen Planung verschoben hat

Der Meilenstein hieß anfangs „MV2 reaktivieren". Das war die falsche Fragestellung.

MV2 war nie die Hürde. Der erste Versuch — die MV2-Flags in `extensions/common/extension_features.cc` umzulegen und neu zu bauen — endete mit `Everything is up-to-date`. Die Datei ist im Android-Build gar nicht Teil des Abhängigkeitsgraphen. `gn refs` fand keinerlei Referenz.

Der Grund: In `out/Vanilla` standen alle drei Extension-Schalter auf `false`. Das Extensions-Subsystem wird auf Android schlicht nicht kompiliert.

> **Kiwis eigentliche Leistung war nicht, MV2 zu erhalten, sondern Extensions auf Android überhaupt zu aktivieren.**

## Kiwis Umsetzung (Chromium 105, 2022)

- `args.gn`: `enable_extensions = true` — das volle Desktop-Extensions-System auf Android erzwungen
- `ui/webui/resources/cr_elements/BUILD.gn`: zwölfmal `if (include_polymer)` zu `if (include_polymer || true)`
- dazu Eingriffe in `ui/webui/BUILD.gn` und `ui/webui/resources/BUILD.gn`
- eine Dep-Umbenennung: `keyboard_shortcut_list.m` → `keyboard_shortcut_list`

Das funktioniert, drückt aber keine Bedingung aus, sondern schaltet sie ab. Bei jedem Versionssprung kollidiert es neu — was mit ein Grund sein dürfte, warum Kiwi nach 2022 nie wieder rebast hat.

## Umsetzung in 149

Chromium 149 kennt einen offiziellen Pfad, den es 2022 nicht gab. In `extensions/buildflags/buildflags.gni`:

```gn
enable_desktop_android_extensions = is_desktop_android
enable_extensions_core = enable_extensions || enable_desktop_android_extensions
```

Google warnt im Kommentar selbst: *very much in-development, non-stable, and likely to crash at any given moment.* Trotzdem ist es der richtige Weg — was dort nicht kompiliert, wird von Google repariert, während Kiwis Ansatz mit jedem Milestone weiter auseinanderlief.

Belegt wird das durch `chrome/browser/ui/android/extensions/`: ein vollständiger nativer UI-Satz mit Toolbar-Integration, Menü, Action-Popups, Kontextmenü, Installationsdialog, Entwicklermodus-Bridge, Tastenkürzel-Registry und eigenen `res/`-Ressourcen. Also genau die Oberfläche, die Kiwi 2022 selbst bauen musste.

### Der Weg dorthin

Erster Versuch war `enable_desktop_android_extensions = true`. Das führte zu vier GN-Assertions:

| # | Stelle | Auslöser |
|---|---|---|
| 1 | `media/router/discovery/BUILD.gn:7` | `media/router/BUILD.gn:418` (Test-Support) |
| 2 | `cr_components/cr_shortcut_input/BUILD.gn:8` | `chrome/browser/resources/extensions/BUILD.gn:151` |
| 3 | `cr_components/managed_footnote/BUILD.gn:8` | dieselbe Kette |
| 4 | `media/router/discovery/BUILD.gn:7` | `extensions/api/mdns/BUILD.gn:19` |

Ursache in allen Fällen dieselbe: Der Baum behandelt `enable_desktop_android_extensions` und `is_desktop_android` als gleichbedeutend. Solange beide zusammenfallen, merkt es niemand — beim Auseinanderziehen fallen sie auf.

Danach scheiterte der Build an zwei TypeScript-Zielen mit `TS2307: Cannot find module '//resources/cr_elements/i18n_mixin_lit.js'`. Ursache identisch: `cr_elements/BUILD.gn:90` gated die Lit-Mixins hinter demselben Muster.

**Die Lösung war, den einen Schalter zu setzen statt jede Bedingung einzeln aufzuweichen.**

`is_desktop_android` wird im ganzen Baum nur an 41 Stellen erwähnt. Außerhalb der GN-Tore wirkt es an drei Stellen, davon zwei ausschließlich bei `current_cpu == "x64"` — auf arm64 also wirkungslos. Die einzige nennenswerte Vergrößerung der Baufläche kommt aus `chrome_paks.gni:517`, das zusätzlich `discards_resources.pak` und `management_resources.pak` aufnimmt.

### Endgültige Konfiguration

```gn
is_desktop_android = true
enable_service_discovery = false
dcheck_always_on = false
treat_warnings_as_errors = false
disable_android_lint = true
```

`enable_desktop_android_extensions` und `enable_extensions_core` folgen automatisch. `enable_extensions` bleibt `false` — das ist gewollt, es ist der Desktop-Pfad.

`enable_service_discovery = false` schaltet die mDNS-Extension-API ab, die den Media Router nachzieht. Kein Verlust: Cast-Discovery und Netzwerkdrucker-Erkennung braucht ein Telefon-Browser nicht.

### Die einzige Quelltextänderung

`extensions/common/extension_features.cc`, zwei Zeilen:

```
Zeile 117:  kExtensionManifestV2Unsupported  → FEATURE_DISABLED_BY_DEFAULT
Zeile 122:  kExtensionManifestV2Disabled     → FEATURE_DISABLED_BY_DEFAULT
```

Warum das reicht: `CalculateCurrentExperimentStage()` in `extensions/browser/manifest_v2_experiment_manager.cc` prüft zuerst `kExtensionManifestV2Unsupported` (→ `kUnsupported`), dann `kExtensionManifestV2Disabled` (→ `kDisableWithReEnable`), sonst `kWarning`. Auf Stufe `kWarning` liefern `ShouldDisableLegacyExtensions`, `ShouldBlockLegacyExtensionEnableForStage` und `ShouldBlockUnpackedExtensions` alle `false`.

`kAllowLegacyMV2Extensions` wird nicht gebraucht — das greift nur in den höheren Stufen.

Die Manifest-Prüfung ist kein Hindernis: `kMinimumExtensionManifestVersion` steht als `static constexpr` auf 2, und `IsManifestSupported` gibt bei `manifest_version == 2` lediglich eine Warnung aus und dann `true`.

### Nachgewiesen nicht nötig

Die drei BUILD.gn-Einzeiler aus dem ersten Anlauf wurden zurückgesetzt. `gn gen` läuft ohne sie durch (62575 Targets), weil alle drei Bedingungen `is_desktop_android` bereits nannten.

> **Die gesamte Aktivierung ist eine reine `args.gn`-Angelegenheit. Einzige Quelltextänderung sind die zwei MV2-Zeilen.**

## Abnahmekriterien

- [ ] Eine MV2-Erweiterung lässt sich laden
- [ ] Sie bleibt nach einem Neustart des Browsers aktiviert (sonst steht die Stufe noch auf `kDisableWithReEnable`)
- [ ] Background-Page läuft, `chrome.webRequest` blockiert tatsächlich
- [ ] Geklärt, wie Erweiterungen auf das Gerät kommen — Googles native UI oder eigener Weg

## Offene Punkte

- Von Kiwis 12 Eingriffen in `chrome/browser/extensions` ist noch unklar, welche Googles Pfad bereits abdeckt. Erst nach lauffähigem Build prüfen.
- Der Chrome Web Store lehnt MV2 serverseitig ab, dazu gibt es eine clientseitige Prüfung in `webstore_private/extension_install_status.cc`. Entpackt oder als CRX laden dürfte gehen, der Store-Weg vermutlich nicht.
- **Langfristig:** Ab 150 fielen die Developer-Flags, ab 151 der MV2-Feature-Code. Da MV2 harte Anforderung ist, wird jeder künftige Versionssprung einen Revert-Satz brauchen. Umfang noch nicht gemessen — siehe `scripts/measure_mv2_removal.sh`.
