import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

if 'VILLAGE 3D V2 REV 290' not in src:
    raise SystemExit('Village v2 source marker missing')
src = src.replace('VILLAGE 3D V2 REV 290', 'VILLAGE 3D V3 REV 291', 1)

# Add authored scene dressing built from true XYZ geometry. These helpers deliberately
# reuse GTE polygons/solids rather than 2D screen-space decoration.
anchor = 'static void villager('
if anchor not in src:
    raise SystemExit('villager anchor missing')
helpers = r'''static void awning(uint32_t*ot,char**pk,int x,int z,int w,int r,int g,int b){
    box3(ot,pk,x,106,z,w,68,74,r,g,b);
    prism(ot,pk,x+w/2,70,z-12,w+28,48,92,clampc(r+24),clampc(g+18),clampc(b+12));
    box3(ot,pk,x+10,170,z-8,8,18,10,74,54,40);box3(ot,pk,x+w-18,170,z-8,8,18,10,74,54,40);
}
static void arch(uint32_t*ot,char**pk,int x,int z,int w){
    box3(ot,pk,x,64,z,34,122,52,111,91,73);box3(ot,pk,x+w-34,64,z,34,122,52,111,91,73);
    box3(ot,pk,x,54,z,w,28,52,137,111,83);
    prism(ot,pk,x+w/2,29,z-3,w+28,48,56,102,68,76);
}
static void plaza(uint32_t*ot,char**pk,int tick){
    int i,p=((tick/10)&3)*3;
    quad3(ot,pk,6,(V3){-520,181,1180},(V3){520,181,1180},(V3){470,181,1510},(V3){-470,181,1510},122,105,82);
    for(i=0;i<5;i++){int x=-360+i*180;box3(ot,pk,x,176,1285+(i&1)*34,118,7,52,157,133,95);}
    box3(ot,pk,-82,132,1330,164,54,164,86,75,73);
    prism(ot,pk,0,78-p,1388,116,64,92,93,181,184);
    prism(ot,pk,0,96,1380,54,45,52,231,173,83);
}
static void foliage(uint32_t*ot,char**pk,int x,int z,int tick){
    int sway=((tick/13+x/37)&3)-1;
    box3(ot,pk,x-8,126,z,16,59,18,68,50,34);
    prism(ot,pk,x+sway*3,72,z-7,74,67,42,56,122,77);
    prism(ot,pk,x-sway*2,101,z+7,61,54,34,73,142,91);
}
static void mission_beacon(uint32_t*ot,char**pk,int x,int z,int tick,int mode){
    int p=6+((tick/5)&3)*3;
    if(mode==0){prism(ot,pk,x,42-p,z-16,25,28,15,238,197,82);}
    else if(mode==1){prism(ot,pk,x,34-p,z-16,30,34,17,98,220,235);prism(ot,pk,x,57-p,z-10,14,19,10,236,167,78);}
    else{prism(ot,pk,x,28-p,z-16,34,38,19,116,226,194);box3(ot,pk,x-3,52-p,z-18,6,22,7,243,211,109);}
}
'''
src = src.replace(anchor, helpers + anchor, 1)

# Replace Moko with a denser articulated low-poly silhouette. The gait uses separate
# hips/feet and a counter-swinging clock-hand tail; jump keeps the grounded shadow.
pat = re.compile(r'static void moko\(uint32_t\*ot,char\*\*pk,int x,int gy,int z,int facing,int tick,int jump\)\{.*?\}\nstatic void camera_follow', re.S)
rep = r'''static void moko(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){
    int phase=(tick/4)&3,dir=facing?1:-1,step=(phase==1?10:(phase==3?-10:0));
    int bob=(phase&1)*3,ear=((tick/15)&1)*3,tail=((tick/5)&3)-1,y=gy-jump;
    shadow(ot,pk,x,z,37,jump);
    /* compact pear-shaped feline body */
    prism(ot,pk,x,y+72-bob,z+4,68,76,58,98,49,149);
    box3(ot,pk,x-29,y+91-bob,z-1,58,48,54,112,58,164);
    /* head and muzzle */
    prism(ot,pk,x,y+27-bob,z-2,84,63,58,143,77,187);
    box3(ot,pk,x-25,y+49-bob,z-17,50,19,22,211,180,199);
    prism(ot,pk,x-25,y-11-bob-ear,z+5,39,52,28,109,44,151);
    prism(ot,pk,x+25,y-11-bob+ear,z+5,39,52,28,109,44,151);
    /* eyes and nose project forward in depth */
    box3(ot,pk,x-23,y+34-bob,z-25,12,8,9,231,224,235);box3(ot,pk,x+11,y+34-bob,z-25,12,8,9,231,224,235);
    box3(ot,pk,x-19,y+36-bob,z-30,5,6,6,36,29,45);box3(ot,pk,x+14,y+36-bob,z-30,5,6,6,36,29,45);
    prism(ot,pk,x,y+52-bob,z-31,11,10,7,232,105,142);
    /* clock medallion */
    prism(ot,pk,x,y+105-bob,z-18,36,38,16,207,166,74);prism(ot,pk,x,y+112-bob,z-23,21,22,10,242,224,157);
    box3(ot,pk,x-2,y+114-bob,z-27,4,14,5,34,28,39);box3(ot,pk,x,y+122-bob,z-27,12,4,5,34,28,39);
    /* articulated legs and broad paws */
    box3(ot,pk,x-23-step,y+137-bob,z+1,18,35,34,69,34,109);box3(ot,pk,x+5+step,y+137-bob,z+1,18,35,34,69,34,109);
    prism(ot,pk,x-15-step,y+169-bob,z-7,31,19,40,52,28,82);prism(ot,pk,x+15+step,y+169-bob,z-7,31,19,40,52,28,82);
    /* clock-hand tail counter-swings to the gait */
    if(dir>0){box3(ot,pk,x+27,y+111-bob,z+18,38+tail*4,8,10,207,59,135);prism(ot,pk,x+67+tail*4,y+72-bob-tail*4,z+18,15,53+tail*3,12,225,157,78);}
    else{box3(ot,pk,x-65-tail*4,y+111-bob,z+18,38+tail*4,8,10,207,59,135);prism(ot,pk,x-70-tail*4,y+72-bob-tail*4,z+18,15,53+tail*3,12,225,157,78);}
}
static void camera_follow'''
src,n = pat.subn(rep,src,count=1)
if n != 1:
    raise SystemExit('Moko model replacement failed')

# Camera has authored staging zones: opening wide shot, conversational plaza framing,
# encounter push-in, and gate reveal. Smoothing stays continuous between zones.
old = 'static void camera_follow(int px,int py,int facing){int tx=wx(px)+(facing?90:-90),tz=wz(py);if(!cam_seeded){cam_follow_x=tx;cam_follow_z=tz;cam_seeded=1;}cam_follow_x+=(tx-cam_follow_x)/8;cam_follow_z+=(tz-cam_follow_z)/10;}'
new = '''static void camera_follow(int px,int py,int facing){
    int tx=wx(px)+(facing?92:-92),tz=wz(py);
    if(px<82){tx=wx(105);tz=1330;}
    else if(px>176&&px<226){tx=wx(206);tz=1260;}
    else if(px>=226&&px<286){tx=wx(px)+(facing?58:-58);tz=wz(py)-28;}
    else if(px>=286){tx=wx(290);tz=1210;}
    if(!cam_seeded){cam_follow_x=tx;cam_follow_z=tz;cam_seeded=1;}
    cam_follow_x+=(tx-cam_follow_x)/9;cam_follow_z+=(tz-cam_follow_z)/11;
}'''
if old not in src:
    raise SystemExit('camera follow anchor missing')
src = src.replace(old,new,1)

# Replace the village staging while preserving the exact public draw contract used by gameplay.
pat = re.compile(r'void world3d_draw_village\(int px,int py,int player_jump,int facing,int tick,int motes,int enemy_hp,int clear,uint32_t\*ot,char\*\*pk\)\{.*?\}\nvoid world3d_draw_station', re.S)
rep = r'''void world3d_draw_village(int px,int py,int player_jump,int facing,int tick,int motes,int enemy_hp,int clear,uint32_t*ot,char**pk){
    int i,mx=wx(px),mz=wz(py),mission_mode;VECTOR t;
    if(!ready)world3d_init();camera_follow(px,py,facing);
    t.vx=-cam_follow_x;t.vy=-82;t.vz=132-(cam_follow_z-1120)/19;TransMatrix(&cam,&t);gte_SetRotMatrix(&cam);gte_SetTransMatrix(&cam);
    road(ot,pk);
    /* dawn horizon and a denser playable village corridor */
    quad3(ot,pk,7,(V3){-1450,-460,1870},(V3){1450,-460,1870},(V3){1450,188,1870},(V3){-1450,188,1870},64,78,98);
    plaza(ot,pk,tick);
    house(ot,pk,-1110,1510,300,255,112,96,87);house(ot,pk,-715,1450,340,295,127,104,88);
    house(ot,pk,435,1470,350,282,116,90,82);house(ot,pk,895,1515,310,250,129,102,87);
    awning(ot,pk,-505,1245,190,116,72,66);awning(ot,pk,330,1240,205,81,99,112);
    arch(ot,pk,-138,1535,276);tower(ot,pk,80,1690);
    tree(ot,pk,-835,1190);tree(ot,pk,745,1170);tree(ot,pk,-1120,900);tree(ot,pk,1120,945);
    foliage(ot,pk,-620,1085,tick);foliage(ot,pk,610,1060,tick+9);foliage(ot,pk,-280,1470,tick+17);foliage(ot,pk,285,1488,tick+23);
    fence(ot,pk,-1230,1370,500);fence(ot,pk,735,1380,500);
    lamp(ot,pk,-470,1110,tick);lamp(ot,pk,470,1130,tick);lamp(ot,pk,-760,1450,tick);lamp(ot,pk,760,1470,tick);
    villager(ot,pk,wx(205),wz(160),tick,!clear);
    /* mission state is communicated in-world before the HUD: NPC -> splinters -> boar -> gate */
    mission_mode = clear?2:(enemy_hp>0?(motes<3?1:0):2);
    if(px<176)mission_beacon(ot,pk,wx(205),wz(160),tick,0);
    else if(enemy_hp>0&&motes<3)mission_beacon(ot,pk,wx(236),wz(145),tick,1);
    else if(enemy_hp>0)mission_beacon(ot,pk,wx(258),wz(168),tick,1);
    else mission_beacon(ot,pk,902,1360,tick,2);
    if(motes>0)splinter(ot,pk,wx(112),115,wz(170),tick);
    if(motes>1)splinter(ot,pk,wx(236),92,wz(145),tick+11);
    if(motes>2)splinter(ot,pk,wx(274),120,wz(176),tick+23);
    boar(ot,pk,wx(258),wz(168),enemy_hp,tick);gate(ot,pk,clear,tick);
    for(i=0;i<9;i++){int sx=-960+i*245,sz=820+((i*127)%700),sy=34+((tick*2+i*43)%128);prism(ot,pk,sx,sy,sz,7,10,7,98,181,204);}
    moko(ot,pk,mx,7,mz,facing,tick,player_jump);
}
void world3d_draw_station'''
src,n = pat.subn(rep,src,count=1)
if n != 1:
    raise SystemExit('Village staging replacement failed')

pathlib.Path(sys.argv[2]).write_text(src)
