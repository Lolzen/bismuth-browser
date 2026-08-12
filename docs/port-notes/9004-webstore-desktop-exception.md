# 9004 — Chrome Web Store in Desktop-Fassung

**Status:** fertig
**Patch:** `patches/9004-webstore-desktop-exception.patch`
**Umfang:** 2 Dateien, rund 25 Zeilen

---

## Absicht

Der Chrome Web Store liefert seine Erweiterungsseiten nur an Desktop-Browser aus. Ohne Eingriff muss man vor jeder Installation von Hand auf Desktop-Ansicht umschalten. Ziel ist, dass **genau diese eine Domain** automatisch als Desktop behandelt wird — und sonst nichts.

---

## Umsetzung

### Ausnahme exakt auf den Host

`chrome/browser/ui/android/desktop_site/…/DesktopSiteUtils.java`

```java
WebsitePreferenceBridge.setContentSettingCustomScope(
        profile,
        ContentSettingsType.REQUEST_DESKTOP_SITE,
        "chromewebstore.google.com",
        /* secondaryPattern= */ SITE_WILDCARD,
        ContentSetting.ALLOW);
```

Einmalig, abgesichert durch einen eigenen Merker in den SharedPreferences. Es ist eine reguläre Content-Setting-Ausnahme — sie taucht in den Website-Einstellungen auf und der Nutzer kann sie jederzeit entfernen.

### Automatisches globales Einschalten unterbinden

`chrome/android/java/src/org/chromium/chrome/browser/ui/RootUiCoordinator.java`

Unter `is_desktop_android` hält Chromium das Telefon für ein Tablet und schaltet die Desktopseite global ein. Der entsprechende Aufruf wird deshalb übersprungen:

```java
if (false
        && DesktopSiteUtils.maybeDefaultEnableGlobalSetting(…
```

Bewusst so statt gelöscht, damit beim nächsten Versionssprung sichtbar bleibt, was dort ursprünglich stand.

---

## Zwei Sackgassen

### `setRequestDesktopSiteContentSettingsForUrl` ist zu grob

Die naheliegende Methode wandelt die URL über `toDomainWildcardPattern` in `[*.]google.com` um — also die gesamte Domain samt Suche, Maps und Konto. Bei einem Test stand danach alles in Desktop-Darstellung.

Zusätzlich enthält sie diese Logik:

> *For normal profile, remove domain level setting if it matches the global setting.*

Weil die globale Einstellung unter `is_desktop_android` ohnehin auf ALLOW stand, wurde die Ausnahme als überflüssig **wieder entfernt** — deshalb erschien nie ein Eintrag, obwohl der Merker gesetzt war. Kein Fehler in Chromium, sondern erwartetes Verhalten.

### User-Agent-Spoofing im Netzwerk-Stack

Kiwis Weg: ein hostabhängiger Zweig in `net/url_request/url_request_http_job.cc`, der User-Agent und drei `Sec-CH-UA`-Header überschreibt. In 149 nachgebaut, exakt auf zwei Hosts begrenzt — **ohne Wirkung**, der Store blieb mobil. Zurückgenommen.

Zwei Nebenbefunde daraus: `url.host()` liefert in 149 ein `std::string_view`, nicht `std::string`. Und der Schalter `--enable-discover-feed`, den eine Suchmaschine als Lösung für ein anderes Problem vorschlug, existiert im ganzen Baum nur in `ios/chrome/browser/flags/chrome_switches.cc` — er ist iOS-spezifisch.

---

## Anmerkung zur Voreinstellung

In den Website-Einstellungen gibt es keinen einzelnen Schalter für die Desktopseite, sondern eine **Auswahl zwischen zwei Listen** mit den Ausnahmen darunter. Steht diese Voreinstellung auf Desktop, wirkt sie global — unabhängig von unserem Eingriff. Wer die Desktop-Darstellung überall sieht, sollte zuerst dort nachsehen.

Ob der Eingriff in `RootUiCoordinator` überhaupt nötig ist oder ob die richtige Voreinstellung genügt hätte, ist nicht abschließend geklärt. Er bleibt vorsorglich drin, weil er bei einem frischen Profil verhindert, dass Chromium selbst auf Desktop stellt.
