# \<PROJECTNAME\>

> **Name still to be chosen.** Replace every `<PROJECTNAME>` and `<projectname>`
> placeholder before publishing. Nothing resembling "Kiwi" — see *Naming* below.

An Android browser built from Chromium, with **extension support** — including
**Manifest V2**.

A spiritual successor to [Kiwi Browser](https://github.com/kiwibrowser/src.next),
rebuilt from scratch on a current Chromium base.

---

## Status

**Work in progress. Not usable yet.** Nothing here is released, and nothing is
guaranteed to build on your machine.

| | |
|---|---|
| Chromium base | 149.0.7827.238 |
| Target | Android, `arm64` |
| Vanilla reference build | works, verified on device |
| Extensions enabled | configuration complete, build unverified |
| Manifest V2 | patch written, **not yet functionally verified** |
| Everything else | not started |

---

## Why this exists

Kiwi Browser was the practical way to run browser extensions on Android. Its
last real Chromium base was **105.0.5195.24**, frozen in August 2022. Later
releases bumped the version string but not the engine. The project has since
been discontinued.

Four years of Chromium development have gone by. Rather than carry Kiwi's 2022
patches forward, this project starts from a current Chromium and re-implements
what still matters.

A lot turns out not to matter anymore. Night mode, the bottom address bar and
much of the extension UI that Kiwi had to build by hand are now part of Chromium
itself. What Kiwi filled in as gaps, Google has largely closed.

What remains is the part nobody else provides: **extensions on Android, with
Manifest V2 support.**

---

## Approach

Chromium 149 has an official — if experimental — path for Android extensions,
gated behind `is_desktop_android`. This project uses that path rather than
forcing the desktop extension system onto Android the way Kiwi did.

The practical consequence is a very small footprint:

- Enabling extensions is **entirely a GN configuration change**
- The only source change is **two lines** in `extensions/common/extension_features.cc`
  to keep Manifest V2 available

Google's own comment calls the desktop-android branch *"very much
in-development, non-stable, and likely to crash at any given moment."* That is a
fair warning and it applies here too. It is still the better foundation: what
breaks there gets fixed upstream, while a private fork of the desktop extension
system drifts further apart with every milestone.

### Manifest V2

Manifest V2 stopped working for users in Chrome 138. Chrome 150 removed the
remaining developer flags, and Chrome 151 removed the feature code.

Chromium 149 still contains everything; MV2 is only switched off. This project
switches it back on.

Keeping MV2 alive past 149 will require reverting Google's removals on every
version bump. That is a deliberate, open-ended maintenance commitment, and the
cost of it has not been measured yet.

---

## What this repository contains

**No Chromium source code.** Only patches, configuration and tooling. A full
build tree is reconstructed on demand.

```
CHROMIUM_TARGET        the exact Chromium tag this builds against
args.gn.template       GN build configuration, API keys redacted
bootstrap.sh           fetches Chromium, applies patches
patches/               the patch series, applied in `series` order
docs/                  build notes and one port note per feature
scripts/               analysis and maintenance tooling
```

---

## Building

**You will need:** Linux, roughly 500 GB of free disk space on a
case-sensitive filesystem, 16 GB RAM (32 GB recommended), and several hours.
Chromium can only be built for Android from Linux.

```
git clone https://github.com/<user>/<projectname>.git
cd <projectname>
./bootstrap.sh ~/<projectname>-build
```

Then edit `args.gn` (see `args.gn.template`), and:

```
cd ~/<projectname>-build/chromium/src
gn gen out/Build
autoninja -C out/Build chrome_public_apk
out/Build/bin/chrome_public_apk install
```

`docs/build-notes.md` covers the parts no official guide mentions — pinning
`protobuf` to 3.20.3, `dcheck_always_on`, non-Debian hosts, and the `gclient`
tag pitfall. Read it before your first build; it will save you a four-hour
failure.

### API keys

No Google API keys are included. Without your own, sync, Safe Browsing,
geolocation and the Discover feed will not work — everything else will. Get
them from the Google Cloud Console and put them in your local `args.gn`, which
is git-ignored for exactly this reason.

---

## Features

### Planned

- Extensions on Android, Manifest V2 and V3
- Tab switcher list view (removed from Chromium after 138)
- User scripts

### Explicitly not included

Night mode, bottom toolbar and the new tab page were part of Kiwi. Chromium now
provides all three natively, so they are not reimplemented here.

Kiwi's per-site user-agent spoofing targeted website behaviour from 2022 and is
not carried over.

Kiwi's search engine loader fetched its configuration from
`settings.kiwibrowser.com` on every network change. With that project
discontinued, a browser trusting that domain is a hijacking risk. It is removed
without replacement.

---

## Credits

This is a fork of [Kiwi Browser](https://github.com/kiwibrowser/src.next) by
**Arnaud GRANAL** and contributors, which is itself a fork of
[Chromium](https://www.chromium.org/).

Kiwi solved the hard problem first: getting extensions to run on Android at all,
years before Chromium had any path for it. This project would not exist without
that work, and its patch series remains the best available documentation of what
that entails.

---

## License

Chromium is distributed under a [BSD 3-Clause license](https://chromium.googlesource.com/chromium/src/+/main/LICENSE).
Kiwi Browser's additions carry their own copyright headers, which are preserved.
Patches and tooling in this repository follow the same terms.

---

## Not affiliated

Not affiliated with, endorsed by or connected to Google LLC, the Chromium
project, or Kiwi Browser. "Chromium" and "Google Chrome" are trademarks of
Google LLC.

---

## Naming

Pick a name that is not derived from "Kiwi" and use a distinct package name
(`org.<yourname>.browser`). Anything else risks colliding with existing Kiwi
installations on users' devices — and invites trademark trouble you do not need.
