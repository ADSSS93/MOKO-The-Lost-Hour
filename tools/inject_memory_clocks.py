import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Runtime state: each story room grants one full restorative charge.
needle = 'static int clock_guard=0,clock_guard_flash=0;'
replacement = needle + 'static uint8_t memory_clock_used[4]={0};static int memory_clock_notice=0;'
if needle not in src: raise SystemExit('memory clock globals anchor missing')
src = src.replace(needle, replacement, 1)

# New games reset restorative charges. Continue reconstructs them conservatively from shard progress.
needle = 'clock_guard=0;clock_guard_flash=0;area_banner=100;'
replacement = 'clock_guard=0;clock_guard_flash=0;memory_clock_notice=0;for(i=0;i<4;i++)memory_clock_used[i]=0;area_banner=100;'
if needle not in src: raise SystemExit('memory clock reset anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'for(i=0;i<4;i++)if(echo_seen[i])gameplay_record_echo(&gameplay);adventure_reset(&adventure);'
replacement = 'for(i=0;i<4;i++){if(echo_seen[i])gameplay_record_echo(&gameplay);memory_clock_used[i]=shard_taken[i]?1:0;}adventure_reset(&adventure);'
if needle not in src: raise SystemExit('memory clock continue anchor missing')
src = src.replace(needle, replacement, 1)

# Visible in-world checkpoint: a purple clock pedestal that unlocks after the room puzzle is solved.
anchor = 'static void clock_guard_art(void)'
helper = r'''static int memory_clock_near(void){
    if(room<0||room>=4||!puzzle_done[room])return 0;
    return hit(px,py,12,18,28,159,46,49);
}
static void memory_clock_art(void){
    int p,cx=51,cy=174;
    if(room<0||room>=4||!puzzle_done[room])return;
    p=(anim_tick/6)&3;
    /* pedestal */
    rect(34,191,34,6,47,34,71);rect(39,185,24,7,69,46,101);rect(44,178,14,8,87,53,128);
    /* clock body */
    rect(cx-13,cy-13,26,26,38,24,65);rect(cx-10,cy-10,20,20,91,53,139);
    rect(cx-7,cy-7,14,14,20,16,34);rect(cx-1,cy-6,3,8,235,193,103);rect(cx,cy,7,3,235,193,103);
    /* ears make the shrine echo Moko's cat silhouette */
    rect(cx-11,cy-17,6,6,86,47,132);rect(cx+5,cy-17,6,6,86,47,132);
    if(!memory_clock_used[room]){
        rect(cx-15-p,cy-15-p,30+p*2,2,112,72,208);rect(cx-15-p,cy+13+p,30+p*2,2,112,72,208);
        rect(cx-15-p,cy-13,2,26,112,72,208);rect(cx+13+p,cy-13,2,26,112,72,208);
    }else{
        rect(cx-2,cy+17,5,3,72,185,198);
    }
}
static int memory_clock_interact(void){
    int restored=0;
    if(!memory_clock_near())return 0;
    if(room>=0&&room<4&&!memory_clock_used[room]){
        memory_clock_used[room]=1;
        if(health<3){health=3;restored=1;}
        if(gameplay.focus<100){gameplay.focus=100;restored=1;}
        if(timer_frames<60*60*5){timer_frames+=600;if(timer_frames>60*60*5)timer_frames=60*60*5;restored=1;}
        score+=50;gameplay_reward(&gameplay,50);
        memory_clock_notice=180;sfx(0x2f00);
    }else{
        memory_clock_notice=120;sfx(0x1900);
    }
    persist_here();
    return restored?2:1;
}
'''
if anchor not in src: raise SystemExit('memory clock draw insertion anchor missing')
src = src.replace(anchor, helper + anchor, 1)

# Draw shrine in the actual room rendering before Moko.
needle = 'clock_guard_art();draw_moko();delivery_art();combat_art();encounter_art();}'
replacement = 'memory_clock_art();clock_guard_art();draw_moko();delivery_art();combat_art();encounter_art();}'
if needle not in src: raise SystemExit('memory clock room render anchor missing')
src = src.replace(needle, replacement, 1)

# Cross interaction is consumed by the shrine before generic world interactions.
needle = 'static void interact(uint16_t n){int reward;if(!pressed(n,PAD_CROSS))return;memory_echo(n);'
replacement = 'static void interact(uint16_t n){int reward;if(!pressed(n,PAD_CROSS))return;if(memory_clock_interact())return;memory_echo(n);'
if needle not in src: raise SystemExit('memory clock interact anchor missing')
src = src.replace(needle, replacement, 1)

# Tick notice duration with the existing frame state.
needle = 'anim_tick++;if(area_banner>0)area_banner--;if(save_notice>0)save_notice--;}'
replacement = 'anim_tick++;if(area_banner>0)area_banner--;if(save_notice>0)save_notice--;if(memory_clock_notice>0)memory_clock_notice--;}'
if needle not in src: raise SystemExit('memory clock notice anchor missing')
src = src.replace(needle, replacement, 1)

# HUD prompt and clear feedback make the mechanic discoverable without documentation.
needle = 'if(save_notice>0)FntPrint(font_id,"\\nMEMORY CARD: %s",moko_memcard_available()?"PROGRESS SAVED":"SAVE FAILED");'
replacement = 'if(memory_clock_near())FntPrint(font_id,"\\nCROSS - REST AT MEMORY CLOCK");if(memory_clock_notice>0)FntPrint(font_id,"\\nMEMORY CLOCK: %s",memory_clock_used[room]?"TIME RESTORED + SAVED":"CHECKPOINT SAVED");if(save_notice>0)FntPrint(font_id,"\\nMEMORY CARD: %s",moko_memcard_available()?"PROGRESS SAVED":"SAVE FAILED");'
if needle not in src: raise SystemExit('memory clock HUD anchor missing')
src = src.replace(needle, replacement, 1)

# Visible revision marker for emulator/BIN verification.
src = src.replace('GUARD REV 257','CLOCK REV 258',1)
src = src.replace('G257 %02d:%02d','C258 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
