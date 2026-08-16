D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()
a = """  int rewritten = 0;
"""
b = """"""
c = """    if (base::WriteFile(target, data)) {
      ++rewritten;
    }"""
d = """    base::WriteFile(target, data);"""
n = 0
if a in s:
    s = s.replace(a, b, 1); n += 1
if c in s:
    s = s.replace(c, d, 1); n += 1
open(F, "w").write(s)
print("Stellen bereinigt:", n)