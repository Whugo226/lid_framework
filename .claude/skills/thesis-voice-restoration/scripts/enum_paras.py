"""Paragraph inventory for a thesis chapter voice pass.

Lists every body paragraph and marks it touched / untouched by EXACT TEXT MATCH
against the pre-pass backup. Text match, not diff line numbers: paragraph splits
shift every subsequent line, so a line-number diff reports the whole file as
changed and is useless here.

Usage (from the thesis root):
    python <skill>/scripts/enum_paras.py chapters/<file>.tex [more.tex ...]

Prints, per file: total body paragraphs, touched, untouched, then every
untouched one as "L<line>  <words>w  <first 96 chars>".

Filter the output to the ones worth working:
    ... | grep -E "^  L" | awk '{if ($2+0>=45) print}'

KNOWN LIMITS — read before trusting the output:
  * Hard-wrapped paragraphs are counted per source line, so one logical
    paragraph spanning 6 wrapped lines shows as 6 entries. Judge by content.
  * Prose that FOLLOWS a \\candidatetodo{...} on the same line is body prose and
    IS included (KEEP_CMD). Edit the prose, never the note.
  * This script cannot tell you what a re-audit can: always ALSO ask the
    re-audit subagent to list paragraphs that came back byte-identical.
"""
import re
import sys

SKIP = re.compile(r'^\\(my)?(chapter|section|subsection|label|begin|end|includegraphics'
                  r'|caption|centering|Require|Ensure|State|For|EndFor|Return|noindent|vspace'
                  r'|ShortInTextTitle|hline|multicolumn|mytable|input|clearpage|toprule|midrule'
                  r'|bottomrule|centerline|par\b)')
# \item prose and post-\candidatetodo prose ARE body prose (blind spot found 2026-08-03).
KEEP_CMD = re.compile(r'^\\(textbf|emph|textit|item|candidatetodo)')
STRIP = re.compile(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?\{?|[{}$\\&]')

BACKUP_SEGMENT = 'backups/pre_voice_restoration_2026-08-03/chapters/'


def body_paragraphs(path):
    out = []
    for i, line in enumerate(open(path, encoding='utf-8'), 1):
        s = line.strip()
        if not s or s.startswith('%'):
            continue
        if SKIP.match(s):
            continue
        if s.startswith('\\') and not KEEP_CMD.match(s):
            continue
        if re.match(r'^[\d|&]', s):
            continue
        if re.match(r'^[A-Za-z_]+\s*=\s*\\frac', s) or s.startswith('C = ') or s.startswith('F_{'):
            continue
        words = len(STRIP.sub(' ', s).split())
        if words < 12:
            continue
        out.append((i, words, s))
    return out


def main(argv):
    for f in argv:
        old = f.replace('chapters/', BACKUP_SEGMENT)
        try:
            old_lines = {l.strip() for l in open(old, encoding='utf-8')}
        except OSError:
            print('!! no backup found at %s — make one before editing' % old)
            continue
        ps = body_paragraphs(f)
        un = [p for p in ps if p[2] in old_lines]
        print('\n=== %s: %d body paragraphs | touched %d | UNTOUCHED %d ==='
              % (f, len(ps), len(ps) - len(un), len(un)))
        for i, w, t in un:
            print('  L%-5d %3dw  %s' % (i, w, t[:96]))


if __name__ == '__main__':
    main(sys.argv[1:])
