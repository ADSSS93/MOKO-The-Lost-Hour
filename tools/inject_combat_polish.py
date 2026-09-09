import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Runtime combat feedback state lives in the generated gameplay translation unit.
needle = 'static int switch_a=0,switch_b=0,dialogue_id=0,dialogue_npc=-1,dialogue_started=0,invuln=0;'
replacement = 'static int switch_a=0,switch_b=0,dialogue_id=0,dialogue_npc=-1,dialogue_started=0,invuln=0,combat_flash=0,combat_flash_x=0,combat_flash_y=0,combat_notice=0;'
if needle not in src: raise SystemExit('combat globals anchor missing')
src = src.replace(needle, replacement, 1)

anchor = 'static void room_art(void)'
helpers = r'''static void combat_art(void){
    int p,i;
    if(combat_flash>0){
        p=2+((combat_flash/2)&3);
        rect(combat_flash_x-8-p,combat_flash_y-8-p,16+p*2,16+p*2,70,34,92);
        rect(combat_flash_x-5,combat_flash_y-5,10,10,235,95,205);
        rect(combat_flash_x-2,combat_flash_y-2,4,4,250,235,120);
        for(i=0;i<4;i++)rect(combat_flash_x-12+i*8,combat_flash_y-12+((i&1)*19),3,3,205,105+i*25,235);
    }
    if(gameplay.combo>1&&gameplay.combo_timer>0){
        int w=gameplay.combo*9;if(w>72)w=72;
        rect(236,55,76,8,20,12,34);rect(238,57,w,4,225,70,180);
    }
}
static const char*combat_rank(void){
    if(gameplay.combo>=7)return "TIME STORM";
    if(gameplay.combo>=5)return "CLOCK RUSH";
    if(gameplay.combo>=3)return "MEMORY CHAIN";
    if(gameplay.combo>=2)return "COMBO";
    return "";
}
'''
if anchor not in src: raise SystemExit('room_art anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

needle = 'draw_moko();delivery_art();}'
replacement = 'draw_moko();delivery_art();combat_art();}'
if needle not in src: raise SystemExit('combat render anchor missing')
src = src.replace(needle, replacement, 1)

# Dash contact gets an immediate impact burst at Moko's position.
needle = 'if(gameplay.dash_timer>0&&world_runtime_dash(&living,room,px,py,facing?1:-1)>=0){score+=50;gameplay_reward(&gameplay,20);sfx(0x2600);}'
replacement = 'if(gameplay.dash_timer>0&&world_runtime_dash(&living,room,px,py,facing?1:-1)>=0){score+=50;gameplay_reward(&gameplay,20);combat_flash=12;combat_flash_x=px+(facing?18:-6);combat_flash_y=py+8;combat_notice=45;sfx(0x2600);}'
if needle not in src: raise SystemExit('dash combat anchor missing')
src = src.replace(needle, replacement, 1)

# Defeating enemies now buys back three seconds of the Lost Hour, capped at five minutes.
needle = 'if(combat_reward>0){score+=combat_reward;gameplay_reward(&gameplay,combat_reward);sfx(0x2f00);}'
replacement = 'if(combat_reward>0){score+=combat_reward;gameplay_reward(&gameplay,combat_reward);timer_frames+=180;if(timer_frames>60*60*5)timer_frames=60*60*5;combat_flash=18;combat_flash_x=px+(facing?20:-8);combat_flash_y=py+6;combat_notice=90;sfx(0x2f00);}'
if needle not in src: raise SystemExit('combat reward anchor missing')
src = src.replace(needle, replacement, 1)

# Tick transient combat presentation in the real gameplay loop.
needle = 'if(invuln>0)invuln--;if(world_runtime_touch_enemy'
replacement = 'if(invuln>0)invuln--;if(combat_flash>0)combat_flash--;if(combat_notice>0)combat_notice--;if(world_runtime_touch_enemy'
if needle not in src: raise SystemExit('combat timers anchor missing')
src = src.replace(needle, replacement, 1)

# Surface combo state and the time-steal reward directly in the HUD.
needle = 'if(delivery_text()[0])FntPrint(font_id,"\\n%s",delivery_text());if(ni>=0)'
replacement = 'if(delivery_text()[0])FntPrint(font_id,"\\n%s",delivery_text());if(combat_rank()[0])FntPrint(font_id,"\\n%s x%d",combat_rank(),gameplay.combo);if(combat_notice>0)FntPrint(font_id,"  +3 SEC");if(ni>=0)'
if needle not in src: raise SystemExit('combat HUD anchor missing')
src = src.replace(needle, replacement, 1)

src = src.replace('DELIVERY REV 254','COMBAT REV 255',1)
src = src.replace('D254 %02d:%02d','C255 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
