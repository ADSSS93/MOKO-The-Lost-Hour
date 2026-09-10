import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# A mid-game miniboss closes the gap between ordinary encounters and the Hour Warden.
needle = 'static uint8_t memory_clock_used[4]={0};static int memory_clock_notice=0;'
replacement = needle + 'static int sentinel_hp=4,sentinel_x=252,sentinel_dir=-1,sentinel_iframes=0,sentinel_defeated=0,sentinel_notice=0;'
if needle not in src: raise SystemExit('sentinel globals anchor missing')
src = src.replace(needle, replacement, 1)

# Reset on new game; Continue reconstructs defeat from possession of the Clockworks shard.
needle = 'memory_clock_notice=0;for(i=0;i<4;i++)memory_clock_used[i]=0;area_banner=100;'
replacement = 'memory_clock_notice=0;sentinel_hp=4;sentinel_x=252;sentinel_dir=-1;sentinel_iframes=0;sentinel_defeated=0;sentinel_notice=0;for(i=0;i<4;i++)memory_clock_used[i]=0;area_banner=100;'
if needle not in src: raise SystemExit('sentinel reset anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'for(i=0;i<4;i++){if(echo_seen[i])gameplay_record_echo(&gameplay);memory_clock_used[i]=shard_taken[i]?1:0;}adventure_reset(&adventure);'
replacement = 'for(i=0;i<4;i++){if(echo_seen[i])gameplay_record_echo(&gameplay);memory_clock_used[i]=shard_taken[i]?1:0;}sentinel_defeated=shard_taken[3]?1:0;sentinel_hp=sentinel_defeated?0:4;sentinel_x=252;sentinel_dir=-1;sentinel_iframes=0;sentinel_notice=0;adventure_reset(&adventure);'
if needle not in src: raise SystemExit('sentinel continue anchor missing')
src = src.replace(needle, replacement, 1)

anchor = 'static int memory_clock_near(void)'
helper = r'''static int sentinel_active(void){return room==3&&puzzle_done[3]&&!sentinel_defeated;}
static void sentinel_art(void){
    int p,i,cx=sentinel_x,cy=151;
    if(!sentinel_active())return;
    p=(anim_tick/5)&3;
    /* large brass/purple clock-cat silhouette */
    rect(cx-18,cy-18,36,34,48,27,62);rect(cx-14,cy-14,28,27,122,65,132);
    rect(cx-15,cy-23,9,9,83,43,105);rect(cx+6,cy-23,9,9,83,43,105);
    rect(cx-10,cy-9,20,18,35,22,43);rect(cx-7,cy-6,14,14,202,139,48);
    rect(cx-4,cy-3,8,8,244,213,112);rect(cx-1,cy-2,3,7,31,22,35);rect(cx,cy,7,3,31,22,35);
    rect(cx-19,cy+13,9,13,78,39,93);rect(cx+10,cy+13,9,13,78,39,93);
    /* clock-hand tail */
    rect(cx+17,cy+4,18,4,222,72,150);rect(cx+31,cy-3,4,10,222,72,150);rect(cx+31,cy-6,4,4,238,188,81);
    /* orbiting teeth make it unmistakably a miniboss */
    for(i=0;i<4;i++)rect(cx-28+i*18,cy-29+((i&1)*55),6,6,165+p*12,104,38);
    if(sentinel_iframes>0&&((anim_tick/2)&1))rect(cx-21,cy-26,42,55,226,86,187);
    /* HP bar */
    rect(96,62,128,10,25,15,31);rect(99,65,122,4,58,30,70);
    for(i=0;i<sentinel_hp;i++)rect(101+i*29,65,24,4,226,82,165);
}
static void sentinel_tick(void){
    int dx,dy;
    if(sentinel_iframes>0)sentinel_iframes--;
    if(sentinel_notice>0)sentinel_notice--;
    if(!sentinel_active())return;
    sentinel_x+=sentinel_dir;
    if(sentinel_x<145){sentinel_x=145;sentinel_dir=1;}
    if(sentinel_x>278){sentinel_x=278;sentinel_dir=-1;}
    dx=(px+6)-sentinel_x;if(dx<0)dx=-dx;dy=(py+9)-151;if(dy<0)dy=-dy;
    if(gameplay.dash_timer>0&&sentinel_iframes<=0&&dx<31&&dy<31){
        sentinel_hp--;sentinel_iframes=42;sentinel_notice=75;combat_flash=18;combat_flash_x=sentinel_x;combat_flash_y=151;score+=125;gameplay_reward(&gameplay,80);sfx(0x2f00);
        if(sentinel_hp<=0){sentinel_hp=0;sentinel_defeated=1;sentinel_notice=180;score+=500;gameplay_reward(&gameplay,250);timer_frames+=600;if(timer_frames>60*60*5)timer_frames=60*60*5;sfx(0x3100);persist_here();}
    }else if(dx<25&&dy<27&&invuln<=0&&clock_guard<=0&&gameplay.dash_timer<=0){
        health--;invuln=90;sentinel_notice=45;sfx(0x1800);if(health<=0)state=STATE_GAMEOVER;
    }
}
'''
if anchor not in src: raise SystemExit('sentinel helper insertion anchor missing')
src = src.replace(anchor, helper + anchor, 1)

# Render directly in Clockworks before Moko so contact positions line up with gameplay.
needle = 'memory_clock_art();clock_guard_art();draw_moko();delivery_art();combat_art();encounter_art();}'
replacement = 'sentinel_art();memory_clock_art();clock_guard_art();draw_moko();delivery_art();combat_art();encounter_art();}'
if needle not in src: raise SystemExit('sentinel render anchor missing')
src = src.replace(needle, replacement, 1)

# Tick in the actual play loop.
needle = 'moko_audio_tick();if(clock_guard>0)clock_guard--;if(clock_guard_flash>0)clock_guard_flash--;'
replacement = 'moko_audio_tick();sentinel_tick();if(clock_guard>0)clock_guard--;if(clock_guard_flash>0)clock_guard_flash--;'
if needle not in src: raise SystemExit('sentinel gameplay tick anchor missing')
src = src.replace(needle, replacement, 1)

# The fourth shard is earned by defeating the Sentinel, not merely solving the room puzzle.
needle = 'if(room>=4||shard_taken[room]||!puzzle_done[room]||!pressed(n,PAD_CROSS))return;'
replacement = 'if(room>=4||shard_taken[room]||!puzzle_done[room]||(room==3&&!sentinel_defeated)||!pressed(n,PAD_CROSS))return;'
if needle not in src: raise SystemExit('sentinel shard gate anchor missing')
src = src.replace(needle, replacement, 1)

# Discoverability and combat objective are visible in the normal HUD.
needle = 'if(memory_clock_near())FntPrint(font_id,"\\nCROSS - REST AT MEMORY CLOCK");'
replacement = 'if(sentinel_active())FntPrint(font_id,"\\nMINIBOSS: CHRONO SENTINEL HP %d/4 - MEMORY DASH TO STRIKE",sentinel_hp);if(sentinel_notice>0&&sentinel_defeated)FntPrint(font_id,"\\nSENTINEL DEFEATED - +10 SEC - SHARD UNLOCKED");if(memory_clock_near())FntPrint(font_id,"\\nCROSS - REST AT MEMORY CLOCK");'
if needle not in src: raise SystemExit('sentinel HUD anchor missing')
src = src.replace(needle, replacement, 1)

src = src.replace('CLOCK REV 258','SENTINEL REV 259',1)
src = src.replace('C258 %02d:%02d','S259 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
