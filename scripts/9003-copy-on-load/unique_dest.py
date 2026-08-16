import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

if "-\" + base::NumberToString(base::Time::Now()" in s:
    print("schon erledigt"); sys.exit(0)

a = """          .AppendASCII(base::NumberToString(base::PersistentHash(
              source.value())));"""
b = """          .AppendASCII(
              base::NumberToString(base::PersistentHash(source.value())) + "-" +
              base::NumberToString(
                  base::Time::Now().ToDeltaSinceWindowsEpoch().InMicroseconds()));"""
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
s = s.replace(a, b, 1)

anker = '#include "base/task/thread_pool.h"'
if anker in s and '#include "base/time/time.h"' not in s:
    s = s.replace(anker, anker + '\n#include "base/time/time.h"', 1)

open(F, "w").write(s)
print("ok")