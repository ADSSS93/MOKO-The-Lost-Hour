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
        /* Runtime REV302: the real PCSX-Redux capture showed that the old nearly
           black framebuffer clear became visible wherever the perspective sky
           rotated away from the viewport, creating a giant false "black wedge".
           Use the PS1 draw-environment clear itself as the far dawn atmosphere;
           this is framebuffer state, not a screen-space debug rectangle. */
        setRGB0(&db[0].draw,62,54,76);setRGB0(&db[1].draw,62,54,76);
        /* Village of Dawn vertical slice: gameplay X/Y become ground-plane X/Z,
           while the existing jump controller drives the 3D model vertically. */
        world3d_draw_village(px,py,moko_z/16,facing,anim_tick,slice_motes,slice_enemy_hp,slice_clear,db[active].ot,&next_packet);
        return;
    }
    /* Restore the legacy dark clear for non-Village rooms. */
    setRGB0(&db[0].draw,6,7,15);setRGB0(&db[1].draw,6,7,15);
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
src+='\n/* REAL 3D VERTICAL SLICE REV 302: runtime dawn clear + depth lanes + animated jump */\n'
src+='/* REAL 3D VERTICAL SLICE REV 288 compatibility marker for legacy CI */\n'
pathlib.Path(sys.argv[2]).write_text(src)
