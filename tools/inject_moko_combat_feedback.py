import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

state_anchor = 'static int chamber_anchors=0;static uint8_t chamber_anchor_used[3]={0};'
if state_anchor not in src:
    raise SystemExit('Hour Chamber state anchor missing')
src = src.replace(state_anchor, state_anchor + '\nstatic int moko_combo=0,moko_combo_timer=0,moko_impact_timer=0,moko_impact_x=0,moko_impact_y=0;', 1)

art_anchor = 'static void world_event_art(void)'
if art_anchor not in src:
    raise SystemExit('world event art anchor missing')
art = r'''static void moko_combat_feedback_art(void){
    int p=(anim_tick/2)&3;
    if(moko_impact_timer>0){
        int r=2+(12-moko_impact_timer);
        rect(moko_impact_x-r,moko_impact_y-1,r*2,2,245,185,92);
        rect(moko_impact_x-1,moko_impact_y-r,2,r*2,235,103,190);
        tri(moko_impact_x-r,moko_impact_y-r,moko_impact_x-2,moko_impact_y-2,moko_impact_x-r-4-p,moko_impact_y-2,116,197,235);
        tri(moko_impact_x+r,moko_impact_y+r,moko_impact_x+2,moko_impact_y+2,moko_impact_x+r+4+p,moko_impact_y+2,216,95,205);
    }
    if(moko_combo_timer>0&&moko_combo>1){int w=20+moko_combo*5;if(w>68)w=68;rect(124,58,w,3,52,24,68);rect(124,58,(w*moko_combo_timer)/90,3,220,92,190);}
}
static void moko_register_hit(int x,int y){
    moko_combo++;if(moko_combo>9)moko_combo=9;moko_combo_timer=90;
    moko_impact_x=x;moko_impact_y=y;moko_impact_timer=12;
    if(moko_combo==3||moko_combo==6||moko_combo==9){score+=moko_combo*20;timer_frames+=30;gameplay_reward(&gameplay,10);sfx(0x2d00);}
}
'''
src = src.replace(art_anchor, art + art_anchor, 1)

# Stable render hook: platform/camera injectors preserve the draw_moko signature.
draw_anchor = 'static void draw_moko(void){'
if draw_anchor not in src:
    raise SystemExit('draw_moko anchor missing')
src = src.replace(draw_anchor, 'static void moko_combat_feedback_art(void);\n' + draw_anchor + 'moko_combat_feedback_art();', 1)

old = 'if(world_runtime_dash(&living,room,px,py,facing?1:-1)>=0){score+=35;gameplay_reward(&gameplay,15);sfx(0x2600);}'
new = 'if(world_runtime_dash(&living,room,px,py,facing?1:-1)>=0){score+=35;gameplay_reward(&gameplay,15);moko_register_hit(px+(facing?25:-10),py+8);sfx(0x2600);}'
if old not in src:
    raise SystemExit('generic tail hit anchor missing')
src = src.replace(old,new,1)

for old,new in [
    ('street_wraith_hp--;street_wraith_hit_flash=8;', 'street_wraith_hp--;street_wraith_hit_flash=8;moko_register_hit(wx,py);'),
    ('house_hound_hp--;house_hound_flash=8;', 'house_hound_hp--;house_hound_flash=8;moko_register_hit(hx2,py);')
]:
    if old not in src:
        raise SystemExit('authored boss hit anchor missing: '+old)
    src = src.replace(old,new,1)

update_anchor = 'static void update_play(uint16_t n)'
if update_anchor not in src:
    raise SystemExit('update_play anchor missing')
logic = r'''static void moko_combat_feedback_tick(void){
    if(moko_impact_timer>0)moko_impact_timer--;
    if(moko_combo_timer>0){moko_combo_timer--;if(moko_combo_timer==0)moko_combo=0;}
}
'''
src = src.replace(update_anchor, logic + update_anchor, 1)

tick_anchor = 'station_traversal_tick(n);backward_street_tick(n);forgotten_house_tick(n);clockworks_expansion_tick(n);hour_chamber_polish_tick(n);'
if tick_anchor not in src:
    raise SystemExit('authored gameplay tick chain missing')
src = src.replace(tick_anchor, tick_anchor + 'moko_combat_feedback_tick();', 1)

hud_anchor = 'if(room==4&&finale.phase==FINALE_STABILIZE)FntPrint(font_id,"TIME ANCHORS %d/3  STABILITY %d%%\\n",chamber_anchors,finale.stability);'
if hud_anchor not in src:
    raise SystemExit('Hour Chamber HUD anchor missing')
src = src.replace(hud_anchor, hud_anchor + 'if(moko_combo_timer>0&&moko_combo>1)FntPrint(font_id,"TAIL COMBO x%d\\n",moko_combo);', 1)

reset_anchor = 'chamber_anchors=0;chamber_anchor_used[0]=chamber_anchor_used[1]=chamber_anchor_used[2]=0;'
if reset_anchor not in src:
    raise SystemExit('Hour Chamber reset anchor missing')
src = src.replace(reset_anchor, reset_anchor + 'moko_combo=0;moko_combo_timer=0;moko_impact_timer=0;', 1)

marker='HOUR CHAMBER POLISH REV 280'
if marker not in src:
    raise SystemExit('Hour Chamber marker missing')
src=src.replace(marker,'MOKO COMBAT FEEDBACK REV 281  '+marker,1)

pathlib.Path(sys.argv[2]).write_text(src)
