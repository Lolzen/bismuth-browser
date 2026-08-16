import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

if "Register the retry path" in s:
    print("schon erledigt")
    sys.exit(0)

# 1. Kennung vor dem Kopieren vergeben
a = "  base::ThreadPool::PostTaskAndReplyWithResult("
b = """  // Register the retry path before copying, so a failed copy still offers a
  // working retry. Retrying re-runs the copy from the original SAF folder.
  retry_guid_ = DeveloperPrivateAPI::Get(browser_context())
                    ->AddUnpackedPath(GetSenderWebContents(), source);
  base::ThreadPool::PostTaskAndReplyWithResult("""
if a not in s:
    print("FEHLER: Anker 1 fehlt")
    sys.exit(1)
s = s.replace(a, b, 1)

# 2. spaeter nicht ueberschreiben
a2 = """  retry_guid_ = DeveloperPrivateAPI::Get(browser_context())
                    ->AddUnpackedPath(GetSenderWebContents(), file_path);"""
b2 = """  if (retry_guid_.empty()) {
    retry_guid_ = DeveloperPrivateAPI::Get(browser_context())
                      ->AddUnpackedPath(GetSenderWebContents(), file_path);
  }"""
if s.count(a2) != 1:
    print("FEHLER: Anker 2 nicht eindeutig:", s.count(a2))
    sys.exit(1)
s = s.replace(a2, b2, 1)

open(F, "w").write(s)
print("ok")