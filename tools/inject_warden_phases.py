import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Add a small deterministic projectile/telegraph state for the final boss.  This is
# deliberately kept in main so the attacks share the exact same coordinates as
# the PS1 renderer and player collision code.
needle = 'static int sentinel_hp=4,sentinel_x=252,sentinel_dir=-1,sentinel_iframes=0,sentinel_defeated=0,sentinel_notice=0;'
replacement = needle + 'static int warden_attack_tick=0,warden_attack_flash=0,warden_phase_notice=0;'
if needle not in src: raise SystemExit('warden globals anchor missing')
src = src.replace(needle, replacement, 1)

# Fresh games reset the boss attack sequencer.
needle = 'sentinel_hp=4;sentinel_x=252;sentinel_dir=-1;sentinel_iframes=0;sentinel_defeated=0;sentinel_notice=0;'
replacement = needle + 'warden_attack_tick=0;warden_attack_flash=0;warden_phase_notice=0;'
if needle not in src: raise SystemExit('warden reset anchor missing')
src = src.replace(needle, replacement, 1)

anchor = 'static int sentinel_active(void)'
helper = r'''static int warden_phase_level(void){
    if(room!=4||finale.phase!=FINALE_STABILIZE)return 0;
    if(finale.boss_hp<=2)return 3;
    if(finale.boss_hp<=4)return 2;
    return 1;
}
static int warden_bolt_x(int lane){
    int t=(warden_attack_tick*3+lane*113)%380;
    return t-30;
}
static int warden_bolt_y(int lane){return lane?166:112;}
static void warden_phase_art(void){
    int phase=warden_phase_level(),i,p,bx,by;
    if(!phase)return;
    bx=finale_boss_x(&finale);by=finale_boss_y(&finale);
    /* Phase crown: increasingly unstable clock fragments orbit the Warden. */
    for(i=0;i<phase+1;i++){
        int ox=((anim_tick*2+i*47)%74)-37;
        int oy=((anim_tick+i*29)%46)-23;
        rect(bx+18+ox,by+13+oy,5+(i&1)*2,5+(i&1)*2,210,137,61);
    }
    /* Phase 2+: horizontal time bolts cross the arena, with bright tips. */
    if(phase>=2){
        for(i=0;i<2;i++){
            int x=warden_bolt_x(i),y=warden_bolt_y(i);
            rect(x,y,23,4,116,56,154);rect(x+17,y-2,6,8,236,91,183);
        }
    }
    /* Phase 3: a pulsing danger frame makes the enrage state unmistakable. */
    if(phase>=3&&((anim_tick/5)&1)){
        p=warden_attack_flash?245:151;
        rect(30,81,260,3,p,43,78);rect(30,196,260,3,p,43,78);
        rect(30,81,3,118,p,43,78);rect(287,81,3,118,p,43,78);
    }
}
static void warden_phase_tick(void){
    int phase=warden_phase_level(),i,dx,dy;
    if(warden_attack_flash>0)warden_attack_flash--;
    if(warden_phase_notice>0)warden_phase_notice--;
    if(!phase){warden_attack_tick=0;return;}
    warden_attack_tick++;
    /* Announce each escalation once as HP crosses a phase boundary. */
    if(phase==2&&finale.boss_hp==4&&warden_phase_notice==0){warden_phase_notice=120;sfx(0x2b00);}
    if(phase==3&&finale.boss_hp==2&&warden_phase_notice==0){warden_phase_notice=150;warden_attack_flash=45;sfx(0x3100);}
    if(phase<2)return;
    for(i=0;i<2;i++){
        dx=(px+6)-(warden_bolt_x(i)+11);if(dx<0)dx=-dx;
        dy=(py+9)-(warden_bolt_y(i)+2);if(dy<0)dy=-dy;
        if(dx<19&&dy<13&&invuln<=0&&clock_guard<=0&&gameplay.dash_timer<=0){
            health--;invuln=75;warden_attack_flash=16;sfx(0x1800);if(health<=0)state=STATE_GAMEOVER;break;
        }
    }
}
'''
if anchor not in src: raise SystemExit('warden helper anchor missing')
src = src.replace(anchor, helper + anchor, 1)

# Render the attack layer in the actual room pass, before Moko so feedback remains readable.
needle = 'sentinel_art();memory_clock_art();clock_guard_art();draw_moko();delivery_art();combat_art();encounter_art();}'
replacement = 'warden_phase_art();sentinel_art();memory_clock_art();clock_guard_art();draw_moko();delivery_art();combat_art();encounter_art();}'
if needle not in src: raise SystemExit('warden render anchor missing')
src = src.replace(needle, replacement, 1)

# Tick in the live play loop after the miniboss system.
needle = 'moko_audio_tick();sentinel_tick();if(clock_guard>0)clock_guard--;if(clock_guard_flash>0)clock_guard_flash--;'
replacement = 'moko_audio_tick();sentinel_tick();warden_phase_tick();if(clock_guard>0)clock_guard--;if(clock_guard_flash>0)clock_guard_flash--;'
if needle not in src: raise SystemExit('warden tick anchor missing')
src = src.replace(needle, replacement, 1)

# Surface phase information directly in the normal HUD.
needle = 'if(sentinel_active())FntPrint(font_id,"\\nMINIBOSS: CHRONO SENTINEL HP %d/4 - MEMORY DASH TO STRIKE",sentinel_hp);'
replacement = 'if(room==4&&finale.phase==FINALE_STABILIZE)FntPrint(font_id,"\\nHOUR WARDEN PHASE %d/3  HP %d/6",warden_phase_level(),finale.boss_hp);if(warden_phase_notice>0&&warden_phase_level()==2)FntPrint(font_id,"\\nTIME BOLTS ONLINE - KEEP MOVING");if(warden_phase_notice>0&&warden_phase_level()==3)FntPrint(font_id,"\\nWARDEN ENRAGED - FINAL PHASE");' + needle
if needle not in src: raise SystemExit('warden HUD anchor missing')
src = src.replace(needle, replacement, 1)

src = src.replace('SENTINEL REV 259','WARDEN REV 260',1)
src = src.replace('S259 %02d:%02d','W260 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
