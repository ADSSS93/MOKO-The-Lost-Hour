import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()
anchor='slice_reset();for(i=0;i<4;i++)'
if anchor not in src:
    raise SystemExit('Village runtime cleanup: slice reset anchor missing')
src=src.replace(anchor,'slice_reset();tutorial_flags=15;for(i=0;i<4;i++)',1)
src+='\n/* VILLAGE RUNTIME CLEANUP REV 305: legacy tutorial panel disabled in vertical slice */\n'
pathlib.Path(sys.argv[2]).write_text(src)
