import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

if 'STORY REV 263' not in src:
    raise SystemExit('audio polish revision anchor missing')
if 'S263 %02d:%02d' not in src:
    raise SystemExit('audio polish HUD anchor missing')

src = src.replace('STORY REV 263','AUDIO REV 264',1)
src = src.replace('S263 %02d:%02d','A264 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
