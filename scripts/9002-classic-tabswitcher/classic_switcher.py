import re, sys

S = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/")

# ---------- 1. Spaltenzahl auf 1 ----------
F = S + "TabListMediator.java"
s = open(F).read()
a = "        final int newSpanCount = getSpanCount(screenWidthDp);"
b = ("        // Classic tab switcher: a single column of full-width cards.\n"
     "        final int newSpanCount = 1;")
if "single column of full-width cards" in s:
    print("Mediator schon gepatcht")
elif a not in s:
    print("FEHLER: Mediator-Anker nicht gefunden")
    sys.exit(1)
else:
    open(F, "w").write(s.replace(a, b, 1))
    print("ok Mediator")

# ---------- 2. Ueberlappung ----------
F = S + "TabListCoordinator.java"
s = open(F).read()

if "ClassicStyleItemDecoration" in s:
    print("Coordinator schon gepatcht")
    sys.exit(0)

if "import android.content.res.Configuration;" not in s:
    m = re.search(r"^import android\.", s, re.M)
    if not m:
        print("FEHLER: kein android-Import gefunden")
        sys.exit(1)
    s = s[:m.start()] + "import android.content.res.Configuration;\n" + s[m.start():]

deco = '''    /** Draws tab cards as an overlapping vertical stack, like the classic switcher. */
    private static class ClassicStyleItemDecoration extends RecyclerView.ItemDecoration {
        private static final int OVERLAP_DP = 75;

        @Override
        public void getItemOffsets(
                Rect outRect, View view, RecyclerView parent, RecyclerView.State state) {
            outRect.left = 0;
            outRect.right = 0;
            outRect.bottom = 0;
            boolean isPortrait =
                    parent.getContext().getResources().getConfiguration().orientation
                            == Configuration.ORIENTATION_PORTRAIT;
            boolean isFirst = parent.getChildAdapterPosition(view) == 0;
            if (!isPortrait || isFirst) {
                outRect.top = 0;
                return;
            }
            outRect.top =
                    -(int) Math.ceil(
                            OVERLAP_DP * parent.getResources().getDisplayMetrics().density);
        }
    }

'''

anchor = "    private void updateGridCardLayout(int viewWidth) {"
if anchor not in s:
    print("FEHLER: Anker fuer Dekoration nicht gefunden")
    sys.exit(1)
s = s.replace(anchor, deco + anchor, 1)

a2 = "                mRecyclerView.setLayoutManager(gridLayoutManager);"
b2 = (a2 + "\n"
      "                mRecyclerView.addItemDecoration(new ClassicStyleItemDecoration());")
if a2 not in s:
    print("FEHLER: setLayoutManager-Anker nicht gefunden")
    sys.exit(1)
s = s.replace(a2, b2, 1)

open(F, "w").write(s)
print("ok Coordinator")