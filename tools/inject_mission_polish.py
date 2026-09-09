import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

anchor = 'static void room_art(void)'
helpers = r'''static void objective_marker(int x,int y,int r,int g,int b){int p=2+((anim_tick/6)&3);rect(x-p,y-p,10+p*2,10+p*2,r/3,g/3,b/3);rect(x,y,10,10,r,g,b);rect(x+3,y+3,4,4,240,245,255);}
static void mission_art(void){
    int i;
    if(room==0){
        if(!puzzle_done[0])objective_marker(116,168,235,190,70);
        else if(!shard_taken[0])objective_marker(250,90,80,225,245);
    }else if(room==1){
        if(!switch_a)objective_marker(70,181,230,80,125);
        if(!switch_b)objective_marker(269,106,230,80,125);
        if(puzzle_done[1]&&!shard_taken[1])objective_marker(215,118,80,225,245);
    }else if(room==2){
        if(!puzzle_done[2])objective_marker(196,92,110,235,195);
        else if(!shard_taken[2])objective_marker(180,146,80,225,245);
    }else if(room==3){
        if(!puzzle_done[3])objective_marker(158,91,245,160,55);
        else if(!shard_taken[3])objective_marker(145,174,80,225,245);
    }else{
        if(shards>=4&&finale.phase==FINALE_RESTORE){for(i=0;i<4;i++)if(!finale.socket[i])objective_marker(110+i*28,151,95,230,245);}
        if(finale.phase==FINALE_STABILIZE&&!finale_complete(&finale))objective_marker(finale.warden_x,finale.warden_y,235,70,105);
    }
    if(room<4&&shard_taken[room]){int pulse=(anim_tick/8)&3;rect(304-pulse,91-pulse,12+pulse*2,54+pulse*2,20,70,90);rect(308,95,8,46,70,210,230);}
}
static const char* mission_text(void){
    if(room==0)return !puzzle_done[0]?"OBJECTIVE: WAKE THE STATION CLOCK":(!shard_taken[0]?"OBJECTIVE: TAKE MEMORY SHARD":"OBJECTIVE: EXIT RIGHT");
    if(room==1)return !puzzle_done[1]?"OBJECTIVE: ACTIVATE BOTH TIME SWITCHES":(!shard_taken[1]?"OBJECTIVE: TAKE MEMORY SHARD":"OBJECTIVE: EXIT RIGHT");
    if(room==2)return !puzzle_done[2]?"OBJECTIVE: CROSS THE IMPOSSIBLE HOUSE":(!shard_taken[2]?"OBJECTIVE: TAKE MEMORY SHARD":"OBJECTIVE: EXIT RIGHT");
    if(room==3)return !puzzle_done[3]?"OBJECTIVE: DASH THROUGH THE CLOCKWORK CORE":(!shard_taken[3]?"OBJECTIVE: TAKE MEMORY SHARD":"OBJECTIVE: ENTER CLOCK CHAMBER");
    if(shards<4)return "OBJECTIVE: FOUR SHARDS REQUIRED";
    if(finale.phase==FINALE_RESTORE)return "OBJECTIVE: RESTORE THE FOUR CLOCK SOCKETS";
    if(finale.phase==FINALE_STABILIZE)return "OBJECTIVE: DASH INTO THE HOUR WARDEN";
    return "OBJECTIVE: HOLD THE LOST HOUR";
}
static void hud_vitals(void){int i;for(i=0;i<3;i++){int on=i<health;rect(8+i*11,55,8,6,on?220:45,on?55:35,on?95:45);}rect(46,55,54,5,25,35,55);rect(47,56,(gameplay.focus*52)/100,3,75,215,235);}
'''
if anchor not in src: raise SystemExit('room_art anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

needle = 'world_event_art();echo_art();if(room<4&&!shard_taken[room]&&puzzle_done[room])draw_shard(250-room*35,90+room*28);draw_moko();}'
replacement = 'world_event_art();echo_art();mission_art();if(room<4&&!shard_taken[room]&&puzzle_done[room])draw_shard(250-room*35,90+room*28);draw_moko();}'
if needle not in src: raise SystemExit('room art body anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'static void hud(void){static const char*n[]={'
replacement = 'static void hud(void){hud_vitals();static const char*n[]={'
if needle not in src: raise SystemExit('hud anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'FntPrint(font_id,"%02d:%02d S%d/4 HP%d SCORE%d FOCUS%d\\n%s R1:DASH SELECT:JOURNAL EV%d%%",'
if needle not in src:
    needle = 'FntPrint(font_id,"S252 %02d:%02d S%d/4 HP%d SCORE%d FOCUS%d\\n%s R1:DASH SELECT:JOURNAL EV%d%%",'
    replacement = 'FntPrint(font_id,"M253 %02d:%02d S%d/4 HP%d SCORE%d FOCUS%d\\n%s R1:DASH SELECT:JOURNAL EV%d%%\\n%s",'
else:
    replacement = 'FntPrint(font_id,"M253 %02d:%02d S%d/4 HP%d SCORE%d FOCUS%d\\n%s R1:DASH SELECT:JOURNAL EV%d%%\\n%s",'
if needle not in src: raise SystemExit('hud text anchor missing')
src = src.replace(needle, replacement, 1)

needle = 's/60,s%60,shards,health,score,gameplay.focus,n[room],adventure_completion(&adventure));'
replacement = 's/60,s%60,shards,health,score,gameplay.focus,n[room],adventure_completion(&adventure),mission_text());'
if needle not in src: raise SystemExit('hud args anchor missing')
src = src.replace(needle, replacement, 1)

src = src.replace('SAVE REV 252', 'MISSION REV 253', 1)

pathlib.Path(sys.argv[2]).write_text(src)
