import pathlib, sys

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
    else if(best>=0&&d)FntPrint(font_id,"\nCOMPASS: %s  DIST %d",d->name,bestd);
    else if(room<4)FntPrint(font_id,"\nAREA MEMORY STABLE - FIND THE EXIT");
    else FntPrint(font_id,"\nOBJECTIVE: HOLD THE LOST HOUR");
    FntPrint(font_id,"\nMEMORIES %d/4  EVENTS %d  AP %d",shards,adventure.world.interactions,adventure.quests.ap);
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

src = src.replace('AUDIO REV 264','COMPASS REV 265',1)
src = src.replace('A264 %02d:%02d','O265 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
