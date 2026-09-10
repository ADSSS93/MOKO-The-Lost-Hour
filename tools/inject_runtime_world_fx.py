import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

anchor = 'static void tutorial_input(uint16_t n)'
if anchor not in src:
    raise SystemExit('runtime world fx helper anchor missing')

helpers = r'''static void runtime_world_fx_art(void){
    int i,p=(anim_tick/6)&3,s=(anim_tick/3)%320;
    if(room==0){
        /* Silent Station: platform lamps, moving rail reflections and signal state. */
        for(i=0;i<6;i++){int x=20+i*56;rect(x,64,20,2,105,98,138);rect(x+8,66,4,5,185,163,205);}
        rect((s+40)%320,212,34,2,70,118,145);rect((s+126)%320,216,22,1,95,145,165);
        rect(151,120,18,3,puzzle_done[0]?70:170,puzzle_done[0]?220:55,puzzle_done[0]?105:70);
        if(puzzle_done[0]&&!shard_taken[0]){rect(238-p,77-p,34+p*2,39+p*2,34,70,95);rect(244,84,22,25,92,205,235);}
    }else if(room==1){
        /* Backward Street: reverse rain, neon pulses and restored switch circuit. */
        for(i=0;i<10;i++){int x=(i*37+anim_tick)%330-5,y=196-((anim_tick*2+i*19)%118);rect(x,y,1,7,92,132,188);}
        rect(18,86,42,3,115+p*18,45,120+p*10);rect(245,72,52,3,55,100+p*18,145+p*15);
        if(switch_a)rect(66,183,22,2,75,225,120);if(switch_b)rect(264,103,22,2,75,225,120);
        if(puzzle_done[1])rect(72,199,196,2,70,190,205);
    }else if(room==2){
        /* House Without Morning: windows gradually regain dawn after the puzzle. */
        for(i=0;i<4;i++){int x=33+i*76;if(puzzle_done[2]){rect(x,104,35,2,220,185,112);rect(x+4,108,27,1,170,145,92);}else rect(x,104,35,2,54,83,78);}
        if(puzzle_done[2]){rect(0,60,320,3,95+p*12,72+p*9,62);rect(148,64,24+p*4,2,210,164,92);}
        for(i=0;i<5;i++){int x=(i*63+anim_tick/2)%320;rect(x,78+((i*23+anim_tick/4)%110),2,2,110,155,130);}
    }else if(room==3){
        /* Clockworks: layered moving gear teeth and electrical sparks. */
        for(i=0;i<6;i++){int x=10+i*52,y=67+((i&1)*92);rect(x+((anim_tick/8+i)&3),y,24,3,170,105,35);rect(x+8,y-4,3,11,115,72,25);}
        if((anim_tick%34)<8){int x=92+(anim_tick*7)%145;rect(x,125,2,9,245,185,65);rect(x-4,130,10,2,235,130,45);}
        if(puzzle_done[3]){rect(42,203,236,3,205,135,38);rect(154-p,68-p,12+p*2,12+p*2,110,75,25);}
    }else{
        /* Clock Chamber: concentric time rings react to the Warden phase. */
        int q=(anim_tick/5)&7;
        rect(96-q,62-q,128+q*2,2,88,38,72);rect(96-q,174+q,128+q*2,2,88,38,72);
        rect(92-q,66,2,106,88,38,72);rect(226+q,66,2,106,88,38,72);
        if(finale.phase==FINALE_STABILIZE){rect(34,64,252,2,175+p*12,55,82);rect(34,202,252,2,175+p*12,55,82);}
        if(finale.stability>50){rect(153-p,108-p,14+p*2,14+p*2,80,185,220);rect(157,112,6,6,205,245,255);}
    }
}
'''

src = src.replace(anchor, helpers + anchor, 1)

hooks = [
    ('room_art();hud();cinematic_area_art(n);', 'room_art();runtime_world_fx_art();hud();cinematic_area_art(n);'),
    ('room_art();hud();boss_intro_art(n);', 'room_art();runtime_world_fx_art();hud();boss_intro_art(n);'),
    ('update_play(n);cinematic_detect();room_art();hud();', 'update_play(n);cinematic_detect();room_art();runtime_world_fx_art();hud();'),
]
for old,new in hooks:
    if old not in src:
        raise SystemExit('runtime world fx play hook missing: ' + old)
    src = src.replace(old,new,1)

marker = 'TITLE REV 268  COMPASS REV 265'
if marker not in src:
    raise SystemExit('runtime world fx title marker anchor missing')
src = src.replace(marker, 'TITLE REV 268  WORLD FX REV 270', 1)

pathlib.Path(sys.argv[2]).write_text(src)
