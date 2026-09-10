import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Platform state must exist before draw_moko(), because FEEL REV 272 declares
# horizontal velocity later near update_play(). Insert the vertical/combat state
# immediately before the renderer instead of piggybacking on moko_vx.
state_anchor = 'static void draw_moko(void)'
state_block = '''static int moko_z=0,moko_vz=0,moko_grounded=1,moko_coyote=0,moko_jump_buffer=0,moko_tail_timer=0,moko_tail_cooldown=0;\n'''
if state_anchor not in src:
    raise SystemExit('draw_moko state anchor missing')
src = src.replace(state_anchor, state_block + state_anchor, 1)

# Replace Moko draw so vertical jump height is visible while the ground shadow stays planted.
pat = re.compile(r'static void draw_moko\(void\)\{.*?\}\s*static void draw_shard', re.S)
rep = r'''static void draw_moko(void){
    int i,moving=(walk_tick&7)!=0,bob=moving?((walk_tick>>1)&1):((anim_tick/18)&1),jh=moko_z/16;
    int sw=18+(moving?3:0)-(jh>18?6:jh/3);if(sw<8)sw=8;
    soft_shadow(px+7,py+19,sw);
    if(gameplay.dash_timer>0){for(i=1;i<5;i++){int ox=px-(facing?i*6:-i*6),a=95-i*13;tri(ox,py+8-jh,ox+7,py+3-jh,ox+11,py+12-jh,55,a,135+i*12);}}
    if(moko_tail_timer>0){int sx=facing?px+19:px-7,sy=py+10-jh;tri(px+7,py+11-jh,sx,sy-8,sx+(facing?7:-7),sy+2,188,88,220);tri(px+7,py+12-jh,sx,sy+2,sx+(facing?4:-4),sy+8,116,55,170);}
    moko_sprite_draw(px,py-bob-jh,facing,walk_tick,invuln,anim_tick,db[active].ot,&next_packet);
    if(!moko_grounded&&moko_vz<0){tri(px+4,py+20-jh,px+8,py+25-jh,px+12,py+20-jh,216,174,78);}
}static void draw_shard'''
src,count = pat.subn(rep,src,count=1)
if count != 1:
    raise SystemExit('draw_moko jump replacement failed')

anchor = 'static void update_play(uint16_t n)'
logic = r'''static int moko_interaction_near(void){
    int sx,sy;
    if(world_runtime_near_npc(&living,room,px,py,24)>=0)return 1;
    if(adventure_near_event(&adventure,room,px,py,24)>=0)return 1;
    if(room<4&&!echo_seen[room]){int ex=55+room*38,ey=112+room*17;if(hit(px,py,12,18,ex-10,ey-10,32,32))return 1;}
    if(room<4&&!shard_taken[room]&&puzzle_done[room]){sx=250-room*35;sy=90+room*28;if(hit(px,py,12,18,sx-8,sy-9,25,31))return 1;}
    if(room==0&&hit(px,py,12,18,105,170,32,45))return 1;
    if(room==1&&(hit(px,py,12,18,65,180,28,30)||hit(px,py,12,18,265,100,28,30)))return 1;
    if(room==2&&hit(px,py,12,18,180,70,55,110))return 1;
    return 0;
}
static void moko_jump_tick(uint16_t n){
    if(pressed(n,PAD_CROSS)&&!moko_interaction_near())moko_jump_buffer=6;
    if(moko_grounded)moko_coyote=6;else if(moko_coyote>0)moko_coyote--;
    if(moko_jump_buffer>0)moko_jump_buffer--;
    if(moko_jump_buffer>0&&moko_coyote>0){moko_grounded=0;moko_coyote=0;moko_jump_buffer=0;moko_vz=72;sfx(0x1800);}
    if(!moko_grounded){
        if((n&PAD_CROSS)&&moko_vz>30)moko_vz=30;
        moko_z+=moko_vz;moko_vz-=5;
        if(moko_z<=0){moko_z=0;moko_vz=0;moko_grounded=1;sfx(0x0d00);}
    }
}
static void moko_tail_tick(uint16_t n){
    if(moko_tail_cooldown>0)moko_tail_cooldown--;
    if(moko_tail_timer>0)moko_tail_timer--;
    if(pressed(n,PAD_CIRCLE)&&moko_tail_cooldown==0){moko_tail_timer=10;moko_tail_cooldown=18;sfx(0x2100);}
    if(moko_tail_timer==7){if(world_runtime_dash(&living,room,px,py,facing?1:-1)>=0){score+=35;gameplay_reward(&gameplay,15);sfx(0x2600);}}
}
static int moko_airborne_safe(void){return moko_z>=160;}
'''
if anchor not in src:
    raise SystemExit('update_play anchor missing')
src = src.replace(anchor, logic + anchor, 1)

needle = 'if(pressed(n,PAD_SELECT)){adventure_journal_sync(&adventure);state=STATE_JOURNAL;return;}'
if needle not in src:
    raise SystemExit('update_play input anchor missing')
src = src.replace(needle, needle + 'moko_jump_tick(n);moko_tail_tick(n);', 1)

# Airborne Moko can clear low enemies and floor hazards, while tall laser walls still matter.
src = src.replace('if(world_runtime_touch_enemy(&living,room,px,py)>=0)hurt();','if(!moko_airborne_safe()&&world_runtime_touch_enemy(&living,room,px,py)>=0)hurt();',1)
src = src.replace('if(room==1&&(hit(px,py,12,18,hx(),142,16,8)||','if(room==1&&!moko_airborne_safe()&&(hit(px,py,12,18,hx(),142,16,8)||',1)
src = src.replace('if(room==2&&hit(px,py,12,18,190,hy(),8,18))hurt();','if(room==2&&!moko_airborne_safe()&&hit(px,py,12,18,190,hy(),8,18))hurt();',1)
src = src.replace('if(room==3&&(hit(px,py,12,18,90,184,45,18)||hit(px,py,12,18,hx(),160,20,6)))hurt();','if(room==3&&!moko_airborne_safe()&&(hit(px,py,12,18,90,184,45,18)||hit(px,py,12,18,hx(),160,20,6)))hurt();',1)

# Reset vertical state on forced reposition and room transitions.
src = src.replace('health--;score=score>=25?score-25:0;invuln=60;', 'health--;score=score>=25?score-25:0;invuln=60;moko_z=0;moko_vz=0;moko_grounded=1;',1)
src = src.replace('room--;px=306;moko_vx=0;moko_vy=0;', 'room--;px=306;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_grounded=1;',1)
src = src.replace('room++;px=2;moko_vx=0;moko_vy=0;', 'room++;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_grounded=1;',1)

# Contextual HUD: Cross remains interaction near objects; otherwise it is the jump button.
src = src.replace('R1:DASH SELECT:JOURNAL EV%d%%', 'R1:DASH CIRCLE:TAIL CROSS:JUMP EV%d%%', 1)

marker='FEEL REV 272'
if marker not in src:
    raise SystemExit('feel marker missing')
src=src.replace(marker,'PLATFORM REV 273  FEEL REV 272',1)

pathlib.Path(sys.argv[2]).write_text(src)
