import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

if 'AUDIO REV 264' not in src:
    raise SystemExit('objective compass revision anchor missing')

anchor = 'static int warden_phase_level(void)'
helpers = r'''static void objective_compass_art(void){
    int i,best=-1,bestd=9999,dx=0,dy=0,p=(anim_tick/8)&3;
    const MokoWorldEventDef*d=0;
    for(i=0;i<MOKO_WORLD_EVENT_COUNT;i++){
        const MokoWorldEventDef*e=adventure_event(&adventure,i);
        int ex,ey,dist;
        if(!e||e->room!=room||adventure.world.collected[i])continue;
        if(!world_event_unlocked(&adventure.world,&adventure.quests,i))continue;
        ex=e->x-px;ey=e->y-py;dist=(ex<0?-ex:ex)+(ey<0?-ey:ey);
        if(dist<bestd){bestd=dist;best=i;dx=ex;dy=ey;d=e;}
    }
    rect(258,62,56,28,12,16,31);rect(260,64,52,24,28,25,52);
    rect(284,68,3,15,103,72,142);rect(278,74,15,3,103,72,142);
    rect(284-p,74-p,3+p*2,3+p*2,186,91,232);
    if(best>=0){
        if((dx<0?-dx:dx)>(dy<0?-dy:dy)){
            if(dx<0){rect(266,74,10,3,224,181,245);rect(266,71,3,9,224,181,245);}
            else{rect(295,74,10,3,224,181,245);rect(302,71,3,9,224,181,245);}
        }else{
            if(dy<0){rect(284,65,3,8,224,181,245);rect(281,65,9,3,224,181,245);}
            else{rect(284,79,3,8,224,181,245);rect(281,84,9,3,224,181,245);}
        }
    }
    rect(12,60,102,12,10,13,27);
    for(i=0;i<5;i++){
        int lit=(i<4)?shard_taken[i]:(room==4);
        rect(17+i*19,64,10,4,lit?116:39,lit?184:47,lit?211:69);
        if(i<4&&!shard_taken[i]&&room==i)rect(15+i*19,62,14,8,99+p*18,48,135);
    }
    if(room<4&&!puzzle_done[room]){
        if(room==0)FntPrint(font_id,"\nOBJECTIVE: RESTORE THE STATION SIGNAL");
        else if(room==1)FntPrint(font_id,"\nOBJECTIVE: ACTIVATE BOTH RED SWITCHES");
        else if(room==2)FntPrint(font_id,"\nOBJECTIVE: OPEN THE MORNING ROOM");
        else FntPrint(font_id,"\nOBJECTIVE: RESTART THE CENTRAL GEAR");
    }else if(room<4&&!shard_taken[room])FntPrint(font_id,"\nOBJECTIVE: CLAIM THE MEMORY SHARD");
    else if(best>=0&&d)FntPrint(font_id,"\nCOMPASS: %s  DIST %d",d->label,bestd);
    else if(room<4)FntPrint(font_id,"\nAREA MEMORY STABLE - FIND THE EXIT");
    else FntPrint(font_id,"\nOBJECTIVE: HOLD THE LOST HOUR");
    FntPrint(font_id,"\nMEMORIES %d/4  EVENTS %d  AP %d",shards,adventure.world.interactions,adventure.quests.ap);
}
static int pause_tab=0;
static const char*pause_area_name(void){
    static const char*n[]={"SILENT STATION","BACKWARD STREET","HOUSE WITHOUT MORNING","CLOCKWORKS","CLOCK CHAMBER"};
    return n[room];
}
static void pause_objective_text(void){
    int near=adventure_near_event(&adventure,room,px,py,999);
    if(room<4&&!puzzle_done[room]){
        if(room==0)FntPrint(journal_font_id,"Restore the station signal.");
        else if(room==1)FntPrint(journal_font_id,"Activate both red switches.");
        else if(room==2)FntPrint(journal_font_id,"Open the Morning Room.");
        else FntPrint(journal_font_id,"Restart the Central Gear.");
    }else if(room<4&&!shard_taken[room])FntPrint(journal_font_id,"Claim the Memory Shard.");
    else if(near>=0){const MokoWorldEventDef*d=adventure_event(&adventure,near);if(d)FntPrint(journal_font_id,"Follow memory: %s",d->label);}
    else if(room<4)FntPrint(journal_font_id,"Memory stable. Find the exit.");
    else FntPrint(journal_font_id,"Survive the Hour Warden.");
}
static void pause_menu_art(void){
    int i,p=(anim_tick/10)&3,complete=adventure_completion(&adventure);
    rect(12,20,296,204,4,7,17);rect(16,24,288,26,18,24,45);rect(16,54,288,166,9,12,27);
    rect(21+pause_tab*92,47,78,4,126,71,173);
    for(i=0;i<4;i++){int x=224+i*17;rect(x,30,12,12,24,48,62);if(shard_taken[i]){rect(x+2,32,8,8,85,211,233);rect(x+4,30-p,4,3+p,183,246,251);}}
    FntPrint(journal_font_id,"PAUSE  |  STATUS     CONTROLS     MEMORY\n\n");
    if(pause_tab==0){
        FntPrint(journal_font_id,"AREA  %s\n\nOBJECTIVE\n",pause_area_name());pause_objective_text();
        FntPrint(journal_font_id,"\n\nHP %d/3     FOCUS %d/100\nSHARDS %d/4  SCORE %d\nEVENTS %d%%   AP %d\nBEST COMBO x%d",health,gameplay.focus,shards,score,complete,adventure.quests.ap,gameplay.best_combo);
        rect(35,184,250,7,28,31,49);rect(35,184,(250*complete)/100,7,84,173,193);
    }else if(pause_tab==1){
        FntPrint(journal_font_id,"CONTROLS\n\nD-PAD    MOVE MOKO\nCROSS    INTERACT / CONFIRM\nR1       MEMORY DASH\nSQUARE   CLOCK GUARD\nSELECT   MEMORY JOURNAL\nSTART    RESUME\n\nClock Guard slows time drain.\nMemory Dash breaks temporal threats.");
    }else{
        FntPrint(journal_font_id,"MEMORY MAP\n\n");
        for(i=0;i<4;i++){
            const char*name=i==0?"STATION":i==1?"STREET":i==2?"HOUSE":"CLOCKWORKS";
            FntPrint(journal_font_id,"%d  %-10s  SHARD %s  PUZZLE %s\n",i+1,name,shard_taken[i]?"YES":"--",puzzle_done[i]?"CLEAR":"OPEN");
        }
        FntPrint(journal_font_id,"\nCURRENT AREA EVENTS LEFT %d\nTOTAL COMPLETION %d%%\n\nFour memories unlock the Clock Chamber.",world_events_remaining(&adventure.world,room),complete);
    }
    FntPrint(journal_font_id,"\n\nLEFT/RIGHT TAB   SELECT JOURNAL\nSTART/CIRCLE RESUME   PAUSE REV 267");
}
static int epilogue_tick=0;
static void epilogue_clock(int cx,int cy,int radius,int tick){
    int hand=(tick/14)&7;
    rect(cx-radius,cy-radius,radius*2,radius*2,19,38,55);
    rect(cx-radius+4,cy-radius+4,radius*2-8,radius*2-8,93,67,132);
    rect(cx-radius+8,cy-radius+8,radius*2-16,radius*2-16,17,25,39);
    rect(cx-2,cy-2,5,5,236,205,123);
    if(hand==0){rect(cx,cy-radius+8,3,radius-8,224,181,245);}
    else if(hand==1){rect(cx,cy,3,3,224,181,245);rect(cx+3,cy-radius/2,3,radius/2,224,181,245);}
    else if(hand==2){rect(cx,cy,radius-8,3,224,181,245);}
    else if(hand==3){rect(cx,cy,3,3,224,181,245);rect(cx+3,cy+3,3,radius/2,224,181,245);}
    else if(hand==4){rect(cx,cy,3,radius-8,224,181,245);}
    else if(hand==5){rect(cx-radius/2,cy+3,radius/2,3,224,181,245);}
    else if(hand==6){rect(cx-radius+8,cy,radius-8,3,224,181,245);}
    else{rect(cx-radius/2,cy-radius/2,radius/2,3,224,181,245);}
}
static void restored_time_epilogue_art(void){
    int i,p=(epilogue_tick/8)&3,ray=(epilogue_tick/3)%320;
    rect(0,0,320,240,10+(epilogue_tick<150?epilogue_tick/15:10),20+(epilogue_tick<150?epilogue_tick/10:15),34+(epilogue_tick<150?epilogue_tick/8:20));
    rect(0,170,320,70,31,45,56);rect(0,202,320,38,53,50,65);
    for(i=0;i<7;i++){int x=(i*53+ray)%340-10;rect(x,28+(i&1)*11,34,2,94,83,130);}
    rect(25,125,58,45,37,57,72);rect(31,132,46,30,66,92,105);
    rect(238,113,54,57,46,36,58);rect(247,122,36,40,95,70,118);
    epilogue_clock(160,98,38,epilogue_tick);
    for(i=0;i<4;i++){int x=116+i*29;rect(x,151,17,5,34,79,90);rect(x+3,148-p,11,5+p,93,217,230);}
    moko_sprite_draw(154,170,1,(epilogue_tick/5)&7,0,epilogue_tick,db[active].ot,&next_packet);
    rect(171,181,13+p,3,184,88,218);rect(181+p,178,3,8,224,181,245);
}
static void restored_time_credits_art(void){
    int i,scroll=(epilogue_tick/2)%520;
    rect(0,0,320,240,5,6,14);
    for(i=0;i<18;i++){int x=(i*73+epilogue_tick/4)%320,y2=(i*41+epilogue_tick/7)%220;rect(x,y2,2,2,79+(i&1)*45,69,122);}
    epilogue_clock(160,62,25,epilogue_tick);
    if(scroll<480)FntPrint(journal_font_id,"\n\n\n\n\n\n\n\n\n\n MOKO: THE LOST HOUR\n\n TIME RESTORED\n\n GAME DESIGN & DEVELOPMENT\n ADSSS93\n\n MOKO - PURPLE CAT OF THE LOST HOUR\n\n MEMORY SHARDS RECOVERED  %d/4\n ADVENTURE COMPLETION     %d%%\n FINAL SCORE              %d\n BEST COMBO               x%d\n\n THE SILENT STATION REMEMBERS.\n THE RAIN FALLS THE RIGHT WAY.\n MORNING RETURNS TO THE HOUSE.\n THE CLOCKWORKS MOVE AGAIN.\n\n THANK YOU FOR REMEMBERING.\n\n START - TITLE",shards,adventure_completion(&adventure),score,gameplay.best_combo);
}
'''
if anchor not in src:
    raise SystemExit('objective compass helper anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

needle = 'story_setpiece_art();world_event_art();echo_art();temporal_pickups();'
replacement = 'story_setpiece_art();objective_compass_art();world_event_art();echo_art();temporal_pickups();'
if needle not in src:
    raise SystemExit('objective compass room anchor missing')
src = src.replace(needle, replacement, 1)

ending_transition = 'sfx(0x2f00);state=STATE_ENDING;'
if ending_transition not in src:
    raise SystemExit('epilogue transition anchor missing')
src = src.replace(ending_transition, 'sfx(0x2f00);epilogue_tick=0;state=STATE_ENDING;', 1)

ending_pattern = re.compile(r'}else if\(state==STATE_ENDING\)\{.*?if\(pressed\(n,PAD_CROSS\)\)state=STATE_CREDITS;\}', re.S)
ending_replacement = r'''}else if(state==STATE_ENDING){
    epilogue_tick++;restored_time_epilogue_art();
    FntPrint(font_id,"\n EPILOGUE REV 266\n THE LOST HOUR RETURNS");
    if(epilogue_tick<150)FntPrint(font_id,"\n\n The Clock Chamber breathes again...");
    else if(epilogue_tick<300)FntPrint(font_id,"\n\n Four memories become one living hour.");
    else FntPrint(font_id,"\n\n Moko remembers. Time can move again.\n SCORE %d  EVENTS %d%%\n\n CROSS - CREDITS",score,adventure_completion(&adventure));
    FntFlush(font_id);
    if(epilogue_tick>=300&&pressed(n,PAD_CROSS)){epilogue_tick=0;sfx(0x2200);state=STATE_CREDITS;}
}'''
src, count = ending_pattern.subn(lambda _m: ending_replacement, src, count=1)
if count != 1:
    raise SystemExit('text-only ending anchor missing')

credits_pattern = re.compile(r'}else\{rect\(0,0,320,240,4,4,10\);FntPrint\(font_id,".*?START - TITLE"\);FntFlush\(font_id\);if\(pressed\(n,PAD_START\)\)state=STATE_TITLE;\}', re.S)
credits_replacement = r'''}else{
    epilogue_tick++;restored_time_credits_art();FntFlush(journal_font_id);
    FntPrint(font_id,"EPILOGUE REV 266");FntFlush(font_id);
    if(pressed(n,PAD_START)){epilogue_tick=0;state=STATE_TITLE;}
}'''
src, count = credits_pattern.subn(lambda _m: credits_replacement, src, count=1)
if count != 1:
    raise SystemExit('credits anchor missing')

pause_pattern = re.compile(r'}else if\(state==STATE_PAUSE\)\{room_art\(\);.*?if\(pressed\(n,PAD_START\)\)state=STATE_PLAY;\}', re.S)
pause_replacement = r'''}else if(state==STATE_PAUSE){
    room_art();pause_menu_art();FntFlush(journal_font_id);
    if(pressed(n,PAD_LEFT)){pause_tab=(pause_tab+2)%3;sfx(0x0d00);}
    if(pressed(n,PAD_RIGHT)){pause_tab=(pause_tab+1)%3;sfx(0x0d00);}
    if(pressed(n,PAD_SELECT)){adventure_journal_sync(&adventure);state=STATE_JOURNAL;sfx(0x1200);}
    if(pressed(n,PAD_START)||pressed(n,PAD_CIRCLE)){state=STATE_PLAY;sfx(0x0d00);}
}'''
src, count = pause_pattern.subn(lambda _m: pause_replacement, src, count=1)
if count != 1:
    raise SystemExit('pause menu anchor missing')

src = src.replace('AUDIO REV 264','COMPASS REV 265',1)
src = src.replace('A264 %02d:%02d','O265 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
