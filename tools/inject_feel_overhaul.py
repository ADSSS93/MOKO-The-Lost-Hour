import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

anchor = 'static void init(void)'
helper = r'''static void tri(int x1,int y1,int x2,int y2,int x3,int y3,int r,int g,int b){POLY_F3*p=(POLY_F3*)next_packet;setPolyF3(p);setXY3(p,x1,y1,x2,y2,x3,y3);setRGB0(p,r,g,b);addPrim(db[active].ot+2,p);next_packet+=sizeof(POLY_F3);}
static void soft_shadow(int x,int y,int w){int i;for(i=0;i<4;i++){int inset=i*2;rect(x-w/2+inset,y+i,w-inset*2,1,10+i*3,8+i*2,18+i*4);}}
'''
if anchor not in src:
    raise SystemExit('feel helper anchor missing')
src = src.replace(anchor, helper + anchor, 1)

pat = re.compile(r'static void draw_moko\(void\)\{.*?\}\s*static void draw_shard', re.S)
rep = r'''static void draw_moko(void){
    int i,moving=(walk_tick&7)!=0,bob=moving?((walk_tick>>1)&1):((anim_tick/18)&1);
    soft_shadow(px+7,py+19,18+(moving?3:0));
    if(gameplay.dash_timer>0){
        for(i=1;i<5;i++){
            int ox=px-(facing?i*6:-i*6),a=95-i*13;
            tri(ox,py+8,ox+7,py+3,ox+11,py+12,55,a,135+i*12);
            tri(ox+2,py+12,ox+10,py+8,ox+7,py+18,40,a-12,120+i*10);
        }
    }
    moko_sprite_draw(px,py-bob,facing,walk_tick,invuln,anim_tick,db[active].ot,&next_packet);
    if(!moving&&((anim_tick/30)&1)){
        tri(px+4,py-3-bob,px+7,py-6-bob,px+9,py-2-bob,180,95,218);
        tri(px+11,py-2-bob,px+14,py-5-bob,px+16,py-1-bob,180,95,218);
    }
}static void draw_shard'''
src,count = pat.subn(rep,src,count=1)
if count != 1:
    raise SystemExit('draw_moko replacement failed')

# Player feel: fixed-point-ish velocity, acceleration, braking and dash impulse.
anchor = 'static void update_play(uint16_t n)'
motion = r'''static int moko_vx=0,moko_vy=0;
static int approach_i(int v,int target,int step){if(v<target){v+=step;if(v>target)v=target;}else if(v>target){v-=step;if(v<target)v=target;}return v;}
static int moko_motion_step(uint16_t n,int spd){
    int tx=0,ty=0,moving=0,base=spd*16;
    if(!(n&PAD_LEFT)){tx=-base;facing=0;moving=1;}
    if(!(n&PAD_RIGHT)){tx=base;facing=1;moving=1;}
    if(!(n&PAD_UP)){ty=-base;moving=1;}
    if(!(n&PAD_DOWN)){ty=base;moving=1;}
    if(gameplay.dash_timer>0){
        int impulse=80;
        if(tx==0&&ty==0){tx=facing?impulse:-impulse;moving=1;}
        else{if(tx>0)tx=impulse;else if(tx<0)tx=-impulse;if(ty>0)ty=impulse;else if(ty<0)ty=-impulse;}
    }
    moko_vx=approach_i(moko_vx,tx,moving?8:6);
    moko_vy=approach_i(moko_vy,ty,moving?8:6);
    if(!moving){if(moko_vx>-6&&moko_vx<6)moko_vx=0;if(moko_vy>-6&&moko_vy<6)moko_vy=0;}
    px+=moko_vx/16;py+=moko_vy/16;
    if(moko_vx||moko_vy)walk_tick+=gameplay.dash_timer>0?2:1;else walk_tick=0;
    return (moko_vx||moko_vy||moving)?1:0;
}
'''
if anchor not in src:
    raise SystemExit('update_play anchor missing')
src = src.replace(anchor, motion + anchor, 1)

move_pat = re.compile(r'spd=gameplay_move_speed\(&gameplay\);.*?gameplay_tick\(&gameplay,m\);', re.S)
move_rep = 'spd=gameplay_move_speed(&gameplay);m=moko_motion_step(n,spd);gameplay_tick(&gameplay,m);'
src,count = move_pat.subn(move_rep,src,count=1)
if count != 1:
    raise SystemExit('movement block replacement failed')

# Stop retained velocity on hard collision rollback so Moko does not buzz against walls.
src = src.replace('px=ox;py=oy;', 'px=ox;py=oy;moko_vx=0;moko_vy=0;')
src = src.replace('room--;px=306;', 'room--;px=306;moko_vx=0;moko_vy=0;', 1)
src = src.replace('room++;px=2;', 'room++;px=2;moko_vx=0;moko_vy=0;', 1)

anchor = 'static void runtime_world_fx_art(void){'
foreground = r'''static void organic_foreground_art(void){
    int drift=(anim_tick/24)&3;
    if(room==0){tri(0,222,0,177,48,222,5,8,18);tri(320,222,320,170,275,222,5,8,18);tri(18,194,34,146+drift,49,194,17,22,41);tri(278,198,292,151-drift,306,198,17,22,41);}
    else if(room==1){tri(0,222,0,151,61,222,13,7,24);tri(320,222,320,143,265,222,13,7,24);tri(8,180,31,116,49,180,35,15,48);tri(274,182,296,109,316,182,35,15,48);}
    else if(room==2){tri(0,222,0,160,54,222,6,18,18);tri(320,222,320,156,270,222,6,18,18);tri(17,205,28,169,41,205,27,45,39);tri(280,205,292,165,306,205,27,45,39);}
    else if(room==3){tri(0,222,0,155,52,222,22,14,6);tri(320,222,320,151,270,222,22,14,6);tri(20,211,36,172-drift,52,211,68,42,15);tri(270,211,286,170+drift,303,211,68,42,15);}
    else{tri(0,222,0,138,72,222,18,5,12);tri(320,222,320,138,248,222,18,5,12);tri(28,198,53,150,78,198,50,13,31);tri(242,198,267,150,292,198,50,13,31);}
}
'''
if anchor not in src:
    raise SystemExit('world fx anchor missing')
src = src.replace(anchor, foreground + anchor, 1)
src = src.replace('runtime_world_fx_art();hud();', 'runtime_world_fx_art();organic_foreground_art();hud();')

marker='WORLD FX REV 270'
if marker not in src:
    raise SystemExit('world fx marker missing')
src=src.replace(marker,'WORLD FX REV 270  FEEL REV 272',1)

pathlib.Path(sys.argv[2]).write_text(src)
