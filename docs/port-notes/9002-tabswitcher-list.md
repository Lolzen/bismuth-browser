# 9002 — Tab-Switcher LIST-Modus

**Status:** TBD — vollständig recherchiert, noch nicht umgesetzt
**Referenzmaterial:** `reports/list-reference-138.0.7204.310/`
**Basis:** Chromium 149.0.7827.238

---

## Absicht

Der Tab-Switcher soll sich auf die **vertikale Listenansicht** umstellen lassen. Das ist ein Kernfeature, kein Komfort — es ist der Grund, warum `tab_ui` von DROP auf KEEP korrigiert wurde.

## Kiwis Umsetzung (Chromium 105)

Umfang: 19 Dateien, 402 Insertions, 21 Deletions. Davon sind 226 Zeilen Kiwis Eigencode:

- `chrome/android/java/src/org/chromium/chrome/browser/settings/TabSwitcherSettings.java` (62 Zeilen)
- `.../settings/RadioButtonGroupTabSwitcherPreference.java` (164 Zeilen)
- `res/xml/tabswitcher_preferences.xml`
- `res/layout/radio_button_group_tabswitcher_preference.xml`

Der Mechanismus ist eine SharedPreference `active_tabswitcher` mit den Werten `default`, `list`, `classic`, `grid`. In `TabSwitcherMediator` steht dazu:

```java
if (…getString("active_tabswitcher", "default").equals("list"))
  mode = TabListMode.LIST;
if (…equals("classic") || …equals("grid"))
  mode = TabListMode.GRID;
```

Plus im Scroll-Offset: bei `classic` wird der Offset auf 0 gesetzt.

**Wichtig:** Kiwi belebt keine gelöschte Layout-Engine wieder. `TabListMode.LIST` und `GRID` sind Chromiums eigene Enum-Werte. `classic` ist schlicht GRID ohne Voranscrollen.

## Lage in 149

Von den 19 Dateien existieren 9 weiter, zwei der „fehlenden" sind Kiwis eigene. Real fehlen 8 Chromium-Dateien.

Chromium ist auf ein **Pane-Modell** umgestellt: `HubLayout` als Container, darin `TabSwitcherPane` und `IncognitoTabSwitcherPane`, erzeugt von `TabSwitcherPaneCoordinatorFactory`. `TabSwitcherMediator`, `TabSwitcherCoordinator` und `TabSwitcherLayout` gibt es nicht mehr.

**Und `TabListMode.LIST` wurde entfernt.** In 149 lautet das IntDef:

```java
@IntDef({TabListMode.GRID, TabListMode.STRIP, TabListMode.NUM_ENTRIES})
```

Keine einzige `LIST`-Verwendung mehr. Der `LinearLayoutManager` in `TabListCoordinator` ist `HORIZONTAL`, also STRIP — kein vertikaler Listenmodus.

### Referenzversion

| | |
|---|---|
| Letzte Version mit LIST | **138.0.7204.310** |
| Entfernt ab | 139.0.7258.400 |
| Abstand zum Ziel | 11 Milestones |

Der zu portierende Code stammt damit aus 2025/2026, nicht aus 2022. Das ist ein völlig anderes Kaliber als der Rest des Projekts.

## Umsetzungsplan

| Datei | Status in 149 | Aufgabe |
|---|---|---|
| `TabSwitcherPaneCoordinatorFactory.java` | vorhanden | **Der Hook.** Zeile ~153 setzt hart `mMode = TabListCoordinator.TabListMode.GRID;`. In 138 stand dort ein Ternär mit LIST (Zeile 139). Verzweigung wiederherstellen, Bedingung = SharedPreference |
| `TabListCoordinator.java` | vorhanden | `LIST` ins `@IntDef` (149er Zeile 121); vertikaler `LinearLayoutManager`-Zweig; Drag-and-Drop-Freigabe. 138er Referenzstellen: 89, 206, 284, 375–381, 532 |
| `TabListContainerViewBinder.java` | vorhanden | modusabhängiges Binding, 138er Zeile 155 |
| `TabListMediator.java` | vorhanden | gruppierte Tabs im Listenmodus, 138er Zeilen 2328/2331 |
| `TabListViewBinder.java` | **fehlt** | 353 Zeilen aus 138 zurückbringen — oder in eine bestehende STRIP-Binder-Klasse integrieren |
| `tab_list_card_item.xml` | **fehlt** | 25 Zeilen Layout |
| `TabProperties.java` | vorhanden | keine Anpassung nötig |

Reihenfolge: erst Kiwis Settings-Klassen einspielen, dann Renderer und Layout zurückbringen, dann die vier Verdrahtungsstellen, zuletzt der Hook.

### Geprüfte Voraussetzungen

- Alle 14 vom 138er Binder benötigten `PropertyKey` existieren in 149 weiter. Einziger entfernter Key ist `CARD_ANIMATION_STATUS`, der nicht gebraucht wird. `TabProperties` wuchs von 226 auf 292 Zeilen, rein additiv.
- `TabActionState` ist identisch: `UNSET=0`, `SELECTABLE=1`, `CLOSABLE=2`.
- Es gibt **keinen eigenen `UiType` für LIST**. Der Listenmodus nutzt `UiType.TAB` mit anderem Layout — kein neuer Zelltyp nötig.

### Fallstrick

`UiType` wurde umnummeriert:

| | 138 | 149 |
|---|---|---|
| `TAB_GROUP` | 5 | **2** |
| `MESSAGE`, `LARGE_MESSAGE`, `CUSTOM_MESSAGE` | 2, 3, 4 | ersetzt durch sechs spezifische Message-Typen |

Konstanten benutzen, niemals Zahlen. Ein numerischer Vergleich im 138er Code würde still falsch werden.

## Aufwandsschätzung

**150–250 Zeilen über fünf bis sechs Dateien.**

## Offene Frage

Gibt es in 149 einen Binder für STRIP-Einträge? `tab_strip_item.xml` und `pinned_tab_strip_item.xml` existieren, die Bindung muss also irgendwo liegen. Falls ja, ergänzt man dort einen Zweig statt eine Klasse neu anzulegen — das würde den Aufwand deutlich senken.

Zu prüfen mit `scripts/find_strip_binder.sh`.

## Was gedroppt wird

Innerhalb von `tab_ui` ersatzlos:

- `StartSurfaceTabSwitcherActionMenuCoordinator` — Start Surface hat Chromium komplett entfernt, `TabSwitcherActionMenuCoordinator` existiert weiter und reicht
- `NewTabTileMediator` — die Kachel gibt es nicht mehr
- `PseudoTab` — war eine temporäre Abstraktion, Kiwis Änderung dort ist eine einzige Zeile

`TabSwitcherDrawable` ist kein Verlust, sondern umgezogen nach `chrome/browser/ui/android/bars_common/`. Reiner Pfad-Remap.
