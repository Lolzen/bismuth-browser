import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/tools/typescript/definitions/"
     "developer_private.d.ts")
s = open(F).read()

if "CopyProgress" in s:
    print("schon erledigt"); sys.exit(0)

a = "      export const onItemStateChanged: ChromeEvent<(data: EventData) => void>;"
b = """      export interface CopyProgress {
        copied: number;
        total: number;
      }

      export const onItemStateChanged: ChromeEvent<(data: EventData) => void>;

      export const onCopyProgress:
          ChromeEvent<(progress: CopyProgress) => void>;"""

if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")