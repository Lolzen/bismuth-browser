# 9005 — Branding

**Status:** fertig
**Patch:** `patches/9005-branding.patch`
**Umfang:** rund 24 Dateien, davon 15 Bilddateien

---

## Absicht

Aus dem Chromium-Build ein eigenständiges Produkt machen: eigener Name, eigenes
Icon, eigener Paketname — und die internen Texte entsprechend.

---

## Paketname

`chrome/android/chrome_public_apk_tmpl.gni`, Zeile 28:

```gn
chrome_public_manifest_package = "org.bismuth.browser"
```

**Eine Zeile genügt.** Der Wert wird über eine Manifest-Variable eingesetzt;
Provider-Authorities und Berechtigungen ziehen automatisch mit.

Zu beachten: Beim Installieren entsteht dadurch eine **neue App**. Das Profil ist
leer, Erweiterungen müssen neu geladen werden. Dafür lässt sich Bismuth neben
einem gewöhnlichen Chromium betreiben.

---

## Anzeigename

`chrome/android/java/res_chromium_base/values/channel_constants.xml` — vier
Zeichenketten: `app_name` und drei Widget-Titel.

Als Label steht dort **Bismuth**, nicht „Bismuth Browser". Unter dem Icon ist
wenig Platz, Android kürzt sonst ab. Der volle Name gehört ins README und in
Store-Einträge.

---

## Icons

Chromium 149 benutzt für den Browser ein Adaptive Icon. Die Struktur ist
verschachtelter, als es zunächst aussieht:

| Datei | Rolle |
|---|---|
| `res_base/drawable/ic_launcher.xml` | Adaptive Icon, eckige Maske |
| `res_base/drawable/ic_launcher_round.xml` | Adaptive Icon, runde Maske |
| `res_chromium_base/mipmap-*/layered_app_icon.png` | Vordergrund, transparent |
| `res_chromium_base/mipmap-*/layered_app_icon_background.png` | Hintergrund |
| `res_chromium_base/mipmap-*/app_icon.png` | Legacy, für API < 26 |
| `res_chromium_base/drawable/themed_app_icon.xml` | Monochrom, ab Android 13 |

**Die beiden Adaptive Icons sind unterschiedlich aufgebaut.** Im Original nimmt
`ic_launcher.xml` eine Farbe als Hintergrund und das PNG als Vordergrund, während
`ic_launcher_round.xml` die ganze Grafik im Hintergrund-PNG führt und einen
transparenten Platzhalter als Vordergrund benutzt. Wer das übersieht, bekommt ein
Icon, das nur aus dem Hintergrund besteht.

In Bismuth verweisen beide XML auf dieselben Ebenen: Kristall im Vordergrund,
Marineblau im Hintergrund.

**Größen:** Vordergrund und Hintergrund 108 / 162 / 216 / 324 / 432 px, Legacy
48 / 72 / 96 / 144 / 192 px. Das Motiv muss in den inneren zwei Dritteln der
Kantenlänge sitzen, sonst beschneidet die Maske es.

**`min_sdk_version` ist 29.** Jedes Gerät, das das APK installieren kann, benutzt
das Adaptive Icon — die Legacy-PNGs kommen für den Startbildschirm nie zum Zug.

**Monochrom** ist eine Vektorgrafik. Die Vorlage von Chromium beschränkt den
Inhalt per `clip-path` auf die mittleren 36 von 90 Einheiten; für ein größeres
Motiv muss diese Zeile entfallen.

**Optimierung:** `pngquant --quality=80-98 --skip-if-larger --strip` reduziert die
Dateien deutlich, ohne bei flächigen Grafiken sichtbare Streifen zu erzeugen. Die
Originale liegen unter `branding/icon_pngs_original`.

---

## Interne Texte

Vier Dateien:

```
chrome/app/theme/chromium/BRANDING
chrome/app/chromium_strings.grd            615 Zeilen
chrome/app/settings_chromium_strings.grdp  155 Zeilen
components/components_chromium_strings.grd  21 Zeilen
```

Ein pauschales Ersetzen von „Chromium" wäre falsch. Ausgenommen bleiben:

- `The Chromium Authors` — Urheberrechtsangaben
- `chromium.org` — Verweise auf das Projekt
- `ChromiumOS` — ein anderes Produkt

Der letzte Punkt ist die Falle: Eine Ausnahmeliste mit „Chromium OS" trifft die
zusammengeschriebene Form nicht, und aus `ChromiumOS` wird stillschweigend
`BismuthOS`. Im vorliegenden Fall betraf das 20 Stellen.

In `BRANDING` werden `PRODUCT_FULLNAME`, `PRODUCT_SHORTNAME`,
`PRODUCT_INSTALLER_*` und `MAC_BUNDLE_ID` geändert. `COMPANY_FULLNAME` und
`COPYRIGHT` bleiben bei „The Chromium Authors" — das ist rechtlich korrekt, der
Code stammt von ihnen.

---

## Offen

- Titel und Beschreibung des Tab-Switcher-Schalters stehen als Literale im XML
  statt als Strings in der `.grd`. Möglich, weil `disable_android_lint = true`
  gesetzt ist.
- Eine deutsche Fassung dieser Texte fehlt.
