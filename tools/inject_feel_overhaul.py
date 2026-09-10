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

pat = re.compile(r'static void living_art\(void\)\{.*?\}\s*static void room_art', re.S)
rep = r'''static void living_art(void){
    int i;
    for(i=0;i<ambient_count(&living.ambient);i++){
        const MokoAmbientParticle*p=ambient_particle(&living.ambient,i);if(!p)continue;
        if(p->kind==AMBIENT_RAIN)tri(p->x,p->y,p->x+1,p->y+6,p->x+2,p->y+2,82,118,178);
        else if(p->kind==AMBIENT_SPARK)tri(p->x,p->y-2,p->x-2,p->y+2,p->x+3,p->y+1,235,168,62);
        else if(p->kind==AMBIENT_GEAR)tri(p->x,p->y-3,p->x-3,p->y+2,p->x+3,p->y+2,150,101,42);
        else rect(p->x,p->y,1,2,72,92,118);
    }
    for(i=0;i<MOKO_NPC_COUNT;i++){
        const MokoNpcDef*n=npc_get(i);int pending,bob;if(!n||n->room!=room)continue;
        bob=((anim_tick/18+i)&1);soft_shadow(n->x,n->y+2,14);
        if(n->kind==NPC_CAT){
            tri(n->x-6,n->y-8-bob,n->x,n->y-15-bob,n->x+7,n->y-7-bob,77,86,122);
            tri(n->x-5,n->y-9-bob,n->x-3,n->y-16-bob,n->x,n->y-10-bob,109,93,138);
            tri(n->x+1,n->y-10-bob,n->x+5,n->y-16-bob,n->x+7,n->y-8-bob,109,93,138);
            rect(n->x-2,n->y-8-bob,2,1,224,192,155);rect(n->x+3,n->y-8-bob,2,1,224,192,155);
            tri(n->x+5,n->y-3,n->x+13,n->y-8-bob,n->x+10,n->y,80,72,112);
        }else{
            tri(n->x-5,n->y,n->x,n->y-17-bob,n->x+6,n->y,56,76,109);
            tri(n->x-4,n->y-15-bob,n->x+1,n->y-22-bob,n->x+6,n->y-14-bob,181,151,133);
            rect(n->x-1,n->y-18-bob,2,1,225,205,177);
        }
        pending=adventure_npc_delivery_required(i)?!adventure_npc_delivered(&adventure,i):!quests_is_clear(&adventure.quests,n->quest);
        if(!adventure_npc_met(&adventure,i))tri(n->x,n->y-31,n->x-4,n->y-25,n->x+4,n->y-25,238,205,79);
        else if(pending)tri(n->x,n->y-30,n->x-4,n->y-25,n->x+4,n->y-25,77,211,236);
    }
    for(i=0;i<MOKO_ENEMY_COUNT;i++){
        const MokoEnemy*e=enemies_get(&living.enemies,i);int flap;if(!e||!e->active||e->room!=room||e->kind==ENEMY_HOUR_WARDEN)continue;
        flap=((anim_tick/7+i)&1)*3;soft_shadow(e->x,e->y+3,16);
        if(e->kind==ENEMY_GEARLING){
            tri(e->x,e->y-10,e->x-8-flap,e->y,e->x,e->y+5,168,101,36);
            tri(e->x,e->y-10,e->x+8+flap,e->y,e->x,e->y+5,127,74,28);
            rect(e->x-2,e->y-4,4,3,241,173,58);rect(e->x-1,e->y-3,2,1,42,25,16);
        }else if(e->kind==ENEMY_SHADOW){
            tri(e->x,e->y-17,e->x-8-flap,e->y+3,e->x+7+flap,e->y+3,45,27,70);
            tri(e->x,e->y-12,e->x-3,e->y-6,e->x+3,e->y-6,173,67,203);
            rect(e->x-2,e->y-10,1,1,236,128,246);rect(e->x+2,e->y-10,1,1,236,128,246);
        }else{
            tri(e->x+(e->vx>0?4:-4),e->y-13,e->x-9,e->y+2,e->x+9,e->y+2,125,43,67);
            tri(e->x,e->y-7,e->x-3,e->y-2,e->x+3,e->y-2,244,189,91);
        }
    }
}static void room_art'''
src,count = pat.subn(rep,src,count=1)
if count != 1:
    raise SystemExit('living_art replacement failed')

anchor = 'static void runtime_world_fx_art(void){'
foreground = r'''static void organic_foreground_art(void){
    int drift=(anim_tick/24)&3;
    if(room==0){
        tri(0,222,0,177,48,222,5,8,18);tri(320,222,320,170,275,222,5,8,18);
        tri(18,194,34,146+drift,49,194,17,22,41);tri(278,198,292,151-drift,306,198,17,22,41);
    }else if(room==1){
        tri(0,222,0,151,61,222,13,7,24);tri(320,222,320,143,265,222,13,7,24);
        tri(8,180,31,116,49,180,35,15,48);tri(274,182,296,109,316,182,35,15,48);
    }else if(room==2){
        tri(0,222,0,160,54,222,6,18,18);tri(320,222,320,156,270,222,6,18,18);
        tri(17,205,28,169,41,205,27,45,39);tri(280,205,292,165,306,205,27,45,39);
    }else if(room==3){
        tri(0,222,0,155,52,222,22,14,6);tri(320,222,320,151,270,222,22,14,6);
        tri(20,211,36,172-drift,52,211,68,42,15);tri(270,211,286,170+drift,303,211,68,42,15);
    }else{
        tri(0,222,0,138,72,222,18,5,12);tri(320,222,320,138,248,222,18,5,12);
        tri(28,198,53,150,78,198,50,13,31);tri(242,198,267,150,292,198,50,13,31);
    }
}
'''
if anchor not in src:
    raise SystemExit('world fx anchor missing')
src = src.replace(anchor, foreground + anchor, 1)
src = src.replace('runtime_world_fx_art();hud();', 'runtime_world_fx_art();organic_foreground_art();hud();')
marker='WORLD FX REV 270'
if marker not in src:
    raise SystemExit('world fx marker missing')
src=src.replace(marker,'WORLD FX REV 270  FEEL REV 271',1)
pathlib.Path(sys.argv[2]).write_text(src)
