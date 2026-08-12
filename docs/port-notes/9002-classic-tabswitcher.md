# 9002 — Classic-Tab-Switcher

**Status:** fertig
**Patch:** `patches/9002-classic-tabswitcher.patch`
**Umfang:** 4 Dateien, rund 60 Zeilen

---

## Absicht

Tabs sollen als **einspaltige, überlappende Karten mit Seitenvorschau** erscheinen — die Darstellung, die Kiwi unter dem Namen „classic" anbot. Dazu ein Schalter in den Einstellungen.

---

## Der Umweg, der sich sparen ließ

Zuerst wurde der **LIST-Modus** portiert — Chromiums vertikale Listenansicht, die nach 138.0.7204.310 entfernt wurde. Dafür kamen `TabListView.java` (123 Zeilen), `TabListViewBinder.java` (353 Zeilen), `tab_list_card_item.xml`, zwei Drawables und fünf Dimensionswerte aus 138 zurück, dazu Einträge in `tab_management_java_sources.gni` und `tab_ui/BUILD.gn`.

Der Code kompilierte, aber der Tab-Switcher stürzte **siebenmal in Folge** ab. Ursache war jedes Mal dieselbe Klasse von Annahme: 149 setzt voraus, dass GRID der einzige Rastermodus ist.

| Absturz | Stelle |
|---|---|
| `ClassCastException` | `TabListCoordinator.updateGridCardLayout` |
| `ClassCastException` | `PinnedTabStripCoordinator.createMediator` |
| `AssertionError` | `TabListContainerViewBinder` Modus-Assert |
| `AssertionError` | zwei `assumeNonNull` auf den LayoutManager |
| `ClassCastException` | `TabListRecyclerView`, zwei Barrierefreiheits-Methoden |

**Dann stellte sich heraus, dass der Listenmodus gar nicht gemeint war.** Ein Screenshot aus Kiwi zeigte Karten mit Vorschaubild — also „classic", nicht LIST. Die gesamte Portierung war überflüssig.

> **Lehre:** Erst klären, wie es aussehen soll, dann was im Code steht. Ein Screenshot am Anfang hätte den Umweg erspart.

Die verworfene Arbeit liegt als `patches/9002-tabswitcher-list-archiv.patch` und in `scripts/wip/`.

---

## Was tatsächlich nötig war

### Einspaltig — `TabListMediator.java`

```java
final int newSpanCount =
        ContextUtils.getAppSharedPreferences()
                        .getBoolean("classic_tab_switcher_v2", true)
                ? 1
                : getSpanCount(screenWidthDp);
```

In `updateSpanCount`, weil dieselbe Methode auch bei Orientierungswechseln durchläuft. Im Konstruktor allein zu ändern hätte beim Drehen wieder zwei Spalten ergeben.

### Überlappung — `TabListCoordinator.java`

Eine `RecyclerView.ItemDecoration` mit negativem oberen Abstand:

```java
outRect.top = -(int) Math.ceil(75 * density);
```

Im Querformat und beim ersten Element auf 0, sonst stapeln sich die Karten am oberen Rand. Angehängt direkt nach `setLayoutManager`, ebenfalls hinter der Preference-Abfrage.

Der Wert 75dp stammt aus Kiwi und sitzt in 149 unverändert gut.

### Schalter — `appearance_preferences.xml` und `AppearanceSettingsFragment.java`

Ein `ChromeSwitchPreference` mit `android:persistent="false"`, dessen Zustand das Fragment selbst aus `ContextUtils.getAppSharedPreferences()` liest und dorthin zurückschreibt.

---

## Zwei Fallstricke beim Schalter

**Chromiums Preference-Unterbau schreibt nicht zuverlässig.** Mit `android:defaultValue` und regulärer Persistenz landete `false` in den Einstellungen, `true` aber nie. Die Ursache blieb ungeklärt; die Lösung ist, die Persistenz selbst zu übernehmen.

**Ein Wert, der nur in eine Richtung gesetzt werden kann, sperrt aus.** Nach dem Abschalten stand `false` fest in den Preferences und ließ sich nicht mehr überschreiben — die classic-Darstellung war dauerhaft weg. Behoben durch einen neuen Schlüsselnamen (`classic_tab_switcher_v2`), der den vergifteten Wert umgeht.

> **Lehre:** Einen Schalter erst einbauen, wenn beide Richtungen nachweislich schreiben.

---

## Was die Fehlersuche entschieden hat

Drei Log-Zeilen im Fragment — `findPreference`, Anfangswert, Listener — haben die Frage in einem Durchlauf beantwortet, nachdem vier Hypothesen daneben lagen. Dasselbe Muster wie bei 9001.

---

## Offen

- Der Umschalter wirkt erst beim Neuaufbau des Switchers, nicht sofort. Für eine Einstellung, die man einmal setzt, verschmerzbar.
- Titel und Beschreibung stehen als Literale im XML statt als Strings in der `.grd`. Möglich, weil `disable_android_lint = true` gesetzt ist; beim Branding nachzuziehen.
