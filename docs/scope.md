# scope.md — was übernommen wird und was nicht

Grundlage ist die Patch-Fläche aus Kiwis `src.next`, gemessen gegen den
Anker-Commit `b2a61e552c94` (Chromium 105.0.5195.24, August 2022):
**577 Dateien, 13.806 Einfügungen, 834 Löschungen.**

Nach den Entscheidungen unten sind es in Bismuth rund **50 geänderte Dateien**,
davon 15 Bilddateien fürs Icon.

---

## Umgesetzt

| Feature | Meilenstein |
|---|---|
| Extensions auf Android | 9001 |
| Manifest V2 | 9001 |
| Entpackte Erweiterungen über SAF laden | 9001 |
| `browserAction`-Schema | 9001 |
| Classic-Tab-Switcher mit Umschalter | 9002 |
| Erweiterungen in den App-Speicher übernehmen | 9003 |
| Aufräumlauf für verwaiste Kopien | 9003 |
| Web Store in Desktop-Fassung | 9004 |
| Branding — Name, Icons, Paketname, Texte | 9005 |
| Erweiterungen-Menü repariert | 9006 |
| Keine MV2-Deprecation | 9007 |
| Fortschrittsanzeige beim Laden | 9009 |
| **Kontenverwaltung und Anmeldung** | **9010** |

Die Nummer 9008 blieb frei — die internen Texte wurden Teil von 9005.

---

## Gestrichen

| Feature | Grund |
|---|---|
| Night Mode | Chromium liefert Force Dark inzwischen selbst |
| Bottom Toolbar | Adressleiste unten ist heute Standard |
| New Tab Page | Standard-NTP gefällt besser als Kiwis Ersatz |
| Übersetzungs-Einstellungen | zu viel Aufwand für zu wenig Nutzen |
| Adblock und Popup-Blocker | durch Erweiterungen abgedeckt |
| User-Scripts | durch Erweiterungen abgedeckt |
| Suchmaschinen-Loader | lädt von `settings.kiwibrowser.com` bei jedem Netzwerkwechsel; bei eingestelltem Projekt ein Hijacking-Risiko |
| User-Agent-Spoofing (generell) | zielte auf Website-Verhalten von 2022; der Web-Store-Fall ist über 9004 gelöst |
| Icons und Branding von Kiwi | Bismuth hat eigene |
| `.github`-Workflows | Kiwis Repo-Infrastruktur |
| Übersetzungen (Crowdin) | eigener Prozess nötig |
| Signin-Promo | nicht relevant |
| `search_url_fetcher.{cc,h}` | gehört zum Suchmaschinen-Loader |

Innerhalb von `tab_ui` ersatzlos gestrichen:
`StartSurfaceTabSwitcherActionMenuCoordinator` (Start Surface entfernt),
`NewTabTileMediator` (Kachel existiert nicht mehr), `PseudoTab` (war eine
temporäre Abstraktion).

---

## Als Sackgasse verworfen

**LIST-Tab-Switcher.** Chromiums vertikale Listenansicht, entfernt nach
138.0.7204.310. Vollständig portiert und nach sieben Abstürzen an Rasterannahmen
verworfen, weil das eigentliche Ziel Kiwis „classic" war und nicht LIST. Liegt
als `patches/archive/9002-tabswitcher-list-archiv.patch`.

**DICE auf Android.** Der webbasierte Anmeldeweg des Desktops lässt sich nicht
einschalten: `enable_dice_support` zieht die Desktop-Profilverwaltung mit herein,
die an der Views-Oberfläche hängt (`assert(!is_android)`). Fünf Buildskripte
ließen sich absichern, danach blieb `batch_upload` mit sechs verstreuten
Abnehmern in Testzielen übrig. Details in `docs/port-notes/9010`.

**Content-Setting-Ausnahme über `setRequestDesktopSiteContentSettingsForUrl`.**
Erzeugt `[*.]google.com` statt eines Host-Eintrags und trifft damit auch die
Suche. Ersetzt durch `setContentSettingCustomScope` in 9004.

**User-Agent-Spoofing im Netzwerk-Stack für den Web Store.** Kiwis Weg in 149
nachgebaut, ohne Wirkung. Zurückgenommen.

**Staging-Verzeichnis neben dem Ziel.** Erster Anlauf gegen den Kopierfehler in
9003; lag im selben gefährdeten Bereich. Ersetzt durch das CRX-Muster mit
`<Profil>/Temp`.

**`hasMv2DeprecationWarning_` in `item.ts`.** Folgenlos, weil der zugehörige
Deaktivierungsgrund bei laufenden Erweiterungen nicht gesetzt ist.
Zurückgenommen.

---

## Offene Fehler

| Punkt | Einordnung |
|---|---|
| Sporadischer Fehlschlag beim Laden einer Erweiterung | Wiederholung behebt es |
| Verzeichnisse ganz entfernter Erweiterungen bleiben liegen | braucht die Erweiterungsliste aus dem UI-Thread |
| uBlock-Popup in der Symbolleiste | ungeprüft |
| Weitere fehlende API-Schemata | reaktiv, je Fall ein Einzeiler |

Der Absturz beim Anmelden ist mit 9010 behoben. Ob Sync dauerhaft durchläuft,
war beim Schreiben noch nicht bestätigt — Googles Kontoprüfung lief.

---

## Vertagt

**Umschalter für das Herkunfts-Abzeichen.** Das orange Abzeichen an entpackten
Erweiterungen ist zutreffend, erscheint in Bismuth aber zwangsläufig immer. Ein
Umschalter dafür bräuchte eine Profil-Einstellung im `PrefService`, aus Java
gesetzt und beim Befüllen von `loadTimeData` gelesen — fünf Dateien für ein
kosmetisches Detail.

**Discover-Feed gegen Extensions.** Unter `is_desktop_android` wird der
Feed-Code nicht kompiliert. Der Ausweg wäre
`enable_desktop_android_extensions` ohne `is_desktop_android`, mit vier bekannten
GN-Assertions als Preis und unbewiesenem Ausgang. Wird beim Versionssprung neu
bewertet.

---

## Noch zu tun

**Vor dem Versionssprung**

- `bootstrap.sh` einmal echt testen
- Googles Kontoprüfung abwarten und 9010 bestätigen

**Der Versionssprung selbst**

- Die 149er Fassung als Branch archivieren
- Auf 150 oder 151 heben, MV2 per Rückportierung erhalten
- Dabei die Frage `is_desktop_android` gegen
  `enable_desktop_android_extensions` neu entscheiden

Der Versionssprung ist der einzige verbliebene große Brocken.
