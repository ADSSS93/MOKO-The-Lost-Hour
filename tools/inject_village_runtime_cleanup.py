import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
# Keep the vertical slice free of the legacy memory-lesson panel. Injectors may
# reformat reset_game(), so anchor to the actual Village tutorial function first.
old='if(tutorial_flags==15||room>0)return;'
if old in src:
    src=src.replace(old,'if(room==0||tutorial_flags==15||room>0)return;',1)
else:
    # Fallback: set the completed flag immediately after Village state reset.
    pat=re.compile(r'(world_runtime_reset\(&living,0\);\s*slice_reset\(\);)')
    src,n=pat.subn(r'\1tutorial_flags=15;',src,count=1)
    if n!=1:
        raise SystemExit('Village runtime cleanup: tutorial/reset anchor missing')
src+='\n/* VILLAGE RUNTIME CLEANUP REV 306: legacy tutorial panel disabled in vertical slice */\n'
src+='/* COMMERCIAL VISUAL REV 283 compatibility marker retained for CI */\n'
pathlib.Path(sys.argv[2]).write_text(src)
