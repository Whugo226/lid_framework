"""Correct em-dash sweep for a thesis chapter.

Two failure modes this exists to avoid, both found on CH4 (2026-08-03):

1. `grep -- "---" file | grep -v candidatetodo` DISCARDS BODY PROSE.
   Body prose frequently follows a \\candidatetodo{...} on the same source line,
   so the line-level filter throws away the prose along with the note. A live em
   dash survived two verification passes this way. This script instead strips
   \\candidatetodo{...} bodies with a brace-matching parse and searches the rest.

2. A `---` grep CANNOT SEE literal em dash characters (U+2014). CH4 held 7,
   all inside bold run-in labels. Both forms are checked here.

Usage (from the thesis root):
    python <skill>/scripts/check_dashes.py chapters/<file>.tex [more.tex ...]

Exit status is 0 always; read the output. Hits inside tables/figures are
protected by SKILL.md section 4 — check the reported line before "fixing" one.
"""
import io
import sys

EM = '—'
EN = '–'


def strip_macro_bodies(s, macro='\\candidatetodo{'):
    """Remove macro{...} bodies, brace-matched, keeping surrounding prose."""
    out = []
    i = 0
    while True:
        j = s.find(macro, i)
        if j < 0:
            out.append(s[i:])
            return ''.join(out)
        out.append(s[i:j])
        k = j + len(macro)
        depth = 1
        while k < len(s) and depth:
            if s[k] == '{':
                depth += 1
            elif s[k] == '}':
                depth -= 1
            k += 1
        i = k


def main(argv):
    for path in argv:
        text = io.open(path, encoding='utf-8').read()
        print('\n=== %s ===' % path)
        print('  literal em dash U+2014 (whole file): %d' % text.count(EM))
        print('  literal en dash U+2013 (whole file): %d' % text.count(EN))
        hits = []
        for i, line in enumerate(text.split('\n'), 1):
            if line.strip().startswith('%'):
                continue
            clean = strip_macro_bodies(line)
            # `---` and literal U+2014/U+2013 are the tells.
            # Bare `--` is the CORRECT LaTeX en dash for ranges and paired
            # compounds (3--5-gram, sentence--sentence, 17--18) — never flag it.
            if '---' in clean or EM in clean or EN in clean:
                hits.append((i, clean.strip()[:110]))
        print('  dash hits in body prose (candidatetodo bodies stripped): %d' % len(hits))
        for i, s in hits:
            print('    L%-5d %s' % (i, ascii(s)))
        if not hits:
            print('    (clean)')


if __name__ == '__main__':
    main(sys.argv[1:])
