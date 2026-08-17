# 9010 — Kontenverwaltung wiederherstellen

**Status:** funktioniert; Googles Kontoprüfung stand beim Schreiben noch aus
**Patch:** `patches/9010-account-manager-delegate.patch`
**Umfang:** 2 Dateien, rund 170 Zeilen

---

## Absicht

Die Anmeldung an einem Google-Konto beendete den Browser. Nach diesem Patch
lässt sich ein Konto auswählen und der Browser übernimmt es.

---

## Der Absturz

```
java.lang.UnsupportedOperationException:
NullAccountManagerDelegate does not implement createAddAccountIntent
```

Chromium 149 liefert für Android nur noch `NullAccountManagerDelegate` — einen
Platzhalter, der leere Listen zurückgibt und bei jedem Schreibvorgang eine
Ausnahme wirft. Der echte Kontenverwalter kommt in Googles Builds aus deren
internem Zweig.

`AccountManagerFacadeProvider` wählt ihn über denselben Service-Loader wie den
Extensions-Toolbar:

```java
AccountManagerDelegate delegate =
        ServiceLoaderUtil.maybeCreate(AccountManagerDelegate.class);
if (delegate == null) {
    delegate = new NullAccountManagerDelegate();
}
```

Ist nichts per `@ServiceImpl` registriert, greift der Platzhalter. Im ganzen Baum
gibt es keine Registrierung und außer dem Platzhalter nur eine Testattrappe.

---

## Umsetzung

`SystemAccountManagerDelegate.java` existierte bis Chromium 132 und wurde danach
aus dem öffentlichen Baum entfernt. Die 132er Fassung lässt sich mit
`git show HEAD:<pfad>` aus einem Referenz-Repository holen und anpassen.

Anzupassen waren:

| 132 | 149 |
|---|---|
| `getAuthToken` | `getAccessToken` |
| `invalidateAuthToken` | `invalidateAccessToken` |
| `createAddAccountIntent(Callback)` | zusätzlicher Parameter `prefilledEmail` |
| `getAccountGaiaId` → `String` | → `GaiaId` |
| `hasFeature` | entfallen |
| `AuthException.NONTRANSIENT` | `AuthException(boolean isTransient, …)` |
| — | `@NullMarked`, `@ServiceImpl(AccountManagerDelegate.class)` |

Dazu der Eintrag in `components/signin/public/android/BUILD.gn` neben
`NullAccountManagerDelegate.java`. Die Berechtigung `GET_ACCOUNTS` steht bereits
im Manifest.

Entfernt wurden gegenüber der Vorlage die Histogramme, die Berechtigungsprüfung
über `ApiCompatibilityUtils` und der Verfügbarkeitstest über `ExternalAuthUtils`
— sie bringen zusätzliche Abhängigkeiten und tragen zur Funktion nichts bei.

---

## Der entscheidende Fund

Die 132er Vorlage benutzt `GoogleAuthUtil` aus der Play-Dienste-Clientbibliothek
für Token und Gaia-Kennung. Eine Suche nach `GoogleAuthUtil` im 149er Baum
liefert nur einen Kommentar — daraus lässt sich fälschlich schließen, die
Bibliothek fehle.

Sie ist vorhanden. `google_play_services_auth_base_java` steht sogar **bereits
als Abhängigkeit** in genau dem Buildskript, in das die Klasse eingetragen wird:

```
components/signin/public/android/BUILD.gn:6
components/signin/public/android/BUILD.gn:198
```

Sie wirkte nur ungenutzt, weil kein Java-Code sie mehr aufruft. Damit lassen sich
Token über `getTokenWithNotification` und Gaia-Kennungen über `getAccountId`
beziehen — also genau die beiden Dinge, die ohne sie nicht zu ersetzen wären.

---

## Verworfen: der Weg über DICE

Der naheliegende Gedanke war, statt des Kontenverwalters den webbasierten
Anmeldeweg des Desktops einzuschalten:

```gn
enable_dice_support = is_linux || is_mac || is_win || is_fuchsia
```

Das trägt nicht. `enable_dice_support` zieht die Desktop-Profilverwaltung mit
herein, und die hängt an der Views-Oberfläche:

```
chrome/browser/ui/views/frame/BUILD.gn:5: assert(!is_android)
```

Fünf Buildskripte ließen sich absichern, danach blieb `batch_upload` mit sechs
verstreuten Abnehmern in `chrome/test/BUILD.gn` übrig. Eine Assertion am Kopf
einer Datei feuert bereits beim Einlesen — es genügt also, dass irgendein
Testziel das Ziel referenziert, auch wenn es nie gebaut wird.

Selbst bei Erfolg wäre offen geblieben, ob die Anmeldung dann funktioniert: Die
Android-Pfade holen ihre Konten weiterhin über `AccountManagerFacade`.

Die Arbeit war trotzdem nicht umsonst — sie hat den Blick auf den fehlenden
Delegaten gelenkt, und der war die eigentliche Lücke.

---

## Beobachtungen beim Testen

**`Log.i` wird im offiziellen Bau wegoptimiert.** Eine Messung schien mehrfach
zu belegen, dass eine Methode nie aufgerufen wird — tatsächlich war nur die
Ausgabe unsichtbar. Mit `Log.e` erschien sie sofort. Das hat mehrere Runden
gekostet und gehört zu den teuersten Irrtümern dieses Projekts.

**Das Flag `MigrateAccountManagerDelegate` wirkt nicht so, wie es aussieht.** In
beiden Stellungen gab es einmal Erfolg und einmal Misserfolg; entscheidend war
eher ein Neustart des Browsers. Der Standardwert bleibt deshalb wie im Original.
Wer hier eine Abweichung einbaut, dokumentiert eine Scheinkorrelation.

**Die Kontenauswahl über `newChooseAccountIntent`** wurde zwischenzeitlich
eingebaut, weil `addAccount` bei einem bereits vorhandenen Konto abbricht. Sie
ist im Endstand nicht enthalten: Sobald der Delegat Konten liefert, bietet der
Browser sie von selbst an, und `addAccount` bleibt für das an, wofür es gedacht
ist — ein wirklich neues Konto.

---

## Offen

- Googles Kontoprüfung lief beim Schreiben dieser Notiz noch. Ob Sync dauerhaft
  durchläuft, ist damit noch nicht bestätigt.
- `hasCapability` liefert `EXCEPTION`, wie schon in der 132er Vorlage.
- Der Weg „Konto hinzufügen" verlangt die volle Identitätsbestätigung und ist für
  ein bereits vorhandenes Konto der falsche. Ihn auszublenden wäre Kosmetik.
