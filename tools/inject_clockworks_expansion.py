import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

state_anchor = 'static int house_lights=0,house_hound_hp=4,house_hound_flash=0,house_hound_defeated=0;static uint8_t house_light_taken[3]={0};'
if state_anchor not in src:
    raise SystemExit('Forgotten House state anchor missing')
src = src.replace(state_anchor, state_anchor + '\nstatic int clock_relays=0;static uint8_t clock_relay_on[3]={0};', 1)

art_anchor = 'static void world_event_art(void)'
if art_anchor not in src:
    raise SystemExit('world event art anchor missing')
art = r'''static void clockworks_scroll_art(void){
    int i,p=(anim_tick/6)&3;
    int rx[3]={366,474,588};int ry[3]={157,136,166};
    if(room!=3)return;
    rect(320,58,320,164,35,23,9);rect(320,210,320,12,66,43,18);
    /* giant machinery wall and moving-looking gear silhouettes */
    for(i=0;i<5;i++){
        int x=330+i*63,y=79+(i&1)*25;
        rect(x,y,48,94-(i&1)*18,52,34,13);rect(x+5,y+5,38,84-(i&1)*18,91,58,20);
        rect(x+17,y+18,15,15,152,98,28);rect(x+21,y+22,7,7,52,35,17);
        rect(x+23,y+5,2,13,205,137,41);rect(x+23,y+33,2,12,205,137,41);
    }
    /* raised maintenance bridges */
    tri(344,181,414,181,407,194,151,92,27);tri(344,181,407,194,350,194,77,46,15);
    tri(442,162,514,162,507,176,169,102,29);tri(442,162,507,176,448,176,82,49,15);
    tri(550,188,620,188,613,201,147,87,25);tri(550,188,613,201,556,201,74,44,14);
    /* piston columns and sparks */
    for(i=0;i<4;i++){int x=352+i*78;rect(x,70,6,65+(i&1)*22,104,69,25);rect(x-4,68,14,7,189,124,35);rect(x-4,134+(i&1)*22,14,7,189,124,35);if(((anim_tick/9)+i)%4==0)rect(x+9,111,2+p,2,240,178,58);}
    /* three chrono relays are the authored local mission */
    for(i=0;i<3;i++){
        int on=clock_relay_on[i];
        rect(rx[i]-8,ry[i]-10,18,22,on?48:91,on?155:53,on?126:27);
        rect(rx[i]-4,ry[i]-6,10,10,32,25,18);
        rect(rx[i]-1,ry[i]-3,4,4,on?111:225,on?235:112,on?191:45);
        if(on){rect(rx[i]-12-p,ry[i]-14-p,26+p*2,30+p*2,35,92,75);}
    }
    /* final lift to the Hour Chamber: visually locked until relay mission + shard */
    rect(614,92,8,118,72,48,19);rect(632,92,8,118,72,48,19);rect(614,92,26,7,153,97,29);
    if(clock_relays<3||!shard_taken[3]){rect(623,101,4,96,205,74,47);rect(617,145,20,3,236,98,49);}
    else{rect(623,101,4,96,59,187,142);rect(617,145,20,3,91,235,176);}
}
'''
src = src.replace(art_anchor, art + art_anchor, 1)

room_old = 'else if(room==3)clockworks_art();'
if room_old not in src:
    raise SystemExit('Clockworks render anchor missing')
src = src.replace(room_old, 'else if(room==3){clockworks_art();clockworks_scroll_art();}', 1)

plat_old = 'else if(room==3){if(px>=56&&px<=118)return 288;if(px>=205&&px<=274)return 400;}'
plat_new = 'else if(room==3){if(px>=56&&px<=118)return 288;if(px>=205&&px<=274)return 400;if(px>=344&&px<=414)return 240;if(px>=442&&px<=514)return 416;if(px>=550&&px<=620)return 224;}'
if plat_old not in src:
    raise SystemExit('Clockworks platform anchor missing')
src = src.replace(plat_old, plat_new, 1)

cam_old = 'if(room==0||room==1||room==2){camera_target_x=px-150;'
if cam_old not in src:
    raise SystemExit('camera extension anchor missing')
src = src.replace(cam_old, 'if(room==0||room==1||room==2||room==3){camera_target_x=px-150;', 1)

update_anchor = 'static void update_play(uint16_t n)'
if update_anchor not in src:
    raise SystemExit('update_play anchor missing')
logic = r'''static void clockworks_expansion_tick(uint16_t n){
    int i;int rx[3]={366,474,588};int ry[3]={157,136,166};
    if(room!=3)return;
    if(pressed(n,PAD_CROSS))for(i=0;i<3;i++)if(!clock_relay_on[i]&&hit(px,py,12,18,rx[i]-13,ry[i]-16,36,40)){
        clock_relay_on[i]=1;clock_relays++;score+=120;timer_frames+=120;gameplay_reward(&gameplay,35);sfx(0x2400);
        if(clock_relays==3){score+=220;timer_frames+=300;gameplay_reward(&gameplay,90);sfx(0x3100);}
        break;
    }
}
'''
src = src.replace(update_anchor, logic + update_anchor, 1)

tick_anchor = 'station_traversal_tick(n);backward_street_tick(n);forgotten_house_tick(n);'
if tick_anchor not in src:
    raise SystemExit('authored tick chain missing')
src = src.replace(tick_anchor, tick_anchor + 'clockworks_expansion_tick(n);', 1)

# Direct HUD injection: this deliberately uses update_play, a stable anchor that exists
# in the generated source. It also fixes the missing Forgotten House objective HUD.
play_open = 'static void update_play(uint16_t n){'
if play_open not in src:
    raise SystemExit('update_play body anchor missing')
hud = 'static void update_play(uint16_t n){if(room==2&&px>315)FntPrint(font_id,"MEMORY LIGHTS %d/3  HOUND %s\\n",house_lights,house_hound_defeated?"DOWN":"ACTIVE");if(room==3&&px>315)FntPrint(font_id,"CHRONO RELAYS %d/3  SENTINEL %s\\n",clock_relays,sentinel_defeated?"DOWN":"ACTIVE");'
src = src.replace(play_open, hud, 1)

left_old = 'px=((room==0||room==1||room==2)?616:306);'
if left_old not in src:
    raise SystemExit('extended return anchor missing')
src = src.replace(left_old, 'px=((room==0||room==1||room==2||room==3)?616:306);', 1)
left_cam_old = 'if(room==0||room==1||room==2)camera_x=320;'
if left_cam_old not in src:
    raise SystemExit('extended camera return anchor missing')
src = src.replace(left_cam_old, 'if(room==0||room==1||room==2||room==3)camera_x=320;', 1)

right_old = 'else if(px>308){if(room<4&&shard_taken[room]){room++;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;sfx(0x0d00);}else px=308;}'
right_new = 'else if(room==3){if(px>620){if(shard_taken[3]&&clock_relays==3){room=4;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;camera_x=0;sfx(0x0d00);}else px=620;}}else if(px>308){if(room<4&&shard_taken[room]){room++;px=2;moko_vx=0;moko_vy=0;moko_z=0;moko_vz=0;moko_floor_z=0;moko_grounded=1;sfx(0x0d00);}else px=308;}'
if right_old not in src:
    raise SystemExit('Clockworks right transition anchor missing')
src = src.replace(right_old, right_new, 1)

reset_anchor = 'house_lights=0;house_hound_hp=4;house_hound_flash=0;house_hound_defeated=0;house_light_taken[0]=house_light_taken[1]=house_light_taken[2]=0;'
if reset_anchor not in src:
    raise SystemExit('Forgotten House reset anchor missing')
src = src.replace(reset_anchor, reset_anchor + 'clock_relays=0;clock_relay_on[0]=clock_relay_on[1]=clock_relay_on[2]=0;', 1)

marker = 'FORGOTTEN HOUSE REV 278'
if marker not in src:
    raise SystemExit('Forgotten House marker missing')
src = src.replace(marker, 'CLOCKWORKS EXPANSION REV 279  ' + marker, 1)

pathlib.Path(sys.argv[2]).write_text(src)
