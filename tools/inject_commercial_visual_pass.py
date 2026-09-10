import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Final presentation pass: runs after all gameplay injectors so these changes
# are guaranteed to be the visuals that reach the PS1 executable.

station = r'''static void station_art(void){
    int i,p=(anim_tick/10)&3;
    /* Deep vaulted station: layered perspective instead of a wall of rectangles. */
    rect(0,58,320,164,7,10,22);
    tri(0,58,320,58,270,90,19,24,43);tri(0,58,270,90,42,90,11,16,32);
    tri(0,90,42,90,18,194,9,14,27);tri(320,90,270,90,302,194,10,15,28);
    /* Repeating iron arches give depth and scale. */
    for(i=0;i<5;i++){
        int x=20+i*68;
        tri(x,194,x+8,194,x+18,83,34,40,58);tri(x+48,194,x+56,194,x+38,83,34,40,58);
        tri(x+18,83,x+38,83,x+28,70,49,49,68);
        rect(x+10,91,36,2,85,76,94);
        rect(x+16,102,24,18,12,24,40);rect(x+19,105,18,12,34,65,82);
    }
    /* Distant platform canopy and glass strip. */
    tri(0,126,320,126,295,143,28,38,58);tri(0,126,295,143,24,143,16,25,43);
    for(i=0;i<8;i++){int x=10+i*42;rect(x,130,28,7,25,49,67);rect(x+3,131,22,4,48,92,108);}
    /* Main platform is a trapezoid, not a flat block. */
    tri(0,187,320,187,300,218,48,45,48);tri(0,187,300,218,20,218,31,31,38);
    rect(0,188,320,3,126,102,69);rect(0,216,320,3,78,67,55);
    /* Rails converge slightly to sell perspective. */
    tri(0,221,320,221,292,225,74,67,61);tri(0,228,320,228,300,231,40,43,49);
    for(i=0;i<13;i++){int x=i*27;tri(x,218,x+5,218,x+10,236,70,61,52);}
    /* Signal cabinet and station clock as readable landmarks. */
    rect(102,151,22,37,41,50,68);rect(106,155,14,20,21,38,51);rect(109,158,8,8,puzzle_done[0]?75:205,puzzle_done[0]?210:67,puzzle_done[0]?116:74);
    rect(151,103,20,20,32,35,51);rect(154,106,14,14,205,184,127);rect(160,108,2,6,36,29,38);rect(160,112,5,2,36,29,38);
    /* Pools of light and small props break the grid. */
    for(i=0;i<4;i++){int x=34+i*78;tri(x,94,x+14,94,x+27,184,28,38,51);tri(x+14,94,x+27,184,x+2,184,18,27,42);rect(x+9,90-p/2,10,4,207,175,102);}
    tri(238,178,270,178,277,187,42,64,74);tri(238,178,277,187,232,187,26,46,57);
}'''

pat = re.compile(r'static void station_art\(void\)\{.*?\}\nstatic void street_art', re.S)
if not pat.search(src):
    raise SystemExit('commercial visual pass: station_art not found')
src = pat.sub(station + '\nstatic void street_art', src, count=1)

scroll = r'''static void station_scroll_art(void){
    int i,p=(anim_tick/12)&3;
    if(room!=0)return;
    rect(320,58,320,164,6,10,22);
    tri(320,58,640,58,594,91,20,24,42);tri(320,58,594,91,352,91,10,16,31);
    /* Grand concourse arches continue the visual language of the first half. */
    for(i=0;i<5;i++){
        int x=332+i*62;
        tri(x,194,x+7,194,x+18,82,35,40,57);tri(x+43,194,x+50,194,x+33,82,35,40,57);
        tri(x+18,82,x+33,82,x+25,70,52,49,66);
        rect(x+12,101,32,2,79,72,89);
    }
    /* Long train with tapered nose and lit windows. */
    tri(350,139,562,139,580,181,35,42,57);tri(350,139,580,181,344,181,24,31,45);
    tri(562,139,594,157,580,181,48,53,66);
    for(i=0;i<6;i++){int x=362+i*33;rect(x,146,23,14,12,25,39);rect(x+3,149,17,8,55,104,119);}
    rect(350,165,225,3,101,82,70);rect(356,174,214,2,56,57,61);
    /* Overhead bridge/catwalk with diagonal braces. */
    tri(338,113,533,113,522,123,57,65,83);tri(338,113,522,123,348,123,34,42,60);
    for(i=0;i<5;i++){int x=350+i*42;tri(x,123,x+4,123,x+21,145,45,52,68);tri(x+21,145,x+25,145,x+42,123,31,39,55);}
    /* Lamps and exit gate. */
    for(i=0;i<5;i++){int x=340+i*54;rect(x,91,3,96,42,45,58);tri(x-8,91,x+11,91,x+2,80,62,57,70);rect(x-4,88-p/2,12,4,205,170,96);}
    tri(585,116,624,116,620,190,57,48,60);tri(585,116,620,190,590,190,36,34,48);
    rect(596,128,18,18,15,31,43);rect(601,133,8,8,shard_taken[0]?65:188,shard_taken[0]?214:64,shard_taken[0]?121:76);
    /* Same perspective platform/rail treatment across the scroll boundary. */
    tri(320,187,640,187,620,218,48,45,48);tri(320,187,620,218,340,218,31,31,38);
    rect(320,188,320,3,126,102,69);rect(320,216,320,3,78,67,55);
    tri(320,221,640,221,612,225,74,67,61);tri(320,228,640,228,620,231,40,43,49);
}'''
pat = re.compile(r'static void station_scroll_art\(void\)\{.*?\}\nstatic void camera_tick', re.S)
if not pat.search(src):
    raise SystemExit('commercial visual pass: station_scroll_art not found')
src = pat.sub(scroll + '\nstatic void camera_tick', src, count=1)

# Replace the giant debug-like HUD with a compact two-line gameplay HUD.
hud = r'''static void hud(void){
    static const char*n[]={"SILENT STATION","BACKWARD STREET","HOUSE WITHOUT MORNING","CLOCKWORKS","CLOCK CHAMBER"};
    int s=timer_frames/60,near=adventure_near_event(&adventure,room,px,py,24),ni=npc_near(room,px,py,24),i;
    /* Small top-left status cluster: hearts, shards and time. */
    for(i=0;i<3;i++){rect(9+i*12,8,9,7,i<health?208:48,i<health?55:35,i<health?91:48);rect(11+i*12,6,5,3,i<health?232:52,i<health?79:38,i<health?113:52);}
    for(i=0;i<4;i++){int c=i<shards?215:52;tri(52+i*9,7,56+i*9,11,52+i*9,15,c,i<shards?181:50,i<shards?94:58);tri(52+i*9,15,48+i*9,11,52+i*9,7,c,i<shards?181:50,i<shards?94:58);}
    FntPrint(font_id,"%s   %02d:%02d   FOCUS %d",n[room],s/60,s%60,gameplay.focus);
    if(ni>=0){const MokoNpcDef*p=npc_get(ni);if(p)FntPrint(font_id,"\nCROSS  TALK  %s",p->name);}
    else if(near>=0){const MokoWorldEventDef*d=adventure_event(&adventure,near);if(d)FntPrint(font_id,"\nCROSS  %s",d->label);}
    else if(adventure.notice_timer>0)FntPrint(font_id,"\nEVENT CLEAR  %s",adventure_notice(&adventure));
    FntFlush(font_id);
}'''
pat = re.compile(r'static void hud\(void\)\{.*?\}\nstatic void draw_journal', re.S)
if not pat.search(src):
    raise SystemExit('commercial visual pass: hud not found')
src = pat.sub(hud + '\nstatic void draw_journal', src, count=1)

# Tutorial becomes a small bottom prompt instead of a full-width debug panel.
pat = re.compile(r'static void tutorial_art\(void\)\{.*?\}\nstatic int warden_phase_level', re.S)
if pat.search(src):
    tutorial = r'''static void tutorial_art(void){
    int step=-1;
    if(tutorial_flags==15||room>0)return;
    if(!(tutorial_flags&1))step=0;else if(!(tutorial_flags&2))step=1;else if(!(tutorial_flags&4))step=2;else if(!(tutorial_flags&8))step=3;
    if(step<0)return;
    rect(68,207,184,21,4,7,16);rect(72,211,176,13,16,20,34);
    if(step==0)FntPrint(font_id,"\n\n\n\n\n\n\n\n\n\n\n\n        D-PAD  MOVE");
    else if(step==1)FntPrint(font_id,"\n\n\n\n\n\n\n\n\n\n\n\n        CROSS  INTERACT / JUMP");
    else if(step==2)FntPrint(font_id,"\n\n\n\n\n\n\n\n\n\n\n\n        R1  MEMORY DASH");
    else FntPrint(font_id,"\n\n\n\n\n\n\n\n\n\n\n\n        SQUARE  CLOCK GUARD");
}'''
    src = pat.sub(tutorial + '\nstatic int warden_phase_level', src, count=1)

# Marker is intentionally rendered nowhere; CI searches generated source.
src += '\n/* COMMERCIAL VISUAL REV 283: compact HUD + rebuilt Silent Station */\n'

pathlib.Path(sys.argv[2]).write_text(src)
