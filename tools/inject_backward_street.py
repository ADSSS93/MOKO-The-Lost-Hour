import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Persistent state for the authored Backward Street encounter.
state_anchor = 'static int camera_x=0,camera_target_x=0,camera_world_draw=0;'
if state_anchor not in src:
    raise SystemExit('camera state anchor missing')
src = src.replace(state_anchor, state_anchor + '\nstatic int street_wraith_hp=3,street_wraith_hit_flash=0,street_wraith_defeated=0;', 1)

# Add a second scrolling half to Backward Street, with readable PS1 geometry and
# an authored mini-encounter instead of another empty corridor.
art_anchor = 'static void world_event_art(void)'
art = r'''static int street_wraith_x(void){return 486+(((anim_tick/24)&1)?8:-8);}
static void backward_street_scroll_art(void){
    int i,wx=street_wraith_x(),pulse=(anim_tick/8)&3;
    if(room!=1)return;
    rect(320,58,320,164,23,11,31);rect(320,202,320,20,39,22,43);
    /* crooked shopfronts and balconies */
    for(i=0;i<5;i++){
        int x=326+i*62,h=58+(i%3)*13;
        rect(x,202-h,53,h,43+(i&1)*8,22,52+(i%2)*8);
        rect(x+5,151-(i%3)*8,17,21,18,26,45);rect(x+29,143+(i%2)*9,18,25,22,29,48);
        rect(x+3,202-h,49,4,91,48,68);
        if(i<4){rect(x+42,126+(i%2)*18,20,4,86,52,71);rect(x+45,130+(i%2)*18,3,31,57,37,55);}
    }
    /* overhead clock cables sell the reversed-street silhouette */
    for(i=0;i<4;i++){int x=346+i*72;rect(x,77,3,45,48,41,61);rect(x-8,76,19,5,105,72,91);}
    tri(330,95,432,79,536,96,68,44,70);tri(430,80,532,96,632,82,61,40,65);
    /* broken raised sidewalks form a jump route */
    tri(344,190,410,190,404,201,91,43,75);tri(344,190,404,201,350,201,50,25,48);
    tri(438,181,510,181,504,194,104,48,82);tri(438,181,504,194,444,194,55,26,51);
    tri(548,188,612,188,606,201,88,42,73);tri(548,188,606,201,554,201,48,24,46);
    /* reverse-flow time puddles on the low street */
    for(i=0;i<3;i++){int x=365+i*91;rect(x,204,48,8,35,19,48);rect(x+5+pulse,207,37-pulse*2,2,186,58,125);}
    /* Bell Wraith mini-enemy: large silhouette, clock face and pendulum tail. */
    if(!street_wraith_defeated){
        int flash=street_wraith_hit_flash>0;
        rect(wx-10,126,22,29,flash?210:72,flash?95:35,flash?205:91);
        tri(wx-12,128,wx,111,wx+13,128,flash?230:105,flash?120:50,flash?220:126);
        rect(wx-6,132,13,13,34,24,50);rect(wx-3,135,7,7,190,151,85);
        rect(wx,137,1,5,238,210,125);rect(wx,141,4,1,238,210,125);
        tri(wx-2,155,wx+3,155,wx+8,171,128,61,113);
        rect(wx-16,120,4,4,215,75,145);rect(wx+14,120,4,4,215,75,145);
    }else{
        rect(478,151,28,4,62,42,61);rect(490,143,4,8,118,82,106);
    }
    /* far gate opens visually after defeating the wraith */
    rect(614,103,8,99,54,34,55);rect(632,103,8,99,54,34,55);rect(614,103,26,6,93,52,75);
    if(!street_wraith_defeated){rect(623,109,4,83,184,48,105);rect(618,148,18,3,225,63,126);}
    else {rect(623,109,4,83,48,119,105);rect(618,148,18,3,75,202,151);}
}
'''
if art_anchor not in src:
    raise SystemExit('world event art anchor missing')
src = src.replace(art_anchor, art + art_anchor, 1)

# Draw the new half inside the existing camera-aware room renderer.
room_old = 'else if(room==1)street_art();'
if room_old not in src:
    raise SystemExit('street room render anchor missing')
src = src.replace(room_old, 'else if(room==1){street_art();backward_street_scroll_art();}', 1)

# Expand platform collision to match the visible raised sidewalks.
platform_old = 'else if(room==1){if(px>=92&&px<=154)return 240;if(px>=232&&px<=294)return 336;}'
platform_new = 'else if(room==1){if(px>=92&&px<=154)return 240;if(px>=232&&px<=294)return 336;if(px>=344&&px<=410)return 192;if(px>=438&&px<=510)return 336;if(px>=548&&px<=612)return 224;}'
if platform_old not in src:
    raise SystemExit('street platform anchor missing')
src = src.replace(platform_old, platform_new, 1)

# Camera now scrolls in both authored 640-unit districts.
cam_pat = re.compile(r'static void camera_tick\(void\)\{.*?\n\}', re.S)
cam = r'''static void camera_tick(void){
    int d;
    if(room==0||room==1){camera_target_x=px-150;if(camera_target_x<0)camera_target_x=0;if(camera_target_x>320)camera_target_x=320;d=camera_target_x-camera_x;if(d>0)camera_x+=(d+3)/4;else if(d<0)camera_x-=(3-d)/4;}
    else{camera_x=0;camera_target_x=0;}
}'''
src,count = cam_pat.subn(cam,src,count=1)
if count != 1:
    raise SystemExit('camera tick replacement failed')

# Authored combat/hazard logic. Circle-tail at close range damages the Bell Wraith;
# its periodic chime wave forces a jump or retreat to the raised sidewalk.
update_anchor = 'static void update_play(uint16_t n)'
if update_anchor not in src:
    raise SystemExit('update_play anchor missing')
logic = r'''static void backward_street_tick(uint16_t n){
    int wx,dist;
    (void)n;
    if(street_wraith_hit_flash>0)street_wraith_hit_flash--;
    if(room!=1||street_wraith_defeated)return;
    wx=street_wraith_x();dist=px-wx;if(dist<0)dist=-dist;
    if(moko_tail_timer==7&&dist<34&&py>120&&py<205){
        street_wraith_hp--;street_wraith_hit_flash=8;score+=60;gameplay_reward(&gameplay,20);sfx(0x2900);
        if(street_wraith_hp<=0){street_wraith_defeated=1;street_wraith_hp=0;score+=250;timer_frames+=60*8;gameplay_reward(&gameplay,80);sfx(0x3100);}
    }
    /* body contact */
    if(!street_wraith_hit_flash&&(moko_z-moko_floor_z)<176&&hit(px,py,12,18,wx-13,111,28,61))hurt();
    /* expanding bell shock along the lower lane every cycle */
    if(((anim_tick/20)%6)==0&&py>166&&moko_floor_z==0&&(moko_z-moko_floor_z)<160&&dist<92)hurt();
}
'''
src = src.replace(update_anchor, logic + update_anchor, 1)

tick_anchor = 'station_traversal_tick(n);'
if tick_anchor not in src:
    raise SystemExit('station traversal tick anchor missing')
src = src.replace(tick_anchor, tick_anchor + 'backward_street_tick(n);', 1)

# Room transitions understand that rooms 0 and 1 are extended. The Bell Wraith
# is an encounter gate, while the existing shard remains the story gate.
left_pat = re.compile(r'if\(px<0\)\{if\(room>0\)\{room--;px=\(room==0\?616:306\);.*?else px=0;\}', re.S)
left_new = 'if(px<0){if(room>0){room--;px=((room==0||room==1)?616:306);moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;if(room==0||room==1)camera_x=320;sfx(0x0d00);}else px=0;}'
src,count = left_pat.subn(left_new,src,count=1)
if count != 1:
    raise SystemExit('left transition replacement failed')

right_old = 'if(room==0){if(px>620){if(shard_taken[0]){room=1;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;camera_x=0;sfx(0x0d00);}else px=620;}}else if(px>308){if(room<4&&shard_taken[room]){room++;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;sfx(0x0d00);}else px=308;}'
right_new = 'if(room==0){if(px>620){if(shard_taken[0]){room=1;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;camera_x=0;sfx(0x0d00);}else px=620;}}else if(room==1){if(px>620){if(shard_taken[1]&&street_wraith_defeated){room=2;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;camera_x=0;sfx(0x0d00);}else px=620;}}else if(px>308){if(room<4&&shard_taken[room]){room++;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;sfx(0x0d00);}else px=308;}'
if right_old not in src:
    raise SystemExit('right transition anchor missing')
src = src.replace(right_old,right_new,1)

# Reset encounter on a new game so continue/save semantics remain deterministic.
reset_anchor = 'world_runtime_reset(&living,0);'
if reset_anchor not in src:
    raise SystemExit('reset anchor missing')
src = src.replace(reset_anchor, reset_anchor + 'street_wraith_hp=3;street_wraith_hit_flash=0;street_wraith_defeated=0;', 1)

marker='STATION LEVEL REV 276'
if marker not in src:
    raise SystemExit('station marker missing')
src=src.replace(marker,'BACKWARD STREET REV 277  STATION LEVEL REV 276',1)

pathlib.Path(sys.argv[2]).write_text(src)
