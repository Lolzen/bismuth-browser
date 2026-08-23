# Versionssprung 150 → 151

**Status:** abgeschlossen
**Von:** 150.0.7871.249
**Auf:** 151.0.7922.176

---

## Ergebnis vorweg

Fünf der neun Patches scheiterten beim Anwenden, aber keiner davon inhaltlich
schwer. Die wirkliche Arbeit lag woanders: an einem Fehler, den wir seit 149 mit
uns herumgetragen haben, ohne ihn zu verstehen.

**9001 wird sogar kleiner.** `extension_features.cc` fällt ersatzlos heraus, weil
das letzte MV2-Feature aus dem Baum verschwunden ist.

---

## Vorher messen

Bei 150 haben wir erst synchronisiert und dann gesehen, was kommt. Bei 151 ging
es andersherum — und das war besser. Die Tags lassen sich holen und lesen, ohne
den Arbeitsbaum anzufassen:

```
git fetch origin tag <tag> --no-tags
git diff --name-status <alt>..<neu> -- extensions/ | grep "^D"
git grep -n "<muster>" <tag> -- <pfad>
git show <tag>:<pfad>
```

Damit stand die Bilanz fest, bevor überhaupt synchronisiert wurde: Der
Experiment-Manager verschwindet, der Hebel `g_allow_mv2_for_testing` zieht mit in
`extensions/browser/manifest_v2_handler.cc` um,
`kMinimumSupportedManifestVersion` bleibt bei 2.

---

## Der wichtigste Fund: gescheiterte Patches liegen ganz

`git apply --3way` wendet einen Patch **entweder ganz oder gar nicht** an.
Scheitert er an einer Datei, bleiben auch die konfliktfreien Dateien liegen.

Bei 9001 fiel das nicht auf, weil nur `extension_features.cc` einen Konflikt
zeigte. Tatsächlich fehlten auch `file_enumerator_posix.cc` und
`api_sources.gni` — und ohne die Rekursionskorrektur im Datei-Aufzähler
scheiterte jedes Laden einer Erweiterung mit
`Failed to copy extension directory`.

Seitdem gehört `scripts/common/verify_applied.sh` fest in den Ablauf. Es
vergleicht für jeden Patch die Zieldateien mit dem, was im Baum tatsächlich
geändert ist, und meldet die Fehlenden. Nachziehen geht gezielt:

```
git apply --3way --include='<pfad>' patches/<patch>
```

---

## Die fünf Konflikte

| Datei | Auflösung |
|---|---|
| `chromium_strings.grd` | zurücksetzen, Branding-Scripts erneut laufen lassen |
| `chrome_feature_list.cc` | nur unsere Zeile behalten; die Nachbarzeile war Kontext aus 150 |
| `manager.css` | beide Seiten behalten |
| `extension.cc` | unsere Seite; 151 hat die Testhilfe zum Unterdrücken der Warnung entfernt |
| `extension_info_generator.cc` | unsere Seite; der Manager heißt jetzt `ManifestV2Handler` |
| `TabbedAppMenuPropertiesDelegate.java` | unsere Seite; `buildExtensionsMenuItem` nimmt jetzt einen Parameter |

---

## Der alte Fehler, endlich verstanden

Seit 149 verschwanden kopierte Erweiterungen — mal nach Stunden, mal nach einem
Neustart, ohne eine einzige Chromium-Zeile im Protokoll. In 149 sind wir ihm
ausgewichen, indem wir **außerhalb** des Zielbereichs aufbauen und mit einem
`Move` einsetzen. Das half beim Kopieren, aber das Ziel lag weiterhin im
Profilverzeichnis.

Auf 151 kippte es erneut: Nach mehrmaligem Ab- und Anschalten und dem Laden einer
zweiten Erweiterung war das Verzeichnis der ersten **komplett leer** — und zwar
schon vor dem zweiten Ladevorgang. Damit schied auch unser eigener Aufräumlauf
aus, denn die beiden Hash-Präfixe überschneiden sich nicht.

**Die Lösung war, das Ziel aus dem Profil herauszunehmen.**

```
vorher:  app_chrome/Default/UnpackedExtensions/<hash>-<zeit>
jetzt:   app_chrome/BismuthExtensions/<hash>-<zeit>
```

Eine Ebene höher, neben Chromiums eigenen Komponentenverzeichnissen wie
`OriginTrials` und `OptimizationHints` — außerhalb dessen, was die
Profilverwaltung als ihr Revier betrachtet. Nach dem Umbau hielten die
Erweiterungen mehreren Testrunden stand.

Ein Beweis für den Verursacher ist das nicht; wir haben ihn nie im Protokoll
gesehen. Aber das Muster ist eindeutig, und der Umzug kostet nichts.

**Nebenwirkung:** Nach dem Umbau zeigen alle bisherigen Registrierungen ins
Leere. Erweiterungen müssen einmal neu geladen werden.

---

## Umbenennungen, die der Compiler nannte

`AccountsChangeObserver.onCoreAccountInfosChanged` heißt in 151
`onAccountsChanged`. Unser `SystemAccountManagerDelegate` stammt aus 132; solche
Nachzüge sind bei jedem Sprung zu erwarten und harmlos, weil der Compiler sie
beim Namen nennt.

---

## Ablauf, der sich eingespielt hat

1. Zweig für die alte Basis anlegen
2. Messen, bevor synchronisiert wird
3. Vom Zweig lösen, `CHROMIUM_TARGET` und `.gclient` umstellen, `gclient sync`
4. `apply_patches.sh`
5. **`verify_applied.sh`** — neu, und unverzichtbar
6. Konflikte auflösen, fehlende Dateien nachziehen
7. `gn gen`, bauen
8. Prüfliste durchgehen
9. `split_patches.sh`, `verify_applied.sh` erneut
10. Dokumentation, Commit, Zweig für die neue Basis

---

## Offen

Die Bestätigung der Google-Kontoanmeldung funktioniert nicht. Dasselbe Verhalten
tritt in anderen Chromium-Abkömmlingen auf, etwa SlimJet — es ist also keine
Eigenheit dieser Patches, sondern betrifft Builds ohne Googles Signatur
allgemein. Anmeldung und Kontenliste funktionieren; die Synchronisierung nicht.
