# 9001 — Extensions und Manifest V2 auf Android

**Status:** fertig, auf 150 bestätigt
**Patch:** `patches/9001-extensions-mv2.patch`
**Umfang:** 4 Dateien

---

## Absicht

Das Erweiterungssystem auf Android einschalten und Manifest V2 verfügbar halten.
Das ist der Grund, aus dem dieses Projekt existiert.

---

## Was der Patch enthält

| Datei | Was |
|---|---|
| `base/files/file_enumerator_posix.cc` | Rekursion über SAF-Pfade |
| `chrome/common/extensions/api/api_sources.gni` | fehlende API-Schemata, u. a. `browserAction` |
| `extensions/common/extension_features.cc` | `kExtensionManifestV2Unsupported` aus |
| `extensions/browser/manifest_v2_experiment_manager.cc` | `g_allow_mv2_for_testing` an |

Das Einschalten des Erweiterungssystems selbst steht nicht im Patch, sondern in
der `args.gn`: `is_desktop_android = true`.

---

## Der SAF-Aufzähler

`base::FileEnumerator` konnte über Storage-Access-Framework-Pfade nicht in
Unterverzeichnisse absteigen. Der Grund: Bei der Rekursion wurde der
Content-URI des Unterverzeichnisses auf den Stapel gelegt statt des virtuellen
Pfades, und beim nächsten Durchlauf ging der Bezug verloren.

**Zweite Eigenheit, die uns später eingeholt hat:** Über SAF reicht
`ListContentUriDirectory` den angeforderten `file_type_` an die Auflistung durch.
Eine rekursive Aufzählung mit `FILES` allein bekommt keine Unterverzeichnisse zu
sehen und bleibt deshalb auf der obersten Ebene stehen — ohne Fehlermeldung. Wer
zählen oder kopieren will, muss `FILES | DIRECTORIES` anfordern und
Verzeichnisse selbst überspringen.

---

## Manifest V2 in 149

Zwei Features standen auf `ENABLED` und mussten auf `DISABLED`:
`kExtensionManifestV2Disabled` und `kExtensionManifestV2Unsupported`. Beide
speisten die Experimentstufe, und `ShouldDisableLegacyExtensions` verzweigte über
diese Stufe. Mit beiden aus blieb die Stufe auf „keine", und MV2 lief.

---

## Manifest V2 in 150 — was sich geändert hat

**Drei Commits mit MV2-Bezug** liegen zwischen den Versionen, zusammen 28
eingefügte und 6 gelöschte Zeilen. Keine gelöschten Dateien. Der Umbau ist also
klein — aber wirksam.

**`kExtensionManifestV2Disabled` ist ersatzlos entfernt.** Unser Patch versuchte,
eine Zeile umzulegen, die es nicht mehr gibt; der Konflikt löst sich, indem man
die Zeile fallen lässt.

**`ShouldDisableLegacyExtensions` ist umgezogen** — von `extension_features.cc`
nach `extensions/browser/manifest_v2_experiment_manager.cc` — und wertet die
Stufe **nicht mehr aus**:

```cpp
bool ShouldDisableLegacyExtensions(MV2ExperimentStage stage) {
  if (g_allow_mv2_for_testing) {
    return false;
  }
  return true;
}
```

Der Parameter steht nur noch da. MV2 ist fest abgeschaltet, und das globale
Kennzeichen ist der einzige verbliebene Hebel.

**Die Lösung ist deshalb eine Zeile:**

```cpp
bool g_allow_mv2_for_testing = true;
```

Chromium hat den Schalter selbst und benutzt ihn aus Tests heraus
(`ScopedTestMV2Enabler`). Wir lassen ihn dauerhaft an. Der Name sagt „für
Tests", die Wirkung ist genau die gewünschte, und Google pflegt ihn, weil die
eigenen Tests darauf angewiesen sind.

---

## Warum nicht über die Flags

Nach dem Sprung liefen MV2-Erweiterungen zunächst gar nicht, dann — mit dem Flag
`#temporary-unexpire-flags-m149` — wieder, verschwanden aber **mit der Zeit**
erneut.

Der Grund: Chromium versieht Flags mit einem Verfallsdatum. Danach werden sie
zwangsweise zurückgesetzt, egal was im Quelltext steht. Patches, die an Flags
ansetzen, werden dadurch **still wirkungslos** — sie wenden sauber an, bauen
durch und tun nichts.

Deshalb sitzt der Eingriff jetzt am globalen Kennzeichen und nicht an den Flags.
Das ist unabhängig vom Verfall und überlebt Neubewertungen zur Laufzeit.

`kExtensionManifestV2Unsupported` bleibt trotzdem im Patch: Es speist weiterhin
die Stufenberechnung, und die steuert Nebenwirkungen wie das Blockieren des
Aktivierens und den Hinweisdialog.

---

## Für den Sprung auf 151

Laut Ankündigung werden dort die verbliebenen MV2-Dateien entfernt. Damit wird
aus dem Einzeiler eine Rückportierung.

**Vorgehen, das sich anbietet:**

Vor dem Sprung die betroffenen Dateien ermitteln:

```
git diff --name-status 150.0.7871.249..<151-tag> -- extensions/ | grep "^D"
```

Die Dateien danach aus dem 150er **Tag** holen, nicht aus dem Arbeitsbaum:

```
git show 150.0.7871.249:<pfad> > <ziel>
```

So bleibt Googles unveränderter Stand die Grundlage, und unsere Anpassungen
liegen als Patch darüber. Andernfalls vermischen sich beide Ebenen, und beim
übernächsten Sprung ist nicht mehr erkennbar, was von wem stammt.

Ob das ein überschaubarer Nachtrag oder ein eigenes Vorhaben wird, hängt davon
ab, ob nur der Experiment-Manager verschwindet oder auch die Unterstützung im
Erweiterungs-Kern. Das lässt sich vorab mit
`scripts/common/measure_mv2_removal.sh` abschätzen.
