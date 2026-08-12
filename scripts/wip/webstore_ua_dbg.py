import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/net/url_request/"
     "url_request_http_job.cc")
s = open(F).read()

if "UADBG" in s:
    print("schon da"); sys.exit(0)

a = """    const std::string_view webstore_host = request_info_.url.host();
    if (webstore_host == "chromewebstore.google.com" ||
        webstore_host == "chrome.google.com") {"""
b = """    const std::string_view webstore_host = request_info_.url.host();
    if (webstore_host.find("google.com") != std::string_view::npos) {
      LOG(ERROR) << "[UADBG] host=" << webstore_host;
    }
    if (webstore_host == "chromewebstore.google.com" ||
        webstore_host == "chrome.google.com") {
      LOG(ERROR) << "[UADBG] MATCH, setting desktop headers";"""

if a not in s:
    print("Anker nicht gefunden"); sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")