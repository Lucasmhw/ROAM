from pathlib import Path,PurePosixPath
import io
import json
import urllib.request
import zipfile

REPOS={
    'Time-Series-Library':('thuml/Time-Series-Library','4e938a1767106324dd753b2a44832bf870a0252e'),
    'ModernTCN':('luodhhh/ModernTCN','56a9a2c018385cd5acef015378cae7f084d1b11c'),
}
root=Path('vendor');root.mkdir(exist_ok=True)
for name,(repo,sha) in REPOS.items():
    dest=(root/name).resolve()
    if dest.exists():
        print('Already present:',name);continue
    url=f'https://codeload.github.com/{repo}/zip/{sha}'
    with urllib.request.urlopen(url,timeout=120) as response:
        archive=zipfile.ZipFile(io.BytesIO(response.read()))
    for member in archive.infolist():
        relative=PurePosixPath(member.filename)
        if member.is_dir() or len(relative.parts)<2:continue
        target=dest.joinpath(*relative.parts[1:]).resolve()
        if not target.is_relative_to(dest):raise ValueError('Unsafe archive member')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(archive.read(member))
    print('Installed:',name,sha)
(root/'versions.json').write_text(json.dumps(REPOS,indent=2))
