import sys
F = "/home/gee/kiwi-rebase/scripts/common/split_patches.sh"
s = open(F).read()

a = "  extensions/common/extension_features.cc \\\n"
b = ("  extensions/common/extension_features.cc \\\n"
     "  extensions/browser/manifest_v2_experiment_manager.cc \\\n")

if "manifest_v2_experiment_manager.cc" in s:
    print("schon erledigt"); sys.exit(0)
if s.count(a) != 1:
    print("FEHLER, Treffer:", s.count(a))
    print("Bitte zeigen: grep -n -A6 'mk 9001' split_patches.sh")
    sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")