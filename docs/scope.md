# scope.md — was übernommen wird und was nicht

Grundlage ist die Patch-Fläche aus Kiwis `src.next`, gemessen gegen den
Anker-Commit `b2a61e552c94` (Chromium 105.0.5195.24, August 2022):
**577 Dateien, 13.806 Einfügungen, 834 Löschungen.**

Nach den Entscheidungen unten stehen davon **11 geänderte Dateien** in Bismuth.

---

## Umgesetzt

| Feature | Meilenstein | Umfang |
|---|---|---|
| Extensions auf Android | 9001 | `args.gn` plus 2 Zeilen |
| Manifest V2 | 9001 | 2 Zeilen in `extension_features.cc` |
| Entpackte Erweiterungen laden | 9001 | 8 Zeilen in `file_enumerator_posix.cc` |
| `browserAction`-Schema | 9001 | 10 Zeilen in `api_sources.gni` |
| Classic-Tab-Switcher | 9002 | rund 60 Zeilen, 4 Dateien |
| Erweiterungen in den App-Speicher | 9003 | rund 118 Zeilen, 2 Dateien |
| Web Store in Desktop-Fassung | 9004 | rund 25 Zeilen, 2 Dateien |

---

## Zurückgestellt

**User-Scripts** (`PersonalizeResults.java`, 7 Commits bei Kiwi).
Bleibt in der Pipeline, hat aber niedrige Priorität: Da Erweiterungen laufen,
deckt eine User-Script-Extension denselben Zweck ab. Vor einer Umsetzung ist
zuerst zu prüfen, ob der Punkt überhaupt noch gebraucht wird.

**Discover-Feed.**
Nicht umsetzbar, solange `is_desktop_android = true` gilt — der Feed-Code wird
in der Desktop-Produktvariante gar nicht kompiliert
(`gn refs out/Ext //components/feed/core/v2:core` liefert nichts). Der Ausweg
wäre `enable_desktop_android_extensions` ohne `is_desktop_android`, mit vier
bekannten GN-Assertions als Preis und unbewiesenem Ausgang. Wird beim
Versionssprung neu bewertet.

**Adblock und Popup-Blocker.**
Vermutlich hinfällig, seit uBlock Origin läuft.

---

## Gestrichen

| Feature | Grund |
|---|---|
| Night Mode | Chromium liefert Force Dark inzwischen selbst |
| Bottom Toolbar | Adressleiste unten ist heute Standard |
| New Tab Page | Standard-NTP gefällt besser als Kiwis Ersatz |
| Übersetzungs-Einstellungen | zu viel Aufwand für zu wenig Nutzen |
| Suchmaschinen-Loader | lädt von `settings.kiwibrowser.com` bei jedem Netzwerkwechsel; bei eingestelltem Projekt ein Hijacking-Risiko |
| User-Agent-Spoofing (generell) | zielte auf Website-Verhalten von 2022; der Web-Store-Fall ist über 9004 gelöst |
| Icons und Branding von Kiwi | Bismuth bekommt eigene |
| `.github`-Workflows | Kiwis Repo-Infrastruktur |
| Übersetzungen (Crowdin) | eigener Prozess nötig |
| Signin-Promo | nicht relevant |
| Desktop-only-Code | betrifft Bismuth nicht |
| `search_url_fetcher.{cc,h}` | gehört zum Suchmaschinen-Loader |

Innerhalb von `tab_ui` ersatzlos gestrichen: `StartSurfaceTabSwitcherActionMenuCoordinator`
(Start Surface entfernt), `NewTabTileMediator` (Kachel existiert nicht mehr),
`PseudoTab` (war eine temporäre Abstraktion).

---

## Als Sackgasse verworfen

**LIST-Tab-Switcher.**
Chromiums vertikale Listenansicht, entfernt nach 138.0.7204.310. Vollständig
portiert — `TabListView.java`, `TabListViewBinder.java`, Layout, zwei Drawables,
fünf Dimensionswerte — und nach sieben Abstürzen an Rasterannahmen verworfen,
weil das eigentliche Ziel Kiwis „classic" war und nicht LIST. Liegt als
`patches/9002-tabswitcher-list-archiv.patch`.

**Content-Setting-Ausnahme über `setRequestDesktopSiteContentSettingsForUrl`.**
Erzeugt `[*.]google.com` statt eines Host-Eintrags und trifft damit auch die
Suche. Ersetzt durch `setContentSettingCustomScope` in 9004.

**User-Agent-Spoofing im Netzwerk-Stack für den Web Store.**
Kiwis Weg in 149 nachgebaut, ohne Wirkung. Zurückgenommen.

---

## Offene Punkte

| Punkt | Einordnung |
|---|---|
| Sporadischer Fehlschlag beim Laden einer Erweiterung | instrumentiert, tritt meist nach APK-Update auf |
| Menüeintrag „Erweiterungen öffnen" stürzt ab | besteht seit dem ersten Ext-Build |
| Fortschrittsanzeige beim Kopieren | kosmetisch |
| uBlock-Popup in der Symbolleiste | ungeprüft |
| Weitere fehlende API-Schemata (`contextMenus`, `pageAction`) | je Fall ein Einzeiler |
| Umschalter wirkt erst beim Neuaufbau des Switchers | verschmerzbar |

---

## Noch zu tun

**Vor dem ersten Commit**

- App-Icon in icon-tauglicher Fassung
- Paketname auf `org.bismuth.browser` ändern
- `bootstrap.sh` testen

**Danach**

- Versionssprung auf 150 oder 151 mit MV2-Rückportierung

Der Versionssprung ist der einzige verbliebene große Brocken. Dabei wird die
Patch-Serie ohnehin überarbeitet — der richtige Moment, um die Frage
`is_desktop_android` gegen `enable_desktop_android_extensions` neu zu
entscheiden und damit auch die Feed-Frage.
