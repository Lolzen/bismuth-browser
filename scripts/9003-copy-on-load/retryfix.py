import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

falsch = """  // Register the retry path before copying, so a failed copy still offers a
  // working retry. Retrying re-runs the copy from the original SAF folder.
  retry_guid_ = DeveloperPrivateAPI::Get(browser_context())
                    ->AddUnpackedPath(GetSenderWebContents(), source);
  base::ThreadPool::PostTaskAndReplyWithResult("""

if falsch in s:
    s = s.replace(falsch, "  base::ThreadPool::PostTaskAndReplyWithResult(", 1)
    print("falsche Einfuegung entfernt")

anker = """              source.value())));
  base::ThreadPool::PostTaskAndReplyWithResult("""

neu = """              source.value())));
  // Register the retry path before copying, so a failed copy still offers a
  // working retry. Retrying re-runs the copy from the original SAF folder.
  retry_guid_ = DeveloperPrivateAPI::Get(browser_context())
                    ->AddUnpackedPath(GetSenderWebContents(), source);
  base::ThreadPool::PostTaskAndReplyWithResult("""

if "Register the retry path" in s:
    print("schon an richtiger Stelle"); sys.exit(0)
if s.count(anker) != 1:
    print("FEHLER: Anker nicht eindeutig:", s.count(anker)); sys.exit(1)

open(F, "w").write(s.replace(anker, neu, 1))
print("ok")