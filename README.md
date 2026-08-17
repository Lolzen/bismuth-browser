# Bismuth Browser

An Android browser built from Chromium, with **extension support** — including
**Manifest V2**.

A spiritual successor to [Kiwi Browser](https://github.com/kiwibrowser/src.next),
rebuilt from scratch on a current Chromium base.

---

## Status

**Work in progress**, but the core works and the build is used day to day.

| | |
|---|---|
| Chromium base | 149.0.7827.238 |
| Target | Android, `arm64` |
| Extensions | working |
| Manifest V2 | working — uBlock Origin loads, runs and blocks |
| Google account | working |
| Tab switcher | classic single-column card stack, toggleable |
| Startup with uBlock | ~3 s |
| Build type | official (PGO + LTO) |
| Branding | complete |
| Released builds | none yet |

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

Rather than carry Kiwi's 2022 patches forward, Bismuth starts from a current
Chromium and re-implements only what still matters.

Much of it no longer does. Night mode, the bottom address bar and most of the
extension UI that Kiwi built by hand are now part of Chromium itself. Ad
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

Details for each are in `docs/port-notes/`. Scope decisions — what was kept,
deferred and dropped, and why — are in `docs/scope.md`.

Enabling extensions is almost entirely a GN configuration change:
`is_desktop_android = true`. Chromium 149 has an official — if experimental —
path for Android extensions, and Bismuth uses it rather than forcing the desktop
extension system onto Android the way Kiwi did.

Google's own comment calls that branch *"very much in-development, non-stable,
and likely to crash at any given moment."* That is a fair warning and it applies
here too. It is still the better foundation: what breaks there gets fixed
upstream, while a private fork drifts further apart with every milestone.

---

## Manifest V2

Manifest V2 stopped working for users in Chrome 138. Chrome 150 removed the
remaining developer flags, Chrome 151 the feature code.

Chromium 149 still contains everything; MV2 is only switched off. Bismuth
switches it back on with a two-line change.

**That two-line change is specific to 149.** In later versions the stage branch
in `ShouldDisableLegacyExtensions` is gone and the flags no longer matter — from
then on it needs a source patch of the kind
[ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium)
carries. Keeping MV2 alive past 149 is an open-ended maintenance commitment, and
its cost has not been measured yet.

The Chrome Web Store no longer serves MV2 extensions at all, so loading an
unpacked folder is the only route. Milestones 9003 and 9009 exist because of
that.

---

## Signing in

A public Chromium checkout ships only `NullAccountManagerDelegate`, a placeholder
that throws on every write — so signing into a Google account crashed the
browser. Milestone 9010 restores the real delegate from Chromium 132 and adapts
it to the current interface.

The Play Services client library needed for tokens and Gaia IDs turned out to be
present in the checkout already; it only looked absent because nothing used it
anymore.

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
pitfall, why `gclient runhooks` must not be skipped, and why an official build
needs `debuggable_apks = true` during development. Read it first; it will save
you a four-hour failure.

### API keys

No Google API keys are included. Without your own, sync, Safe Browsing and
geolocation will not work — everything else will. Put them in your local
`args.gn`, which is git-ignored for exactly this reason.

---

## Known limitations

- **No Discover feed.** `is_desktop_android` selects the desktop product
  variant, which does not compile the feed. Extensions and the feed are
  currently mutually exclusive; the trade-off will be revisited at the next
  version bump.
- Loading an unpacked extension occasionally fails on the first attempt and
  needs a retry.
- Directories of extensions you remove entirely are not cleaned up.
- The Web Store still shows its "install Chrome" banner. Cosmetic; installation
  works regardless.
- Extensions loaded from a folder carry the standard "unpacked" source badge.
  Since that is the only route for MV2, it is always present.

---

## Not included

Night mode, bottom toolbar and the new tab page were part of Kiwi. Chromium now
provides all three natively.

Kiwi's per-site user-agent spoofing targeted 2022 website behaviour and is not
carried over.

Kiwi's search engine loader fetched its configuration from
`settings.kiwibrowser.com` on every network change. With that project
discontinued, a browser trusting that domain is a hijacking risk. Removed
without replacement.

---

## Credits

A fork of [Kiwi Browser](https://github.com/kiwibrowser/src.next) by
**Arnaud GRANAL** and contributors, itself a fork of
[Chromium](https://www.chromium.org/).

Kiwi solved the hard problem first: getting extensions to run on Android at all,
years before Chromium had any path for it. Bismuth would not exist without that
work, and Kiwi's patch series remains the best available documentation of what
that entails.

---

## License

Chromium is distributed under a
[BSD 3-Clause license](https://chromium.googlesource.com/chromium/src/+/main/LICENSE).
Kiwi Browser's additions carry their own copyright headers, which are preserved.
Patches and tooling here follow the same terms.

---

## Not affiliated

Bismuth Browser is not affiliated with, endorsed by or connected to Google LLC,
the Chromium project, or Kiwi Browser. "Chromium" and "Google Chrome" are
trademarks of Google LLC.
