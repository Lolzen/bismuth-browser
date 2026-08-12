import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/net/url_request/"
     "url_request_http_job.cc")
s = open(F).read()

if "chromewebstore" in s:
    print("schon da"); sys.exit(0)

a = """  request_info_.extra_headers.SetHeaderIfMissing(
      HttpRequestHeaders::kUserAgent,
      http_user_agent_settings_ ? http_user_agent_settings_->GetUserAgent()
                                : std::string());"""

b = a + """

  // The Chrome Web Store only serves its extension pages to desktop browsers.
  // Present a desktop identity for those hosts only; every other request keeps
  // the regular mobile user agent.
  {
    const std::string webstore_host = request_info_.url.host();
    if (webstore_host == "chromewebstore.google.com" ||
        webstore_host == "chrome.google.com") {
      request_info_.extra_headers.SetHeader(
          HttpRequestHeaders::kUserAgent,
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36");
      request_info_.extra_headers.SetHeader(
          "Sec-CH-UA",
          "\\"Chromium\\";v=\\"149\\", \\"Not:A-Brand\\";v=\\"24\\", "
          "\\"Google Chrome\\";v=\\"149\\"");
      request_info_.extra_headers.SetHeader("Sec-CH-UA-Mobile", "?0");
      request_info_.extra_headers.SetHeader("Sec-CH-UA-Platform",
                                            "\\"Windows\\"");
    }
  }"""

if a not in s:
    print("Anker nicht gefunden"); sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")