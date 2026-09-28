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
| Classic-Tab-Switcher mit Umschalter | 9002 |
| Erweiterungen in den App-Speicher übernehmen | 9003 |
| Aufräumlauf für verwaiste Kopien | 9003 |
| Web Store in Desktop-Fassung | 9004 |
| Branding — Name, Icons, Paketname, Texte | 9005 |
| Erweiterungen-Menü repariert | 9006 |
| Keine MV2-Deprecation | 9007 |
| Fortschrittsanzeige beim Laden | 9009 |
| Browser-Anmeldung abgeschaltet | 9010 |
| **Erweiterungs-Symbolleiste auf dem Telefon** | **9011** |

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
| Erweiterungen im Hauptmenü (Kiwis Weg) | überflüssig geworden durch 9011 |
| Suchmaschinen-Loader | lädt von `settings.kiwibrowser.com` bei jedem Netzwerkwechsel; bei eingestelltem Projekt ein Hijacking-Risiko |
| User-Agent-Spoofing (generell) | zielte auf Website-Verhalten von 2022; der Web-Store-Fall ist über 9004 gelöst |
| Icons und Branding von Kiwi | Bismuth hat eigene |
| `.github`-Workflows | Kiwis Repo-Infrastruktur |
| Übersetzungen (Crowdin) | eigener Prozess nötig |
| Signin-Promo | nicht relevant |

---

## Als Sackgasse verworfen

**LIST-Tab-Switcher.** Chromiums vertikale Listenansicht, entfernt nach
138.0.7204.310. Vollständig portiert und nach sieben Abstürzen an Rasterannahmen
verworfen. Liegt als `patches/archive/9002-tabswitcher-list-archiv.patch`.

**DICE auf Android.** Der webbasierte Anmeldeweg des Desktops lässt sich nicht
einschalten: `enable_dice_support` zieht die Desktop-Profilverwaltung mit herein,
die an der Views-Oberfläche hängt. Details in der alten Notiz zu 9010
(`docs/port-notes/old_moot/`).

**Kontenverwaltung aus 132.** Der `SystemAccountManagerDelegate` machte die
Anmeldung möglich, Sync aber nie: Google hat Chromium-Builds im März 2021 von
Chrome Sync ausgeschlossen. Übrig blieben Fehler in den Anmeldeabläufen. Liegt
als `patches/archive/9010-account-manager-delegate.patch`; 9010 schaltet die
Browser-Anmeldung jetzt ab.

**Discover-Feed.** Drei Annahmen erwiesen sich als falsch: Der Feed wird sehr
wohl kompiliert, er ist auf der Neuer-Tab-Seite auch sichtbar, und er schließt
sich nicht mit Extensions aus. Er lädt nur nie Inhalte — sein Renderer ist
Googles geschlossene Bibliothek **XSurface**, die im echten Chrome als
nachladbares Modul aus dem internen Baum kommt und nie öffentlich war.
`XSurfaceProcessScopeProvider` liefert ohne registrierte Hooks schlicht `null`.
Kein Chromium-Abkömmling kann den Feed anzeigen.

**Kiwis `AppMenuBridge`.** Eine eigene JNI-Brücke, die Erweiterungen als
serialisierte Zeichenkette ins Hauptmenü brachte. 2021 klug, heute überflüssig —
Chromium hat die gesamte Infrastruktur, sie war nur nicht für Telefone
verdrahtet.

**Content-Setting-Ausnahme über `setRequestDesktopSiteContentSettingsForUrl`.**
Erzeugt `[*.]google.com` statt eines Host-Eintrags. Ersetzt durch
`setContentSettingCustomScope` in 9004.

**Staging-Verzeichnis neben dem Ziel** und später **das Zielverzeichnis im
Profil**. Beide führten dazu, dass Kopien verschwanden. Gelöst durch Aufbau in
`<Profil>/Temp` und ein Ziel außerhalb des Profils.

---

## Offene Fehler

| Punkt | Einordnung |
|---|---|
| Google-Passwortmanager meldet, er funktioniere nicht | vermutlich dieselbe Klasse |
| Web Store zeigt das Chrome-Banner | kosmetisch |

---

## Vertagt

**Umschalter für das Herkunfts-Abzeichen.** Das orange Abzeichen an entpackten
Erweiterungen ist zutreffend, erscheint aber zwangsläufig immer. Ein Umschalter
bräuchte eine Profil-Einstellung im `PrefService`.

**`bootstrap.sh` einmal echt testen.**

**Rückbau nach 150**, falls dieser Zweig gepflegt bleiben soll: Zielverzeichnis
außerhalb des Profils und die Stufenbedingung in `extension_service.cc`.

**Signierung und Veröffentlichung** von Builds — bisher nie besprochen.

---

## Lehre aus 9011

Der Weg dorthin führte über drei Irrtümer: die Annahme, Kiwi habe eine Vorlage,
die Annahme, wir müssten das Menü selbst bauen, und die Annahme, die Bindung ans
Tablet sei logisch statt zufällig.

**Erst prüfen, was der aktuelle Baum kann.** Dann in älteren Fassungen nach
Vorlagen suchen. Wir haben es umgekehrt gemacht und dabei Zeit verloren — bei
9010 mit demselben Muster, nur dort war die Vorlage tatsächlich nötig.
