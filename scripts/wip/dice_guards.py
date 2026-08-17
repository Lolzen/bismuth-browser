import sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

edits = [
("chrome/browser/contextual_tasks/BUILD.gn",
 """  if (enable_dice_support) {
    sources += [ "search_ai_mode_promo_tab_helper_interactive_uitest.cc" ]""",
 """  if (enable_dice_support && !is_android) {
    sources += [ "search_ai_mode_promo_tab_helper_interactive_uitest.cc" ]"""),

("chrome/browser/policy/BUILD.gn",
 """  if (enable_dice_support) {
    sources += [ "cloud/user_policy_signin_service_browsertest.cc" ]""",
 """  if (enable_dice_support && !is_android) {
    sources += [ "cloud/user_policy_signin_service_browsertest.cc" ]"""),

("chrome/browser/profiles/BUILD.gn",
 """  if (enable_dice_support) {
    deps += [
      "//chrome/browser/profiles/batch_upload",
      "//chrome/browser/ui/signin",
    ]
  }""",
 """  if (enable_dice_support && !is_android) {
    deps += [
      "//chrome/browser/profiles/batch_upload",
      "//chrome/browser/ui/signin",
    ]
  }"""),
]

for path, a, b in edits:
    f = B + path
    s = open(f).read()
    if b.split("\n")[0] in s:
        print("schon erledigt:", path); continue
    if s.count(a) != 1:
        print("FEHLER, Treffer:", s.count(a), "in", path); sys.exit(1)
    open(f, "w").write(s.replace(a, b, 1))
    print("ok", path)