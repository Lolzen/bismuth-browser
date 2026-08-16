# 9006 — Erweiterungen-Menü

**Status:** fertig
**Patch:** `patches/9006-extensions-menu.patch`
**Umfang:** 3 Dateien, rund 10 Zeilen

---

## Absicht

Der Menüeintrag „Menü *Erweiterungen* öffnen" beendete den Browser beim
Antippen. Nach dem Fix stürzt nichts mehr ab, und das Menü zeigt stattdessen die
Einträge, die tatsächlich funktionieren.

---

## Der Absturz

```
java.lang.NullPointerException: Attempt to write to field 'boolean u34.B'
    on a null object reference
    at ChromeTabbedActivity.onMenuOrKeyboardAction(...)
```

`ChromeTabbedActivity`, Zweig `R.id.extensions_menu_menu_id`:

```java
ExtensionsToolbarCoordinator coordinator =
        getToolbarManager().getExtensionsToolbarCoordinator();
coordinator.showExtensionsMenu();   // coordinator ist null
```

**Warum er null ist:** Der Coordinator wird in `ToolbarManager` nur erzeugt, wenn
`mControlContainer` den ViewStub `extensions_toolbar_container_stub` enthält —
und er bekommt `(ToolbarTablet) mToolbarLayout` übergeben. Der Puzzle-Toolbar ist
also **tablet-spezifisch**. Auf einem Telefon fehlt der Stub, der Block wird nicht
erreicht, der Coordinator bleibt null.

Der Menüeintrag hängt dagegen an `ExtensionUi.isEnabled(profile)` — eine andere
Bedingung. Genau diese Lücke erzeugt den Absturz.

Kein Buildproblem: `gn path` findet einen Weg vom APK zum Extensions-Toolbar-
Target, alles ist einkompiliert. Google hat den Toolbar für Telefone schlicht
noch nicht gebaut.

---

## Umsetzung

**Nullprüfung** in `ChromeTabbedActivity`. Bleibt auch dann sinnvoll, wenn der
Eintrag verschwindet — falls Google die Bedingungen später ändert, stürzt nichts
ab.

**Untermenüs standardmäßig an.** In `chrome_feature_list.cc`:

```cpp
BASE_FEATURE(kSubmenusInAppMenu, base::FEATURE_ENABLED_BY_DEFAULT);
```

Damit erscheint statt des einzelnen, wirkungslosen Eintrags ein Untermenü mit
„Erweiterungen verwalten" und „Chrome Web Store besuchen" — beide funktionieren.
Das Flag bleibt in `chrome://flags` umschaltbar.

**Der wirkungslose Eintrag** wird in `TabbedAppMenuPropertiesDelegate` aus dem
Untermenü genommen.

---

## Anmerkungen

Das Feature war die ganze Zeit als `submenus-in-app-menu` in `chrome://flags`
verfügbar. Zum Ausprobieren hätte kein Neubau genötigt — nur der Umschalter dort.
Der Umweg über die Kommandozeilendatei scheiterte, weil ein offizieller Build sie
ignoriert, solange `debuggable_apks` nicht gesetzt ist.

Der Umschalter für den Tab-Switcher wurde in derselben Runde von *Darstellung*
nach *Tabs* verlegt und liegt jetzt in `tabs_settings.xml` und
`TabsSettings.java` — beides Teil von 9002.

---

## Lehre

Das Muster wiederholt sich: Ein Feature erklärt sich für verfügbar, während der
Teil, der es umsetzt, unter anderen Bedingungen kompiliert oder erzeugt wird. Bei
`browserAction` war es das fehlende Schema, hier die tablet-gebundene Erzeugung.
Beim Versionssprung ist das die Klasse von Fehlern, mit der zu rechnen ist.
