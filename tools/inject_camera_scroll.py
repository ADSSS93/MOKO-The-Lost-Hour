import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

anchor = 'static void sfx(int p)'
state = 'static int camera_x=0,camera_target_x=0,camera_world_draw=0;\n'
if anchor not in src:
    raise SystemExit('camera state anchor missing')
src = src.replace(anchor, state + anchor, 1)

pat = re.compile(r'static void rect\(int x,int y,int w,int h,int r,int g,int b\)\{(.*?)\}\nstatic void init', re.S)
m = pat.search(src)
if not m:
    raise SystemExit('rect helper missing')
body = m.group(1)
if 'camera_world_draw' not in body:
    body = 'if(camera_world_draw)x-=camera_x;' + body
src = src[:m.start()] + 'static void rect(int x,int y,int w,int h,int r,int g,int b){' + body + '}\nstatic void init' + src[m.end():]

tri_old = 'static void tri(int x1,int y1,int x2,int y2,int x3,int y3,int r,int g,int b){POLY_F3*p=(POLY_F3*)next_packet;setPolyF3(p);setXY3(p,x1,y1,x2,y2,x3,y3);setRGB0(p,r,g,b);addPrim(db[active].ot+2,p);next_packet+=sizeof(POLY_F3);}'
tri_new = 'static void tri(int x1,int y1,int x2,int y2,int x3,int y3,int r,int g,int b){POLY_F3*p=(POLY_F3*)next_packet;if(camera_world_draw){x1-=camera_x;x2-=camera_x;x3-=camera_x;}setPolyF3(p);setXY3(p,x1,y1,x2,y2,x3,y3);setRGB0(p,r,g,b);addPrim(db[active].ot+2,p);next_packet+=sizeof(POLY_F3);}'
if tri_old not in src:
    raise SystemExit('tri helper missing')
src = src.replace(tri_old, tri_new, 1)

art_anchor = 'static void world_event_art(void)'
art = r'''static void station_scroll_art(void){
    int i,pulse=(anim_tick/10)&3;
    if(room!=0)return;
    rect(320,58,320,164,10,15,31);rect(320,194,320,28,25,31,49);rect(320,218,320,4,96,82,64);
    for(i=0;i<4;i++){int x=338+i*70;rect(x,72,54,36,18,31,57);rect(x+4,76,46,28,30,45,74);rect(x+9,82,36,3,75,92,121);}
    rect(350,128,212,46,31,38,59);rect(356,134,200,34,45,55,82);
    for(i=0;i<5;i++){int x=365+i*38;rect(x,138,25,17,12,23,41);rect(x+3,141,19,11,48,88,110);}
    tri(350,174,562,174,548,187,38,43,58);tri(350,174,548,187,364,187,24,28,39);
    for(i=0;i<3;i++){int x=332+i*118;rect(x,94,12,112,28,31,48);tri(x-8,94,x+20,94,x+6,78,49,45,62);}
    for(i=0;i<6;i++){int x=336+i*49;rect(x,185,3,13,74,70,66);rect(x-3,181-pulse/2,9,5,180,148,86);}
    rect(590,116,8,90,54,48,63);rect(616,116,8,90,54,48,63);rect(590,116,34,6,86,71,82);
    rect(598,126,18,18,18,33,44);rect(603,131,8,8,shard_taken[0]?55:175,shard_taken[0]?210:62,shard_taken[0]?105:70);
    rect(320,207,300,3,74,70,67);rect(320,216,300,2,103,92,77);
}
static void camera_tick(void){
    int d;
    if(room==0){camera_target_x=px-150;if(camera_target_x<0)camera_target_x=0;if(camera_target_x>320)camera_target_x=320;d=camera_target_x-camera_x;if(d>0)camera_x+=(d+3)/4;else if(d<0)camera_x-=(3-d)/4;}
    else{camera_x=0;camera_target_x=0;}
}
'''
if art_anchor not in src:
    raise SystemExit('world art anchor missing')
src = src.replace(art_anchor, art + art_anchor, 1)

old = 'if(room==0){if((px>=68&&px<=132)||(px>=184&&px<=246))return 288;}'
new = 'if(room==0){if((px>=68&&px<=132)||(px>=184&&px<=246))return 288;if(px>=344&&px<=412)return 256;if(px>=454&&px<=524)return 336;if(px>=548&&px<=606)return 224;}'
if old not in src:
    raise SystemExit('platform candidate anchor missing')
src = src.replace(old,new,1)

plat_anchor = '    if(room==0){\n        lift=18;'
plat_insert = '''    if(room==0){\n        lift=18;\n        tri(340,196-16,416,196-16,410,206-16,60,72,98);tri(340,196-16,410,206-16,346,206-16,34,42,64);rect(350,190-16,52,3,128,112,72);\n        tri(450,196-21,528,196-21,522,206-21,64,75,101);tri(450,196-21,522,206-21,456,206-21,36,44,66);rect(460,190-21,54,3,128,112,72);\n        tri(544,196-14,610,196-14,604,206-14,68,78,102);tri(544,196-14,604,206-14,550,206-14,38,46,67);\n'''
if plat_anchor not in src:
    raise SystemExit('platform art room0 anchor missing')
src = src.replace(plat_anchor,plat_insert,1)

room_start = 'static void room_art(void){int i;'
if room_start not in src:
    raise SystemExit('room_art start missing')
src = src.replace(room_start, room_start + 'camera_world_draw=1;', 1)
src = src.replace('if(room==0)station_art();', 'if(room==0){station_art();station_scroll_art();}', 1)

sprite_call = 'moko_sprite_draw(px,py-bob-jh,facing,walk_tick,invuln,anim_tick,db[active].ot,&next_packet);'
if sprite_call not in src:
    raise SystemExit('moko sprite call missing')
src = src.replace(sprite_call, 'moko_sprite_draw(px-camera_x,py-bob-jh,facing,walk_tick,invuln,anim_tick,db[active].ot,&next_packet);', 1)

# draw_moko is the final world-space draw inside room_art; reset here instead of
# depending on an exact generated room_art tail, which other injectors rewrite.
reset_anchor = '}static void draw_shard'
if reset_anchor not in src:
    raise SystemExit('draw_moko reset anchor missing')
src = src.replace(reset_anchor, 'camera_world_draw=0;}static void draw_shard', 1)

left_old = 'if(px<0){if(room>0){room--;px=306;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;sfx(0x0d00);}else px=0;}'
left_new = 'if(px<0){if(room>0){room--;px=(room==0?616:306);moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;if(room==0)camera_x=320;sfx(0x0d00);}else px=0;}'
if left_old not in src:
    raise SystemExit('left boundary anchor missing')
src = src.replace(left_old,left_new,1)

right_old = 'if(px>308){if(room<4&&shard_taken[room]){room++;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;sfx(0x0d00);}else px=308;}'
right_new = 'if(room==0){if(px>620){if(shard_taken[0]){room=1;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;camera_x=0;sfx(0x0d00);}else px=620;}}else if(px>308){if(room<4&&shard_taken[room]){room++;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;sfx(0x0d00);}else px=308;}'
if right_old not in src:
    raise SystemExit('right boundary anchor missing')
src = src.replace(right_old,right_new,1)

needle = 'if(room!=last_room){area_banner=90;'
if needle not in src:
    raise SystemExit('camera update anchor missing')
src = src.replace(needle, 'camera_tick();' + needle, 1)

marker='PLATFORM REV 274'
if marker not in src:
    raise SystemExit('platform marker missing')
src=src.replace(marker,'CAMERA REV 275  PLATFORM REV 274',1)

pathlib.Path(sys.argv[2]).write_text(src)
