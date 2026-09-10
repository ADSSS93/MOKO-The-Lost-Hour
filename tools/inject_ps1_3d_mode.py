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
        /* Genuine PS1 GTE perspective scene. Gameplay remains in authored 2D
           coordinates; presentation maps those coordinates into the 3D world. */
        world3d_draw_station(px,py,facing,anim_tick,db[active].ot,&next_packet);
        slice_art();
    }else if(room==1)street_art();
    else if(room==2)house_art();
    else if(room==3)clockworks_art();
    else chamber_art();
    /* Keep interactive actors visible while the station migrates to full 3D. */
    living_art();world_event_art();echo_art();
    if(room<4&&!shard_taken[room]&&puzzle_done[room])draw_shard(250-room*35,90+room*28);
    /* Silent Station Moko is rendered as low-poly geometry by world3d.c. */
    if(room!=0)draw_moko();
    for(i=0;i<5;i++)if(room!=0)rect((i*61+anim_tick/3)%320,72+((i*31+anim_tick/5)%126),1,1,70,75,100);
}
'''
src=pat.sub(room+'static void collect_shard',src,count=1)
src+='\n/* PS1 3D MODE REV 286: GTE station + low-poly Moko active in gameplay */\n'
pathlib.Path(sys.argv[2]).write_text(src)
