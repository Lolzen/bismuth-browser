#!/usr/bin/env python3
"""Copy-on-Load fuer entpackte Erweiterungen auf Android.

Teilt DeveloperPrivateLoadUnpackedFunction::StartFileLoad in zwei Haelften
und kopiert den ueber SAF gewaehlten Ordner vorher in den App-Speicher.
Grund: Jeder Dateizugriff ueber den Document Provider kostet einen
Binder-IPC, was Erweiterungen mit vielen Dateien unbenutzbar langsam macht.

Idempotent: bricht ab, wenn der Patch bereits angewendet wurde.
Schreibt erst, wenn alle Ersetzungen gelungen sind.
"""

import re
import sys

S = "/home/gee/kiwi-rebase/build/chromium/src"
BASE = S + "/chrome/browser/extensions/api/developer_private/"
F = BASE + "developer_private_functions.cc"
H = BASE + "developer_private_functions.h"

src = open(F).read()

if "CopyVirtualDirectory" in src:
    print("Patch scheint bereits angewendet zu sein - Abbruch")
    sys.exit(1)

# ---------------------------------------------------------------- includes
inc_anchor = ('#include "chrome/browser/extensions/api/developer_private/'
              'developer_private_functions.h"')
inc_new = inc_anchor + """
#if BUILDFLAG(IS_ANDROID)
#include "base/files/file.h"
#include "base/files/file_enumerator.h"
#include "base/files/file_util.h"
#include "base/hash/hash.h"
#include "base/strings/string_number_conversions.h"
#include "base/task/thread_pool.h"
#endif"""

if inc_anchor not in src:
    print("FEHLER: Include-Anker nicht gefunden")
    sys.exit(1)
src = src.replace(inc_anchor, inc_new, 1)

# ------------------- Schritt 1: alten Android-Block entfernen (tolerant)
# Ankert auf "file_path = *vp;" - diese Zeile ist im Original eindeutig.
block_re = re.compile(
    r"#if BUILDFLAG\(IS_ANDROID\)\n"
    r"(?:[^\n]*\n)*?"
    r"[ \t]*file_path = \*vp;\n"
    r"[ \t]*#?endif[^\n]*\n",
)

matches = block_re.findall(src)
if len(matches) != 1:
    print("FEHLER: Android-Block nicht eindeutig, gefunden:", len(matches))
    print("Bitte zeigen mit:")
    print("  cd " + BASE)
    print("  grep -n -A16 'StartFileLoad(' developer_private_functions.cc")
    sys.exit(1)

src = block_re.sub("", src, count=1)

# ------------------------------------- Schritt 2: Kopierfunktion + Umbau
helper = """
#if BUILDFLAG(IS_ANDROID)
namespace {

// Copies a SAF-backed directory tree into app storage. Extensions loaded
// straight from a document provider are unusably slow: every file access
// crosses a Binder IPC to the document provider process.
bool CopyVirtualDirectory(const base::FilePath& from,
                          const base::FilePath& to) {
  base::DeletePathRecursively(to);
  if (!base::CreateDirectory(to)) {
    return false;
  }
  base::FileEnumerator traversal(
      from, true,
      base::FileEnumerator::FILES | base::FileEnumerator::DIRECTORIES);
  for (base::FilePath p = traversal.Next(); !p.empty();
       p = traversal.Next()) {
    base::FilePath target = to;
    if (!from.AppendRelativePath(p, &target)) {
      continue;
    }
    if (traversal.GetInfo().IsDirectory()) {
      if (!base::CreateDirectory(target)) {
        return false;
      }
      continue;
    }
    base::File in(p, base::File::FLAG_OPEN | base::File::FLAG_READ);
    if (!in.IsValid()) {
      return false;
    }
    std::string data;
    std::vector<uint8_t> buf(65536);
    while (true) {
      std::optional<size_t> n = in.ReadAtCurrentPos(base::span(buf));
      if (!n) {
        return false;
      }
      if (*n == 0) {
        break;
      }
      data.append(reinterpret_cast<const char*>(buf.data()), *n);
    }
    if (!base::WriteFile(target, data)) {
      return false;
    }
  }
  return true;
}

}  // namespace
#endif  // BUILDFLAG(IS_ANDROID)

"""

old_start = ("void DeveloperPrivateLoadUnpackedFunction::StartFileLoad(\n"
             "    base::FilePath file_path) {")

if old_start not in src:
    print("FEHLER: StartFileLoad nicht gefunden")
    sys.exit(1)

new_start = helper + """void DeveloperPrivateLoadUnpackedFunction::StartFileLoad(
    base::FilePath file_path) {
#if BUILDFLAG(IS_ANDROID)
  // SelectFileDialog returns a content URI so on Android we need to further
  // resolve it to a virtual document path.
  std::optional<base::FilePath> vp =
      base::ResolveToVirtualDocumentPath(file_path);
  if (!vp) {
    OnLoadComplete(nullptr, file_path, u"Failed to resolve (removed?)");
    return;
  }
  base::FilePath source = *vp;
  base::FilePath dest =
      browser_context()->GetPath()
          .AppendASCII("UnpackedExtensions")
          .AppendASCII(base::NumberToString(
              base::PersistentHash(source.value())));
  base::ThreadPool::PostTaskAndReplyWithResult(
      FROM_HERE, {base::MayBlock(), base::TaskPriority::USER_VISIBLE},
      base::BindOnce(&CopyVirtualDirectory, source, dest),
      base::BindOnce(&DeveloperPrivateLoadUnpackedFunction::OnCopyComplete,
                     this, dest, source));
  return;
#else
  ContinueFileLoad(std::move(file_path));
#endif
}

void DeveloperPrivateLoadUnpackedFunction::OnCopyComplete(
    base::FilePath dest,
    base::FilePath source,
    bool success) {
  if (!success) {
    OnLoadComplete(nullptr, source, u"Failed to copy extension directory");
    return;
  }
  ContinueFileLoad(std::move(dest));
}

void DeveloperPrivateLoadUnpackedFunction::ContinueFileLoad(
    base::FilePath file_path) {"""

src = src.replace(old_start, new_start, 1)

# ---------------------------------------------------------------- Header
hdr = open(H).read()
hdr_out = None

if "ContinueFileLoad" in hdr:
    print("WARNUNG: Header scheint bereits gepatcht - uebersprungen")
else:
    anchor_re = re.compile(r"[ \t]*void StartFileLoad\([^\)]*\);")
    m = anchor_re.search(hdr)
    if not m:
        print("FEHLER: Header-Anker nicht gefunden.")
        print("Bitte pruefen mit:")
        print("  cd " + BASE)
        print("  grep -n StartFileLoad developer_private_functions.h")
        sys.exit(1)
    add = (m.group(0) + "\n"
           "  void ContinueFileLoad(base::FilePath file_path);\n"
           "  void OnCopyComplete(base::FilePath dest,\n"
           "                      base::FilePath source,\n"
           "                      bool success);")
    hdr_out = hdr[:m.start()] + add + hdr[m.end():]

# Erst jetzt schreiben, wenn alles geklappt hat.
open(F, "w").write(src)
if hdr_out is not None:
    open(H, "w").write(hdr_out)

print("ok - Patch angewendet")