import pathlib, sys
src=pathlib.Path(sys.argv[1]).read_text()
start=src.index('static void station_art(void){')
end=src.index('\nstatic void street_art', start)
src=src[:start]+'static void station_art(void){world3d_draw_station(px,py,facing,anim_tick,db[active].ot,&next_packet);}' + src[end:]
needle='#include "world_runtime.h"\n'
if '#include "world3d.h"' not in src:
    src=src.replace(needle, needle+'#include "world3d.h"\n')
pathlib.Path(sys.argv[2]).write_text(src)
