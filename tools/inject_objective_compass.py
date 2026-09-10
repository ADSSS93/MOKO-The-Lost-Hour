import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

if 'AUDIO REV 264' not in src:
    raise SystemExit('objective compass revision anchor missing')

anchor = 'static int warden_phase_level(void)'
helpers = r'''static void objective_compass_art(void){
    int i,best=-1,bestd=9999,dx=0,dy=0,p=(anim_tick/8)&3;
    const MokoWorldEventDef*d=0;
    /* Find the closest real, unlocked objective/event in the current playable room. */
    for(i=0;i<MOKO_WORLD_EVENT_COUNT;i++){
        const MokoWorldEventDef*e=adventure_event(&adventure,i);
        int ex,ey,dist;
        if(!e||e->room!=room||adventure.world.collected[i])continue;
        if(!world_event_unlocked(&adventure.world,&adventure.quests,i))continue;
        ex=e->x-px;ey=e->y-py;dist=(ex<0?-ex:ex)+(ey<0?-ey:ey);
        if(dist<bestd){bestd=dist;best=i;dx=ex;dy=ey;d=e;}
    }
    /* PS1-style temporal compass: always visible, but driven by live world state. */
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
    /* Route strip: four memories feeding the final Clock Chamber. */
    rect(12,60,102,12,10,13,27);
    for(i=0;i<5;i++){
        int lit=(i<4)?shard_taken[i]:(room==4);
        rect(17+i*19,64,10,4,lit?116:39,lit?184:47,lit?211:69);
        if(i<4&&!shard_taken[i]&&room==i)rect(15+i*19,62,14,8,99+p*18,48,135);
    }
    /* Context objective text uses actual puzzle/shard/event progression. */
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
    /* Dawn physically returns to the five-area world after the Warden falls. */
    rect(0,0,320,240,10+(epilogue_tick<150?epilogue_tick/15:10),20+(epilogue_tick<150?epilogue_tick/10:15),34+(epilogue_tick<150?epilogue_tick/8:20));
    rect(0,170,320,70,31,45,56);rect(0,202,320,38,53,50,65);
    for(i=0;i<7;i++){int x=(i*53+ray)%340-10;rect(x,28+(i&1)*11,34,2,94,83,130);}
    /* Restored station/clock silhouettes reuse the game's visual language. */
    rect(25,125,58,45,37,57,72);rect(31,132,46,30,66,92,105);
    rect(238,113,54,57,46,36,58);rect(247,122,36,40,95,70,118);
    epilogue_clock(160,98,38,epilogue_tick);
    for(i=0;i<4;i++){int x=116+i*29;rect(x,151,17,5,34,79,90);rect(x+3,148-p,11,5+p,93,217,230);}
    /* Moko stands in the restored hour; sprite keeps the purple cat/clock identity. */
    moko_sprite_draw(154,170,1,(epilogue_tick/5)&7,0,epilogue_tick,db[active].ot,&next_packet);
    rect(171,181,13+p,3,184,88,218);rect(181+p,178,3,8,224,181,245);
}
static void restored_time_credits_art(void){
    int i,y,scroll=(epilogue_tick/2)%520;
    rect(0,0,320,240,5,6,14);
    for(i=0;i<18;i++){int x=(i*73+epilogue_tick/4)%320,y2=(i*41+epilogue_tick/7)%220;rect(x,y2,2,2,79+(i&1)*45,69,122);}
    epilogue_clock(160,62,25,epilogue_tick);
    y=238-scroll;
    if(y>-100&&y<250)FntPrint(journal_font_id,"\n\n\n\n\n\n\n\n\n\n MOKO: THE LOST HOUR\n\n TIME RESTORED\n\n GAME DESIGN & DEVELOPMENT\n ADSSS93\n\n MOKO - PURPLE CAT OF THE LOST HOUR\n\n MEMORY SHARDS RECOVERED  %d/4\n ADVENTURE COMPLETION     %d%%\n FINAL SCORE              %d\n BEST COMBO               x%d\n\n THE SILENT STATION REMEMBERS.\n THE RAIN FALLS THE RIGHT WAY.\n MORNING RETURNS TO THE HOUSE.\n THE CLOCKWORKS MOVE AGAIN.\n\n THANK YOU FOR REMEMBERING.\n\n START - TITLE",shards,adventure_completion(&adventure),score,gameplay.best_combo);
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

# Reset the epilogue animation on the real Hour Warden completion transition.
ending_transition = 'sfx(0x2f00);state=STATE_ENDING;'
if ending_transition not in src:
    raise SystemExit('epilogue transition anchor missing')
src = src.replace(ending_transition, 'sfx(0x2f00);epilogue_tick=0;state=STATE_ENDING;', 1)

# Replace the old text-only ending with a staged, visible restored-time scene.
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
src, count = ending_pattern.subn(ending_replacement, src, count=1)
if count != 1:
    raise SystemExit('text-only ending anchor missing')

# Credits are now animated and carry real completion statistics.
credits_pattern = re.compile(r'}else\{rect\(0,0,320,240,4,4,10\);FntPrint\(font_id,".*?START - TITLE"\);FntFlush\(font_id\);if\(pressed\(n,PAD_START\)\)state=STATE_TITLE;\}', re.S)
credits_replacement = r'''}else{
    epilogue_tick++;restored_time_credits_art();FntFlush(journal_font_id);
    FntPrint(font_id,"EPILOGUE REV 266");FntFlush(font_id);
    if(pressed(n,PAD_START)){epilogue_tick=0;state=STATE_TITLE;}
}'''
src, count = credits_pattern.subn(credits_replacement, src, count=1)
if count != 1:
    raise SystemExit('credits anchor missing')

src = src.replace('AUDIO REV 264','COMPASS REV 265',1)
src = src.replace('A264 %02d:%02d','O265 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)