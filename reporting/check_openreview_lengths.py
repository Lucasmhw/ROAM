"""Check actual pasted Comment lengths after manually editing the master file.

Usage: python check_openreview_lengths.py [path/to/rebuttal.md]
The surrounding fenced blocks and editorial labels are excluded.
No external packages or network access are needed.
"""
from pathlib import Path
import re
import sys

path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('01_ROAM_OpenReview_Rebuttal.md')
text=path.read_text(encoding='utf-8')
titles=re.findall(r'```text\n(.*?)\n```',text,re.S)
bodies=re.findall(r'```markdown\n(.*?)\n```',text,re.S)
ids=re.findall(r'^## ([A-Za-z0-9_]+) \|',text,re.M)
if not(len(titles)==len(bodies)==len(ids)):
    raise SystemExit('Mismatched ID / Title / Comment blocks. Check Markdown fences.')
failed=False
print('ID                 Title  Comment(LF)  Comment(CRLF)  Combined(CRLF)  Status')
for cid,title,body in zip(ids,titles,bodies):
    nt=len(title.encode('utf-16-le'))//2
    nb=len(body.encode('utf-16-le'))//2
    nc=nb+body.count('\n')
    ok=nt<=500 and nc<=5000
    failed|=not ok
    print(f'{cid:18} {nt:5} {nb:12} {nc:14} {nt+nc:15}  '+('PASS' if ok else 'OVER LIMIT'))
print(f'Checked {len(bodies)} comments. Combined counts are an extra conservative reference.')
raise SystemExit(1 if failed else 0)
