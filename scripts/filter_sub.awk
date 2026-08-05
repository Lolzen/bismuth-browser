NR==FNR { p[++n] = $0 "/"; next }
{ for (i = 1; i <= n; i++) if (index($0, p[i]) == 1) next; print }