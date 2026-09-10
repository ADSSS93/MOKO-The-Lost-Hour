import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if '#include "world3d.h"' not in src:
    src=src.replace('#include "world_runtime.h"','#include "world_runtime.h"\n#include "world3d.h"',1)
pat=re.compile(r'static void room_art\(void\)\{.*?\}\nstatic void collect_shard',re.S)
m=pat.search(src)
if not m: raise SystemExit('3d mode: room_art missing')
room=r'''static void room_art(void){
    int i;
    if(room==0){
        /* Village of Dawn vertical slice: the entire gameplay presentation is
           rendered in GTE 3D. No legacy 2D actors or debug scenery are layered
           over this scene. */
        world3d_draw_village(px,py,facing,anim_tick,slice_motes,slice_enemy_hp,slice_clear,db[active].ot,&next_packet);
        return;
    }
    if(room==1)street_art();
    else if(room==2)house_art();
    else if(room==3)clockworks_art();
    else chamber_art();
    living_art();world_event_art();echo_art();
    if(room<4&&!shard_taken[room]&&puzzle_done[room])draw_shard(250-room*35,90+room*28);
    draw_moko();
    for(i=0;i<5;i++)rect((i*61+anim_tick/3)%320,72+((i*31+anim_tick/5)%126),1,1,70,75,100);
}
'''
src=pat.sub(room+'static void collect_shard',src,count=1)
src+='\n/* REAL 3D VERTICAL SLICE REV 287: Village of Dawn active in gameplay */\n'
pathlib.Path(sys.argv[2]).write_text(src)
