import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Persistent runtime state for the new defensive clock ability.
needle = 'static MokoGameplay gameplay;static MokoFinale finale;static MokoAdventure adventure;static MokoWorldRuntime living;'
replacement = needle + 'static int clock_guard=0,clock_guard_flash=0;'
if needle not in src:
    raise SystemExit('clock guard globals anchor missing')
src = src.replace(needle, replacement, 1)

# Reset guard cleanly on a new game/checkpoint reconstruction.
needle = 'switch_a=switch_b=0;invuln=0;area_banner=100;'
replacement = 'switch_a=switch_b=0;invuln=0;clock_guard=0;clock_guard_flash=0;area_banner=100;'
if needle not in src:
    raise SystemExit('clock guard reset anchor missing')
src = src.replace(needle, replacement, 1)

# Draw a large unmistakable clock-shaped energy shield around Moko.
anchor = 'static void draw_moko(void)'
helper = r'''static void clock_guard_art(void){
    int p,i,cx=px+12,cy=py+13;
    if(clock_guard<=0)return;
    p=(anim_tick/5)&3;
    rect(cx-23-p,cy-23-p,46+p*2,3,94,49,153);
    rect(cx-23-p,cy+20+p,46+p*2,3,94,49,153);
    rect(cx-23-p,cy-20,3,40,94,49,153);
    rect(cx+20+p,cy-20,3,40,94,49,153);
    rect(cx-17,cy-17,34,34,26,18,52);
    rect(cx-14,cy-14,28,28,55,30,91);
    /* clock hands */
    rect(cx-1,cy-10,3,12,238,198,105);
    rect(cx,cy,11,3,238,198,105);
    /* orbiting memory sparks */
    for(i=0;i<4;i++){
        int ox=(i==0?cx-26:i==1?cx+23:cx-2);
        int oy=(i==2?cy-27:i==3?cy+24:cy-2);
        rect(ox,oy,5,5,105+p*20,75,210);
    }
    if(clock_guard_flash>0)rect(px-4,py-5,32,39,95,55,180);
}
'''
if anchor not in src:
    raise SystemExit('clock guard draw anchor missing')
src = src.replace(anchor, helper + anchor, 1)

# Render the shield immediately before Moko so the protagonist remains readable.
needle = 'draw_moko();delivery_art();combat_art();encounter_art();}'
replacement = 'clock_guard_art();draw_moko();delivery_art();combat_art();encounter_art();}'
if needle not in src:
    raise SystemExit('clock guard room render anchor missing')
src = src.replace(needle, replacement, 1)

# Input/gameplay integration: Square spends Focus to create 1.5 seconds of protection.
needle = 'if(pressed(n,PAD_R1)&&gameplay_try_dash(&gameplay)){adventure_dash(&adventure);sfx(0x2b00);}spd=gameplay_move_speed(&gameplay);'
replacement = 'if(pressed(n,PAD_R1)&&gameplay_try_dash(&gameplay)){adventure_dash(&adventure);sfx(0x2b00);}if(pressed(n,PAD_SQUARE)&&clock_guard<=0&&gameplay.focus>=25){gameplay.focus-=25;clock_guard=90;clock_guard_flash=12;sfx(0x2900);}spd=gameplay_move_speed(&gameplay);'
if needle not in src:
    raise SystemExit('clock guard input anchor missing')
src = src.replace(needle, replacement, 1)

# Make guard actually defensive against every normal hurt source.
needle = 'static void hurt(void){if(invuln||gameplay.dash_timer>0)return;'
replacement = 'static void hurt(void){if(invuln||gameplay.dash_timer>0||clock_guard>0){if(clock_guard>0)clock_guard_flash=8;return;}'
if needle not in src:
    raise SystemExit('clock guard hurt anchor missing')
src = src.replace(needle, replacement, 1)

# Tick the ability and halve Lost Hour drain while it is active.
needle = 'moko_audio_tick();if(pressed(n,PAD_START))state=STATE_PAUSE;if(timer_frames>0)timer_frames--;else{'
replacement = 'moko_audio_tick();if(clock_guard>0)clock_guard--;if(clock_guard_flash>0)clock_guard_flash--;if(pressed(n,PAD_START))state=STATE_PAUSE;if(timer_frames>0){if(clock_guard<=0||(anim_tick&1))timer_frames--;}else{'
if needle not in src:
    raise SystemExit('clock guard timer anchor missing')
src = src.replace(needle, replacement, 1)

# HUD: player can discover and understand the ability without documentation.
needle = 'R1:DASH SELECT:JOURNAL EV%d%%'
replacement = 'R1:DASH SQUARE:GUARD SELECT:JOURNAL EV%d%%'
if needle not in src:
    raise SystemExit('clock guard HUD controls anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'if(combat_rank()[0])FntPrint(font_id,"\\n%s x%d",combat_rank(),gameplay.combo);'
replacement = 'if(clock_guard>0)FntPrint(font_id,"\\nCLOCK GUARD %d",(clock_guard+59)/60);if(combat_rank()[0])FntPrint(font_id,"\\n%s x%d",combat_rank(),gameplay.combo);'
if needle not in src:
    raise SystemExit('clock guard HUD status anchor missing')
src = src.replace(needle, replacement, 1)

# Revision marker for emulator verification.
src = src.replace('ENCOUNTER REV 256','GUARD REV 257',1)
src = src.replace('E256 %02d:%02d','G257 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
