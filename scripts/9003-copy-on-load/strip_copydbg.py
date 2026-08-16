import re, sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

# doppelter Schreibvorgang aus der Diagnose
s = re.sub(r'\n    if \(target\.BaseName\(\)\.value\(\) == "manifest\.json"\) \{'
           r'[\s\S]*?\n    \}\n(?=    if \(!base::WriteFile)', '\n', s, count=1)

# Zielprotokollierung
s = re.sub(r'\n    if \(copied < 5 \|\| target\.DirName\(\) == to\) \{'
           r'[\s\S]*?\n    \}\n', '\n', s, count=1)

# Fortschrittszaehler ohne Ausgabe
s = re.sub(r'    if \(\+\+copied % 25 == 0\) \{[\s\S]*?\n    \}\n',
           '    ++copied;\n', s, count=1)

# alle uebrigen COPYDBG-Ausgaben
s = re.sub(r'[ \t]*LOG\(ERROR\) << "\[COPYDBG\][\s\S]*?;\n', '', s)

open(F, "w").write(s)
print("verbliebene COPYDBG:", s.count("COPYDBG"))