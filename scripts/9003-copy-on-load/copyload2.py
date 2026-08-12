import re, sys
B = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/extensions/api/developer_private/"
F = B + "developer_private_functions.cc"
H = B + "developer_private_functions.h"

s = open(F).read()
if "CopyVirtualDirectory" in s:
    print("schon angewendet"); sys.exit(0)

old = '''void DeveloperPrivateLoadUnpackedFunction::StartFileLoad(
    base::FilePath file_path) {
#if BUILDFLAG(IS_ANDROID)
  // SelectFileDialog returns a content URI so on Android we need to further
  // resolve it to a virtual document path
  std::optional<base::FilePath> vp =
      base::ResolveToVirtualDocumentPath(file_path);
  if (!vp) {
    OnLoadComplete(nullptr, file_path, u"Failed to resolve (removed?)");
    return;
  }
  file_path = *vp;
#endif  // BUILDFLAG(IS_ANDROID)
'''

if old not in s:
    print("FEHLER: Funktionskopf weicht ab")
    print("Bitte zeigen: sed -n '954,972p' developer_private_functions.cc")
    sys.exit(1)

new = '''#if BUILDFLAG(IS_ANDROID)
namespace {

// Copies a SAF-backed directory tree into app storage. Running an unpacked
// extension straight off a document provider is unusably slow: every file
// access crosses a Binder IPC.
bool CopyVirtualDirectory(const base::FilePath& from,
                          const base::FilePath& to) {
  int copied = 0;
  LOG(ERROR) << "[COPYDBG] start " << from.value() << " -> " << to.value();
  base::DeletePathRecursively(to);
  if (!base::CreateDirectory(to)) {
    LOG(ERROR) << "[COPYDBG] cannot create destination";
    return false;
  }
  base::FileEnumerator traversal(
      from, true,
      base::FileEnumerator::FILES | base::FileEnumerator::DIRECTORIES);
  for (base::FilePath p = traversal.Next(); !p.empty(); p = traversal.Next()) {
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
      LOG(ERROR) << "[COPYDBG] cannot open " << p.value();
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
    if (++copied % 100 == 0) {
      LOG(ERROR) << "[COPYDBG] " << copied << " files";
    }
  }
  LOG(ERROR) << "[COPYDBG] done, " << copied << " files";
  return true;
}

}  // namespace
#endif  // BUILDFLAG(IS_ANDROID)

void DeveloperPrivateLoadUnpackedFunction::StartFileLoad(
    base::FilePath file_path) {
#if BUILDFLAG(IS_ANDROID)
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
          .AppendASCII(base::NumberToString(base::PersistentHash(
              source.value())));
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
  LOG(ERROR) << "[COPYDBG] OnCopyComplete success=" << success;
  if (!success) {
    OnLoadComplete(nullptr, source, u"Failed to copy extension directory");
    return;
  }
  ContinueFileLoad(std::move(dest));
}

void DeveloperPrivateLoadUnpackedFunction::ContinueFileLoad(
    base::FilePath file_path) {
'''

s = s.replace(old, new, 1)

anchor = ('#include "chrome/browser/extensions/api/developer_private/'
          'developer_private_functions.h"')
inc = anchor + """
#if BUILDFLAG(IS_ANDROID)
#include "base/files/file.h"
#include "base/files/file_enumerator.h"
#include "base/files/file_util.h"
#include "base/hash/hash.h"
#include "base/strings/string_number_conversions.h"
#include "base/task/thread_pool.h"
#endif"""
if anchor not in s:
    print("FEHLER: Include-Anker fehlt"); sys.exit(1)
s = s.replace(anchor, inc, 1)
open(F, "w").write(s)

h = open(H).read()
if "ContinueFileLoad" not in h:
    a = "  void StartFileLoad(const base::FilePath file_path);"
    if a not in h:
        print("FEHLER: Header-Anker fehlt"); sys.exit(1)
    h = h.replace(a, a + """
  void ContinueFileLoad(base::FilePath file_path);
  void OnCopyComplete(base::FilePath dest,
                      base::FilePath source,
                      bool success);""", 1)
    open(H, "w").write(h)

print("ok")