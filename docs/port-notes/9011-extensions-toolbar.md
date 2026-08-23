# 9011 — Erweiterungs-Symbolleiste auf dem Telefon

**Status:** fertig
**Patch:** `patches/9011-extensions-toolbar.patch`
**Umfang:** 2 Dateien, 2 wirksame Zeilen

---

## Absicht

Zugriff auf die Erweiterungen von der Adressleiste aus — Puzzle-Knopf, Menü mit
allen Erweiterungen, deren Popups, Seitenzugriff und Anheften.

---

## Was man bekommt

Chromium 151 bringt die **komplette Oberfläche** dafür bereits mit. Nach diesem
Patch erscheint auf dem Telefon:

- ein Puzzle-Knopf in der Adressleiste
- ein Menü mit allen Erweiterungen, jeweils mit Symbol und Zählerplakette
- je Erweiterung ein Schalter und die Angabe des Seitenzugriffs
  („Immer auf allen Websites", „Immer auf dieser Website")
- ein Schalter „Erweiterungen auf dieser Website zulassen"
- Anheften an die Symbolleiste
- „Mehr Erweiterungen entdecken" und „Erweiterungen verwalten"

Nichts davon ist selbst gebaut.

---

## Die zwei Zeilen

**Ein `ViewStub` in `toolbar_phone.xml`**, im `LinearLayout` mit der Kennung
`toolbar_buttons`, vor dem Tab-Umschalter:

```xml
<ViewStub
    android:id="@+id/extensions_toolbar_container_stub"
    android:inflatedId="@+id/extensions_toolbar_container"
    android:layout_width="wrap_content"
    android:layout_height="match_parent"
    android:layout_gravity="top"/>
```

**Eine überflüssige Typumwandlung in `ToolbarManager.java`**, im Aufruf von
`ExtensionsToolbarCoordinator.maybeCreate`:

```java
- (ToolbarTablet) mToolbarLayout,
+ mToolbarLayout,
```

Das war alles.

---

## Warum das reicht

`ToolbarManager` prüft nicht, ob ein Tablet vorliegt. Es sucht schlicht den
ViewStub in der Steuerleiste:

```java
ViewStub extensionsToolbarStub =
        mControlContainer.findViewById(R.id.extensions_toolbar_container_stub);
if (extensionsToolbarStub != null) { … }
```

Der Stub existierte bis dahin nur in `toolbar_tablet.xml`. Die Bindung ans
Tablet war also nicht logisch, sondern rein durch das Layout gegeben.

Die Typumwandlung war ebenfalls Beiwerk. Die Signatur verlangt

```java
ViewGroup rootView,
```

und `ExtensionsToolbarCoordinatorImpl` erwähnt `ToolbarTablet` an keiner Stelle.
Der Wert wird nur durchgereicht. `ToolbarLayout` erbt von `FrameLayout` und ist
damit eine `ViewGroup` — die Umwandlung konnte ersatzlos entfallen.

---

## Was Chromium bereits mitbringt

Unter `chrome/browser/ui/android/toolbar/.../toolbar/extensions/` liegen unter
anderem:

```
ExtensionsToolbarCoordinator      Puzzle-Knopf und Leiste
ExtensionsMenuCoordinator         das Menü
ExtensionActionPopup              die Popups
ExtensionActionIconUtil           Symbole samt Plakette
ExtensionActionDragHelper         Anheften und Umsortieren
```

Und die Brücke zur nativen Seite unter
`chrome/browser/ui/android/extensions/`:

```java
getAllActionIds() / getPinnedActionIds()   die Liste
getAction(id, webContents)                 Name und Titel
getIcon(...)                               Symbol als Bitmap
executeUserAction(id, source)              ausloesen
triggerPopup(id, nativeHostPtr)            Popup oeffnen
```

Wer eine eigene Oberfläche bauen will, findet hier alles Nötige. Wir brauchten
sie nicht.

---

## Der Umweg, der nicht nötig war

Der ursprüngliche Plan war, Kiwis Lösung nachzubauen: Erweiterungen als Einträge
im Hauptmenü. Kiwi hat dafür 2021 eine eigene Brücke `AppMenuBridge` geschrieben,
die eine serialisierte Zeichenkette liefert — Einträge durch `\u001f` getrennt,
Felder durch `\u001e`, mit Name, Kennung, Popup-URL und base64-PNG. Die Kennung
wurde im Feld `TitleCondensed` als `"Extension: <id>: <url>"` mitgeschmuggelt und
beim Antippen wieder herausgeparst.

Das war 2021 eine kluge Lösung, weil Chromium nichts dergleichen hatte. Heute
wäre es Eigenbau gegen eine Schnittstelle, die es fertig gibt.

**Lehre:** Erst prüfen, was der aktuelle Baum kann, dann in älteren Fassungen
nach Vorlagen suchen. Wir haben es umgekehrt gemacht und dabei Zeit verloren.

---

## Beim Versionssprung

Der Patch ist so klein, dass er kaum brechen kann. Zwei Dinge sind zu prüfen:

Ob der ViewStub im Telefon-Layout noch an derselben Stelle passt — die
Knopfreihe ändert sich gelegentlich.

Ob die Umwandlung in `ToolbarManager` wieder auftaucht. Sollte Google die
Symbolleiste von sich aus für Telefone öffnen, wird dieser Patch überflüssig und
kann ersatzlos entfallen.
