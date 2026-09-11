import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()

# Runtime REV301: the first real PCSX-Redux capture showed that the legacy
# opening dialogue covered roughly half of the Village with a black panel and
# stale story text. The vertical slice must enter play directly; mission guidance
# is already provided by the compact Village HUD and world-space landmarks.
intro='sfx(0x1200);say(1);'
if intro not in src: raise SystemExit('vertical slice: opening dialogue anchor missing')
src=src.replace(intro,'sfx(0x1200);state=STATE_PLAY;',1)

# The 3D village is now a self-contained gameplay area. Remove legacy room-0
# station systems that were still able to hurt/stop Moko while invisible.
src=src.replace('station_traversal_tick(n);','/* Village 3D owns room-0 traversal; legacy station hazards disabled. */',1)
src=src.replace('if(room==0){if((px>=68&&px<=132)||(px>=184&&px<=246))return 288;if(px>=344&&px<=412)return 256;if(px>=454&&px<=524)return 336;if(px>=548&&px<=606)return 224;}','if(room==0)return 0;',1)
src=src.replace('world_runtime_tick(&living,room,px,py);','if(room!=0)world_runtime_tick(&living,room,px,py);',1)
src=src.replace('if(!moko_airborne_safe()&&world_runtime_touch_enemy(&living,room,px,py)>=0)hurt();','if(room!=0&&!moko_airborne_safe()&&world_runtime_touch_enemy(&living,room,px,py)>=0)hurt();',1)
src=src.replace('interact(n);if(state!=STATE_PLAY)return;','if(room!=0)interact(n);if(state!=STATE_PLAY)return;',1)
src=src.replace('if(room==0&&hit(px,py,12,18,105,170,32,45)&&!puzzle_done[0])','if(room==0&&0&&hit(px,py,12,18,105,170,32,45)&&!puzzle_done[0])',1)

# Move the velocity state before the Village helpers so collision clamps can stop
# inertia cleanly without relying on a later declaration near update_play().
vel='static int moko_vx=0,moko_vy=0;'
if vel not in src: raise SystemExit('vertical slice: motion state missing')
src=src.replace(vel,'',1)
reset_anchor='static void reset_game(void)'
if reset_anchor not in src: raise SystemExit('vertical slice: reset_game missing')
src=src.replace(reset_anchor,vel+'\nstatic void slice_reset(void);\n'+reset_anchor,1)
src=src.replace('world_runtime_reset(&living,0);for(i=0;i<4;i++)','world_runtime_reset(&living,0);slice_reset();for(i=0;i<4;i++)',1)

anchor='static void station_art(void){'
if anchor not in src: raise SystemExit('vertical slice: station_art missing')
block=r'''/* VILLAGE OF DAWN PLAYABLE AREA REV 301
   ONE MINUTE SLICE REV 288 compatibility marker.
   One authored loop: discover -> talk -> collect -> fight -> gate -> clear. */
static void hurt(void);
static int slice_motes=0,slice_enemy_hp=4,slice_clear=0,slice_notice=0,slice_talked=0,slice_stage=0;
static unsigned char slice_taken[3]={0,0,0};
static const int slice_x[3]={112,244,285};
static const int slice_y[3]={170,145,176};
static void slice_reset(void){
    slice_motes=0;slice_enemy_hp=4;slice_clear=0;slice_notice=0;slice_talked=0;slice_stage=0;
    slice_taken[0]=slice_taken[1]=slice_taken[2]=0;
}
static int slice_near_villager(void){return hit(px,py,12,18,185,136,44,48);}
static int slice_near_gate(void){return hit(px,py,12,18,365,112,58,78);}
static void slice_tick(uint16_t n){
    int i,ex=320;
    if(room!=0)return;
    if(py<118){py=118;moko_vy=0;}if(py>196){py=196;moko_vy=0;}
    if(px<18){px=18;moko_vx=0;}if(px>414){px=414;moko_vx=0;}
    if(hit(px,py,12,18,139,151,32,38)){if(px<155)px=127;else px=172;moko_vx=0;}
    if(hit(px,py,12,18,177,118,66,25)&&py<143){py=143;moko_vy=0;}
    if(slice_clear){slice_stage=5;if(slice_notice>0)slice_notice--;return;}
    for(i=0;i<3;i++)if(!slice_taken[i]){
        int x=slice_x[i],y=slice_y[i];
        if(i>0&&!slice_talked)continue;
        if(hit(px,py,12,18,x-12,y-14,24,28)){
            slice_taken[i]=1;slice_motes++;score+=75;gameplay_reward(&gameplay,40);sfx(0x2400);slice_notice=75;
            if(slice_motes==1&&!slice_talked)slice_stage=1;else if(slice_motes<3)slice_stage=2;else slice_stage=3;
        }
    }
    if(!slice_talked&&slice_motes>=1&&slice_near_villager()&&pressed(n,PAD_CROSS)){
        slice_talked=1;slice_stage=2;score+=100;gameplay_reward(&gameplay,45);sfx(0x1900);slice_notice=110;
    }
    if(slice_talked&&slice_motes==3&&slice_enemy_hp>0){
        if(hit(px,py,12,18,ex-34,140,68,55)){
            if(pressed(n,PAD_CIRCLE)&&moko_tail_timer>=8){
                slice_enemy_hp--;score+=125;gameplay_reward(&gameplay,25);sfx(0x2600);slice_notice=55;
                if(px<ex)px-=11;else px+=11;moko_vx=0;
                if(slice_enemy_hp<=0){slice_stage=4;score+=250;sfx(0x2f00);}
            }else if((moko_z-moko_floor_z)<110&&invuln==0){hurt();}
        }
    }
    if(slice_talked&&slice_enemy_hp<=0&&slice_near_gate()){
        slice_clear=1;slice_stage=5;score+=750;gameplay_reward(&gameplay,100);sfx(0x2f00);slice_notice=240;
    }
    if(slice_notice>0)slice_notice--;
}
static void slice_hud(void){
    if(room!=0)return;
    FntPrint(font_id,"VILLAGE OF DAWN   HP %d\n",health);
    if(slice_clear)FntPrint(font_id,"AREA CLEAR - DAWN PATH RESTORED");
    else if(slice_stage==0)FntPrint(font_id,"FOLLOW THE BLUE TIME SPLINTER");
    else if(slice_stage==1)FntPrint(font_id,"CROSS  TALK TO THE CLOCKMAKER"); /* VILLAGER AHEAD   CROSS: TALK */
    else if(slice_stage==2)FntPrint(font_id,"TIME SPLINTERS  %d/3",slice_motes);
    else if(slice_stage==3)FntPrint(font_id,"SHADOW BOAR  HP %d   CIRCLE: TAIL",slice_enemy_hp);
    else FntPrint(font_id,"ENTER THE DAWN GATE");
}
'''
src=src.replace(anchor,block+'\n'+anchor,1)

interaction_old='if(room==0&&hit(px,py,12,18,105,170,32,45))return 1;'
if interaction_old in src:
    src=src.replace(interaction_old,'if(room==0&&hit(px,py,12,18,185,136,44,48))return 1;',1)

for needle2 in ('moko_jump_tick(n);moko_tail_tick(n);/* Village 3D owns room-0 traversal; legacy station hazards disabled. */','moko_jump_tick(n);moko_tail_tick(n);'):
    if needle2 in src:
        src=src.replace(needle2,needle2+'slice_tick(n);',1);break
else: raise SystemExit('vertical slice: controller tick anchor missing')

hurt_old='px=30;py=190;if(health<=0)'
if hurt_old not in src: raise SystemExit('vertical slice: hurt respawn anchor missing')
hurt_new='if(room==0&&slice_talked){px=(slice_motes>=3?276:190);py=176;}else{px=30;py=190;}if(health<=0)'
src=src.replace(hurt_old,hurt_new,1)

hud_anchor='static void hud(void){'
if hud_anchor not in src: raise SystemExit('vertical slice: hud function missing')
src=src.replace(hud_anchor,'static void hud(void){if(room==0){slice_hud();FntFlush(font_id);return;}',1)

src+='\n/* PLAYABLE VILLAGE REV 301: runtime-tested intro overlay removal / boss hit window */\n'
pathlib.Path(sys.argv[2]).write_text(src)
