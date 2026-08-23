# Bismuth Browser

An Android browser built from Chromium, with **extension support** — including
**Manifest V2**.

A **Chromium fork**, built from a current Chromium base. Kiwi Browser was the
inspiration and the reference for what such a browser needs to do; none of its
code is used here.

---

## Status

**Work in progress**, but the core works and the build is used day to day.

| | |
|---|---|
| Chromium base | 151.0.7922.176 |
| Target | Android, `arm64` |
| Extensions | working, with the full toolbar UI |
| Manifest V2 | working — uBlock Origin loads, runs and blocks |
| Google account | sign-in works, sync does not |
| Tab switcher | classic single-column card stack, toggleable |
| Startup with uBlock | ~3 s |
| Build type | official (PGO + LTO) |
| Branding | complete |
| Released builds | none yet |

Earlier bases are kept as branches: `149.0.7827.238`, `150.0.7871.249`.

---

## Why the name

Bismuth was long held to be the heaviest stable element. It is in fact
radioactive — with a half-life a billion times the age of the universe.
Officially decaying, effectively permanent.

That seemed a reasonable name for a project whose purpose is keeping Manifest V2
alive past its announced end. The crystal's stepped, iridescent hopper structure
is where the logo comes from.

---

## Why this exists

Kiwi Browser was the practical way to run browser extensions on Android. Its
last real Chromium base was **105.0.5195.24**, frozen in August 2022; later
releases bumped the version string but not the engine. The project has since
been discontinued.

Bismuth does not continue that codebase. It starts from a current Chromium and
implements what is actually still missing. Kiwi's patch series was read
carefully — as documentation of which problems arise and where — but every patch
here was written against today's tree.

Most of what Kiwi added no longer needs adding. Night mode, the bottom address
bar and most of the extension UI it built by hand are part of Chromium now. Ad
blocking, popup blocking and user scripts are covered by extensions. What
remains is the part nobody else provides: **extensions on Android, with
Manifest V2 support.**

---

## What is patched

| Milestone | What it does |
|---|---|
| **9001** | Enables the extension system and keeps Manifest V2 available |
| **9002** | Classic tab switcher — one overlapping column of cards, with a toggle |
| **9003** | Copies unpacked extensions into app storage instead of running them over SAF |
| **9004** | Serves the Chrome Web Store its desktop pages, for that host only |
| **9005** | Branding — name, icons, package name, internal strings |
| **9006** | Fixes the crashing extensions menu entry, enables app-menu submenus |
| **9007** | Removes the Manifest V2 deprecation warning and notice |
| **9009** | Progress dialog with a real percentage while an extension is copied |
| **9010** | Restores the account manager delegate, so signing in works |
| **9011** | Brings Chromium's extensions toolbar to phones |

Details for each are in `docs/port-notes/`, including one note per version bump.
Scope decisions are in `docs/scope.md`.

Enabling extensions is almost entirely a GN configuration change:
`is_desktop_android = true`. Chromium has an official — if experimental — path
for Android extensions, and Bismuth uses it rather than forcing the desktop
extension system onto Android the way Kiwi did.

Google's own comment calls that branch *"very much in-development, non-stable,
and likely to crash at any given moment."* That is a fair warning and it applies
here too. It is still the better foundation: what breaks there gets fixed
upstream, while a private fork drifts further apart with every milestone.

Milestone 9011 is the clearest illustration. Chromium already contains the whole
extensions toolbar — puzzle button, menu, popups, per-site access, pinning. It
was simply never wired up for phone-sized layouts. Two lines connect it.

---

## Manifest V2

Manifest V2 stopped working for users in Chrome 138. Since 150 the switch-off is
hardcoded — the experiment stage is no longer consulted at all.

Chromium keeps one lever, used by its own tests, that allows MV2 extensions
regardless. Bismuth leaves that lever on. **That is a single line**, and it has
survived two version bumps; only the file it lives in changed.

Flipping feature flags does not work and fails silently: Chromium expires flags
after a milestone and force-resets them, so a flag-based patch applies cleanly,
builds, and does nothing.

The Chrome Web Store no longer serves MV2 extensions at all, so loading an
unpacked folder is the only route. Milestones 9003 and 9009 exist because of
that.

---

## Signing in

A public Chromium checkout ships only `NullAccountManagerDelegate`, a placeholder
that throws on every write — so signing into a Google account crashed the
browser. Milestone 9010 restores the real delegate from Chromium 132 and adapts
it to the current interface.

Signing in and listing device accounts works. **Sync does not** — the account
confirmation step never completes. The cause is not established.

---

## What this repository contains

**No Chromium source code.** Only patches, configuration and tooling.

```
CHROMIUM_TARGET        the exact Chromium tag this builds against
args.gn.template       GN configuration, API keys redacted
bootstrap.sh           fetches Chromium, applies patches
branding/              icon sources
patches/               the patch series, applied in `series` order
docs/                  scope, build notes, one port note per milestone
scripts/               tooling, grouped by milestone
```

---

## Building

**You will need:** Linux, roughly 500 GB free on a case-sensitive filesystem,
16 GB RAM (32 recommended), and several hours. Chromium can only be built for
Android from Linux.

```
git clone https://github.com/Lolzen/bismuth-browser.git
cd bismuth-browser
./bootstrap.sh ~/bismuth-build
```

Then edit `out/Default/args.gn` and:

```
cd ~/bismuth-build/chromium/src
gn gen out/Default
autoninja -C out/Default chrome_public_apk
```

`docs/build-notes.md` covers what no official guide mentions — pinning
`protobuf` to 3.20.3, `dcheck_always_on`, non-Debian hosts, the `gclient` tag
pitfall, the V8 PGO profiles that do not come along on a version bump, and why an
official build needs `debuggable_apks = true` during development. Read it first;
it will save you a four-hour failure.

### API keys

No Google API keys are included. Without your own, Safe Browsing and geolocation
will not work — everything else will. Put them in your local `args.gn`, which is
git-ignored for exactly this reason.

---

## Known limitations

- **Sync does not work.** Signing in does; the confirmation step does not
  complete.
- **No Discover feed content.** The feed area appears on the new tab page but
  never loads. Its renderer is Google's closed **XSurface** library, which ships
  as an on-demand module in official Chrome and has never been part of the
  public tree. No Chromium derivative can show the feed.
- **The Web Store shows an "install Chrome" banner.** Not a user-agent problem —
  in desktop mode the browser reports Chrome 151 on Chrome OS, and forcing
  Linux instead changes nothing. Whatever the store recognises, chasing it would
  mean impersonating another platform more aggressively than Chromium already
  does. Installation works regardless.
- Extensions loaded from a folder carry the standard "unpacked" source badge.
  Since that is the only route for MV2, it is always present.

---

## Not included

Night mode, bottom toolbar and the new tab page were features Kiwi added.
Chromium now provides all three natively.

Kiwi's per-site user-agent spoofing targeted 2022 website behaviour and is not
reproduced here.

Kiwi's search engine loader fetched its configuration from
`settings.kiwibrowser.com` on every network change. With that project
discontinued, a browser trusting that domain is a hijacking risk. Not
reproduced, and no replacement.

---

## Credits

Built from [Chromium](https://www.chromium.org/).

[Kiwi Browser](https://github.com/kiwibrowser/src.next) by **Arnaud GRANAL** and
contributors solved the hard problem first: getting extensions to run on Android
at all, years before Chromium had any path for it. Its patch series remains the
best available documentation of what that entails, and reading it shaped what
this project set out to do. No Kiwi code is used here.

---

## License

Chromium is distributed under a
[BSD 3-Clause license](https://chromium.googlesource.com/chromium/src/+/main/LICENSE).
Patches and tooling in this repository follow the same terms.

---

## Not affiliated

Bismuth Browser is not affiliated with, endorsed by or connected to Google LLC,
the Chromium project, or Kiwi Browser. "Chromium" and "Google Chrome" are
trademarks of Google LLC.
