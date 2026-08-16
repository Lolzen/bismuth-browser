# 9007 — Keine MV2-Deprecation

**Status:** fertig
**Patch:** `patches/9007-mv2-no-deprecation.patch`
**Umfang:** 2 Dateien, rund 12 Zeilen

---

## Absicht

Manifest V2 ist das Kernstück dieses Browsers. Ein Hinweis, der es als veraltet
kennzeichnet, ist hier sachlich falsch — er soll verschwinden.

---

## Umsetzung

**Warnung beim Laden** — `extensions/common/extension.cc`, in
`IsManifestSupported`:

```cpp
if (type == Manifest::Type::kExtension && manifest_version == 2 &&
    Manifest::IsUnpackedLocation(location) &&
    !g_silence_deprecated_manifest_version_warnings) {
  *warning = errors::kManifestV2IsDeprecatedWarning;
}
```

Der Block entfällt. Damit erscheint beim Installieren keine Warnung mehr, und die
Detailansicht bleibt frei davon.

**Hinweisfeld in der Erweiterungsseite** —
`chrome/browser/extensions/api/developer_private/extension_info_generator.cc`:

```cpp
info.is_affected_by_mv2_deprecation = false;
info.did_acknowledge_mv2_deprecation_notice = false;
```

An die Stelle des `ManifestV2ExperimentManager`-Zugriffs. Da die Oberfläche ihre
gesamte Deprecation-Darstellung an dieser Angabe aufhängt, verschwinden Panel und
Hinweise damit von selbst — inklusive des `CHECK`, das den Manager voraussetzte.

---

## Was bewusst nicht angefasst wurde

**`item.ts` in der WebUI.** Ein Versuch, `hasMv2DeprecationWarning_()` auf
`false` zu setzen, blieb folgenlos: Die Methode liefert
`this.data.disableReasons.unsupportedManifestVersion`, und dieser
Deaktivierungsgrund ist bei einer laufenden Erweiterung ohnehin nicht gesetzt.
Die Änderung wurde zurückgenommen, um die Patchfläche klein zu halten.

**Das orange Abzeichen am Erweiterungssymbol** ist keine MV2-Warnung, sondern der
Herkunftshinweis `extensions-icons:unpacked` aus `computeSourceIndicatorIcon_`.
Er ist zutreffend — nur erscheint er in Bismuth zwangsläufig immer, weil MV2
keinen anderen Ladeweg hat. Er bleibt.

**Die leere Fläche in der Detailansicht** nach dem Entfernen des Hinweises ist
kein Fehler. `detail_view.css` gibt dem Element `:host { height: 100% }` — die
Karte füllt die Fensterhöhe, und was vorher der MV2-Block ausfüllte, ist jetzt
sichtbar leer. Auf dem Desktop fällt das nicht auf.

---

## Beim Versionssprung

Dieser Patch hängt eng an 9001. Ab Chromium 150 sind die Flags weg, die MV2
überhaupt erlauben; ohne 9001 in neuer Form ist 9007 gegenstandslos.

Umgekehrt gilt: Sollte MV2 über einen Rückportierungs-Patch am Leben gehalten
werden, muss auch dieser Patch neu geschnitten werden — die betroffenen Stellen
werden sich verschoben haben.
