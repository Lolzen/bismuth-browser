# 9010 — Browser-Anmeldung abschalten

**Status:** fertig, ungetestet auf dem Gerät
**Patch:** `patches/9010-disable-browser-signin.patch`
**Umfang:** 2 Dateien, 2 wirksame Stellen

---

## Absicht

Kein Anmeldeweg des Browsers soll abstürzen oder in Fehler laufen. Google-Seiten
sollen sich verhalten wie in jedem anderen Browser: Anmeldung über das
Webformular.

---

## Warum nicht reparieren

**Sync ist für Chromium-Builds gesperrt, und zwar absichtlich.** Google hat im
Januar 2021 angekündigt, Chrome Sync und weitere private APIs ab dem 15. März
2021 nur noch Google Chrome zur Verfügung zu stellen. Das trifft jeden
Chromium-Abkömmling; Brave und Edge betreiben eigene Sync-Dienste. Daran lässt
sich im Code nichts ändern.

**Ohne Sync bringt die Browser-Anmeldung nichts.** Die frühere 9010 holte den
`SystemAccountManagerDelegate` aus 132 zurück. Anmeldung und Kontenliste liefen,
die Bestätigung aber nie, und die Anmeldeabläufe liefen immer wieder in Fehler.
Sie liegt jetzt unter `patches/archive/9010-account-manager-delegate.patch`, die
Notiz dazu unter `docs/port-notes/old_moot/`.

---

## Das Problem ohne die alte 9010

Der öffentliche Baum liefert nur `NullAccountManagerDelegate`. Er gibt leere
Kontenlisten zurück und wirft bei jedem Schreibzugriff eine
`UnsupportedOperationException`. Dorthin führen zwei Wege:

1. **Browser-Anmeldung** — Anmeldebildschirm beim ersten Start,
   Anmelde-Promos, Eintrag in den Einstellungen. Alle enden bei
   `createAddAccountIntent`.
2. **Mirror** — Chromium auf Android schickt Google-Seiten den Header
   `X-Chrome-Connected`. Google antwortet mit `X-Chrome-Manage-Accounts`, und
   `ProcessMirrorHeader` öffnet daraufhin native Kontenoberfläche, etwa
   `SigninBridge.startAddAccountFlow`. Diese Stelle prüft nicht, ob Anmeldung
   erlaubt ist.

---

## Die zwei Stellen

**`prefs::kSigninAllowed` standardmäßig aus** —
`components/signin/internal/identity_manager/primary_account_manager.cc`:

```cpp
registry->RegisterBooleanPref(prefs::kSigninAllowed, !BUILDFLAG(IS_ANDROID));
```

Das ist Chromiums eigener Schalter. Alles auf dem ersten Weg fragt ihn bereits
ab:

| Stelle | Verhalten bei `false` |
|---|---|
| `SigninManagerImpl.isSigninAllowed()` | liefert `false`, Promos entfallen |
| `FullscreenSigninMediator.isSigninSupported()` | erster Start nur mit „Weiter" |
| `SignInPreference.update()` | Eintrag in den Einstellungen ausgeblendet |
| `SigninBridge.openAccountPickerBottomSheet` | unterdrückt |

**Mirror-Antworten ignorieren** — `chrome/browser/signin/chrome_signin_helper.cc`,
Android-Zweig von `ProcessMirrorHeader`:

```cpp
if (!profile->GetPrefs()->GetBoolean(::prefs::kSigninAllowed)) {
  return;
}
```

Der Header begleitet nur eine gewöhnliche Navigation. Wird er ignoriert, lädt
die Seite trotzdem, und Google bleibt bei seinem Webformular.

---

## Verworfen: Mirror ganz abschalten

`ComputeAccountConsistencyMethod` für Android auf `kDisabled` zu setzen, würde
den Header gar nicht erst senden. Auf Android ist aber überall Mirror
vorausgesetzt, und nicht jede Stelle ließ sich ohne vollen Baum prüfen. Die
Abfrage in `ProcessMirrorHeader` ist schmaler und fängt denselben Fall ab.

---

## Beim Update von einer Fassung mit alter 9010

Ohne Delegat liefert Android keine Konten mehr. Chromium sollte ein Hauptkonto,
das auf dem Gerät fehlt, von selbst entfernen — auf dem Gerät geprüft ist das
nicht. Wer angemeldet war, meldet sich sicherheitshalber vor dem Update ab.
