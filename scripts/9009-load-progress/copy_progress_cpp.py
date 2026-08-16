import sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"
D = B + "chrome/browser/extensions/api/developer_private/"

# ---------- 1. Schema ----------
f = B + "chrome/common/extensions/api/developer_private.webidl"
s = open(f).read()
if "OnCopyProgressEvent" in s:
    print("webidl schon erledigt")
else:
    a = "// Listener callback for the onItemStateChanged event."
    b = """// Progress while copying an unpacked extension into app storage.
dictionary CopyProgress {
  required long copied;
  required long total;
};

// Listener callback for the onCopyProgress event.
callback OnCopyProgressListener = undefined (CopyProgress progress);

interface OnCopyProgressEvent : ExtensionEvent {
  static undefined addListener(OnCopyProgressListener listener);
  static undefined removeListener(OnCopyProgressListener listener);
  static boolean hasListener(OnCopyProgressListener listener);
};

// Listener callback for the onItemStateChanged event."""
    if a not in s:
        print("FEHLER: webidl-Anker 1"); sys.exit(1)
    s = s.replace(a, b, 1)

    a2 = "  static attribute OnItemStateChangedEvent onItemStateChanged;"
    b2 = a2 + "\n\n  static attribute OnCopyProgressEvent onCopyProgress;"
    if a2 not in s:
        print("FEHLER: webidl-Anker 2"); sys.exit(1)
    open(f, "w").write(s.replace(a2, b2, 1))
    print("ok webidl")

# ---------- 2. Kopf ----------
f = D + "developer_private_functions.h"
s = open(f).read()
if "OnCopyProgress" in s:
    print("header schon erledigt")
else:
    a = "  void OnCopyComplete(base::FilePath dest,"
    b = "  void OnCopyProgress(int copied, int total);\n" + a
    if a not in s:
        print("FEHLER: header-Anker"); sys.exit(1)
    open(f, "w").write(s.replace(a, b, 1))
    print("ok header")

# ---------- 3. Implementierung ----------
f = D + "developer_private_functions.cc"
s = open(f).read()
if "OnCopyProgress" in s:
    print("cc schon erledigt"); sys.exit(0)

a = """bool CopyVirtualDirectory(const base::FilePath& from,
                          const base::FilePath& to) {"""
b = """bool CopyVirtualDirectory(const base::FilePath& from,
                          const base::FilePath& to,
                          base::RepeatingCallback<void(int, int)> on_progress) {
  int total = 0;
  {
    base::FileEnumerator counter(from, true, base::FileEnumerator::FILES);
    for (base::FilePath p = counter.Next(); !p.empty(); p = counter.Next()) {
      ++total;
    }
  }
  on_progress.Run(0, total);"""
if a not in s:
    print("FEHLER: Funktionskopf"); sys.exit(1)
s = s.replace(a, b, 1)

a = "    ++copied;"
b = """    ++copied;
    if (copied % 10 == 0) {
      on_progress.Run(copied, total);
    }"""
if a not in s:
    print("FEHLER: Zaehler"); sys.exit(1)
s = s.replace(a, b, 1)

a = "      base::BindOnce(&CopyVirtualDirectory, source, dest),"
b = """      base::BindOnce(
          &CopyVirtualDirectory, source, dest,
          base::BindPostTask(
              content::GetUIThreadTaskRunner({}),
              base::BindRepeating(
                  &DeveloperPrivateLoadUnpackedFunction::OnCopyProgress,
                  this))),"""
if a not in s:
    print("FEHLER: BindOnce"); sys.exit(1)
s = s.replace(a, b, 1)

a = "void DeveloperPrivateLoadUnpackedFunction::OnCopyComplete("
b = """void DeveloperPrivateLoadUnpackedFunction::OnCopyProgress(int copied,
                                                          int total) {
  developer::CopyProgress progress;
  progress.copied = copied;
  progress.total = total;
  base::ListValue args;
  args.Append(progress.ToValue());
  auto event = std::make_unique<Event>(
      events::DEVELOPER_PRIVATE_ON_ITEM_STATE_CHANGED,
      developer::OnCopyProgress::kEventName, std::move(args));
  EventRouter::Get(browser_context())->BroadcastEvent(std::move(event));
}

void DeveloperPrivateLoadUnpackedFunction::OnCopyComplete("""
if a not in s:
    print("FEHLER: OnCopyComplete"); sys.exit(1)
s = s.replace(a, b, 1)

anker = '#include "base/time/time.h"'
if anker in s:
    s = s.replace(anker, anker + '\n#include "base/task/bind_post_task.h"', 1)

open(f, "w").write(s)
print("ok cc")