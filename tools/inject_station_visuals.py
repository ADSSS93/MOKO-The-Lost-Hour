import pathlib, sys
# Keep the authored gameplay renderer intact. The previous injector replaced
# station_art() with an experimental world3d call, which made visual builds
# fail at link time and left players testing an older artifact.
src = pathlib.Path(sys.argv[1]).read_text()
pathlib.Path(sys.argv[2]).write_text(src)
