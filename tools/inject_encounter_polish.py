import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Bind the combat/world runtime to the real adventure state. The runtime already
# advances quests 48..52 and challenge notices, but without this binding those
# events cannot update the active Adventure instance.
needle = 'adventure_reset(&adventure);world_runtime_reset(&living,0);'
replacement = 'adventure_reset(&adventure);world_runtime_reset(&living,0);world_runtime_bind_adventure(&adventure);'
count = src.count(needle)
if count < 2:
    raise SystemExit(f'adventure/runtime bind anchors missing: {count}')
src = src.replace(needle, replacement)

anchor = 'static void room_art(void)'
helpers = r'''static void encounter_art(void){
    int left=world_runtime_room_remaining(&living,room),pulse=(anim_tick/7)&3,i;
    if(room>=4)return;
    /* A compact combat radar makes active enemies readable without a minimap. */
    rect(244,66,66,11,9,10,23);
    for(i=0;i<left&&i<6;i++){
        int x=249+i*9;
        rect(x,69,6,5,105,42,92);
        rect(x+1,70,4,3,225,75,176);
    }
    if(left==0){
        /* Room-clear temporal seal: visibly confirms the challenge reward. */
        rect(255-pulse,78-pulse,38+pulse*2,38+pulse*2,18,55,70);
        rect(261,84,26,26,53,173,190);
        rect(267,90,14,14,14,25,42);
        rect(272,92,3,8,235,205,105);
        rect(273,98,7,3,235,205,105);
        for(i=0;i<4;i++)rect(258+i*9,119-((anim_tick/6+i)&3),5,3,80,220,235);
    }
}
static const char*encounter_text(void){
    int left;
    if(room>=4)return "";
    left=world_runtime_room_remaining(&living,room);
    if(left<=0)return "AREA SECURED - TIME MEMORY RESTORED";
    if(left==1)return "THREAT: 1 MEMORY CREATURE";
    return "THREATS REMAIN";
}
'''
if anchor not in src:
    raise SystemExit('encounter room_art anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

needle = 'draw_moko();delivery_art();combat_art();}'
replacement = 'draw_moko();delivery_art();combat_art();encounter_art();}'
if needle not in src:
    raise SystemExit('encounter render anchor missing')
src = src.replace(needle, replacement, 1)

# Show encounter state in the actual HUD. For 2+ enemies include the exact
# count so the player can tell when an area is nearly secured.
needle = 'if(combat_rank()[0])FntPrint(font_id,"\\n%s x%d",combat_rank(),gameplay.combo);if(combat_notice>0)FntPrint(font_id,"  +3 SEC");if(ni>=0)'
replacement = 'if(combat_rank()[0])FntPrint(font_id,"\\n%s x%d",combat_rank(),gameplay.combo);if(combat_notice>0)FntPrint(font_id,"  +3 SEC");if(encounter_text()[0]){int er=world_runtime_room_remaining(&living,room);if(er>1)FntPrint(font_id,"\\n%s: %d",encounter_text(),er);else FntPrint(font_id,"\\n%s",encounter_text());}if(ni>=0)'
if needle not in src:
    raise SystemExit('encounter HUD anchor missing')
src = src.replace(needle, replacement, 1)

# Make the revision unmistakable in emulator captures.
src = src.replace('COMBAT REV 255','ENCOUNTER REV 256',1)
src = src.replace('C255 %02d:%02d','E256 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
