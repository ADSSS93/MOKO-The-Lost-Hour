import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

def replace_func(name, next_name, body):
    global src
    pattern = rf"static void {name}\(void\)\{{.*?\}}\nstatic void {next_name}"
    repl = f"static void {name}(void){{{body}}}\nstatic void {next_name}"
    src, count = re.subn(pattern, repl, src, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"could not replace {name}")

replace_func("station_art", "street_art", r'''int i;/* Silent Station: layered platforms, clock arch, lamps, rails */
rect(0,58,320,164,8,13,29);rect(0,188,320,34,24,30,46);rect(0,216,320,6,92,73,58);
rect(14,72,292,7,38,49,76);rect(18,82,284,3,18,29,48);
for(i=0;i<6;i++){int x=18+i*50;rect(x,91,34,44,18,29,52);rect(x+3,94,28,38,29,44,69);rect(x+8,101,18,22,10,18,34);rect(x+14,104,6,16,68,92,116);}
rect(126,75,68,68,29,39,60);rect(132,81,56,56,7,13,26);rect(158,88,4,22,201,174,106);rect(159,107,22,4,201,174,106);rect(156,104,10,10,55,176,205);
rect(40,151,76,6,63,74,98);rect(46,157,8,27,45,56,77);rect(100,157,8,27,45,56,77);rect(205,143,78,8,58,71,94);rect(215,151,6,32,46,57,76);rect(267,151,6,32,46,57,76);
rect(22,64,86,12,23,66,88);rect(27,67,76,6,87,183,205);
for(i=0;i<4;i++){int x=34+i*82;rect(x,134,4,54,42,52,67);rect(x-4,130,12,7,160,139,83);rect(x-2,131,8,4,238,209,116);}
rect(0,203,320,3,104,90,70);for(i=0;i<16;i++)rect(i*22,202,3,20,65,57,52);''')

replace_func("street_art", "house_art", r'''int i;/* Backward Street */
rect(0,58,320,164,24,9,35);rect(0,196,320,26,47,24,48);
for(i=0;i<7;i++){int x=i*50-10,h=55+(i%3)*18;rect(x,196-h,46,h,43,20,55);rect(x+5,196-h+7,36,h-12,29,16,42);rect(x+10,196-h+15,8,10,126,67,104);rect(x+26,196-h+28,8,10,80,118,145);}
rect(245,70,38,38,73,62,95);rect(251,76,26,26,137,111,148);rect(263,63,3,58,205,58,112);
rect(30,154,74,8,111,37,67);rect(35,162,64,28,50,22,45);rect(194,150,78,8,42,91,111);rect(199,158,68,32,25,43,61);
rect(66,181,22,21,35,35,45);rect(70,185,14,13,switch_a?55:151,switch_a?221:62,72);rect(265,102,22,21,35,35,45);rect(269,106,14,13,switch_b?55:151,switch_b?221:62,72);
rect(hx(),174,22,9,212,66,88);rect(hx()+4,181,5,5,18,19,29);rect(hx()+15,181,5,5,18,19,29);
if(!puzzle_done[1]){rect(pulse_x(1),118,17,5,234,72,128);rect(pulse_x(2),162,14,5,198,53,106);}
for(i=0;i<5;i++){int x=20+i*67;rect(x,127,3,69,39,34,54);rect(x-3,125,9,5,226,177,93);}''')

replace_func("house_art", "clockworks_art", r'''int i;/* House Without Morning */
rect(0,58,320,164,8,25,27);rect(0,201,320,21,42,48,39);rect(0,62,320,8,23,54,51);
for(i=0;i<5;i++){int x=16+i*63;rect(x,82,52,64,18,45,43);rect(x+4,86,44,56,31,66,59);rect(x+10,94,32,34,13,31,32);rect(x+16,100,20,18,82,109,95);}
rect(18,161,98,9,64,55,42);rect(24,170,8,31,48,43,36);rect(102,170,8,31,48,43,36);rect(207,153,82,12,56,50,41);rect(214,165,8,36,46,41,35);rect(274,165,8,36,46,41,35);
rect(125,83,28,118,35,72,62);rect(130,89,18,106,13,31,31);rect(258,111,30,90,35,72,62);rect(263,117,20,78,13,31,31);
rect(175,74,43,43,47,86,76);rect(181,80,31,31,11,28,29);rect(195,84,3,13,175,211,185);rect(196,95,10,3,175,211,185);rect(190,hy(),12,22,170,226,196);
if(!puzzle_done[2]){rect(155,66,4,84,166,216,188);rect(226,143,4,67,166,216,188);}
for(i=0;i<9;i++)rect(8+i*38,205-(i%2)*4,22,4,74,70,56);''')

replace_func("clockworks_art", "chamber_art", r'''int i;/* Clockworks */
rect(0,58,320,164,29,18,8);rect(0,207,320,15,67,44,19);rect(0,63,320,6,81,51,19);
for(i=0;i<8;i++){int x=4+i*42,y=76+(i%2)*37;rect(x,y,34,34,64,43,18);rect(x+4,y+4,26,26,145,91,28);rect(x+10,y+10,14,14,49,34,19);rect(x+15,y+2,4,30,212,132,37);rect(x+2,y+15,30,4,212,132,37);}
rect(14,154,122,7,98,66,30);rect(129,154,7,40,98,66,30);rect(201,121,7,79,98,66,30);rect(208,121,74,7,98,66,30);
rect(hx(),174,28,7,241,151,37);rect(hx()+4,181,20,4,103,67,27);
rect(176,132,7,75,gameplay.dash_timer?57:236,gameplay.dash_timer?219:68,55);rect(236,72,7,101,gameplay.dash_timer?57:236,gameplay.dash_timer?219:68,55);
for(i=0;i<7;i++){int x=(i*53+anim_tick*2)%310;int y=72+((i*31+anim_tick)%113);rect(x,y,3,3,244,183,56);}''')

replace_func("chamber_art", "world_event_art", r'''int i,sx,p,bx,by;/* Clock Chamber + active Hour Warden boss */
rect(0,58,320,164,24,5,14);rect(0,206,320,16,63,18,30);rect(22,70,276,8,71,29,48);rect(22,78,8,128,71,29,48);rect(290,78,8,128,71,29,48);
rect(92,73,136,112,44,16,31);rect(101,82,118,94,82,39,57);rect(111,92,98,74,16,12,25);rect(156,97,8,31,218,174,106);rect(158,123,35,7,218,174,106);rect(151,117,18,18,92,224,236);
for(i=0;i<4;i++){sx=108+i*31;if(finale.socket[i]){p=(anim_tick/9+i)&3;rect(sx-2-p,172-p,18+p*2,18+p*2,24,93,112);rect(sx,174,14,14,91,237,250);}else{rect(sx-2,172,18,18,61,28,45);rect(sx+2,176,10,10,18,14,24);}}
if(finale.phase==FINALE_STABILIZE){
 bx=finale_boss_x(&finale);by=finale_boss_y(&finale);p=finale.boss_flash?245:118;
 /* Warden: large clock-headed silhouette, visibly moving */
 rect(bx-6,by-8,48,48,45,12,37);rect(bx,by-14,36,18,78,22,58);rect(bx+5,by-9,26,13,p,48,92);
 rect(bx+9,by-5,5,5,250,196,94);rect(bx+23,by-5,5,5,250,196,94);
 rect(bx+14,by+7,9,9,218,174,106);rect(bx+17,by+10,3,8,25,19,28);
 rect(bx-10,by+21,12,29,61,18,48);rect(bx+35,by+21,12,29,61,18,48);rect(bx+4,by+35,10,20,50,14,42);rect(bx+23,by+35,10,20,50,14,42);
 /* boss HP pips */rect(91,61,138,8,18,9,20);for(i=0;i<6;i++){rect(95+i*22,63,18,4,i<finale.boss_hp?232:55,i<finale.boss_hp?55:23,i<finale.boss_hp?92:38);}
}
if(finale_hazard_active(&finale)){rect(finale_sweep_x(&finale),68,4,138,244,56,82);if(finale.phase==FINALE_STABILIZE)rect(28,finale_sweep_y(&finale),264,4,72,181,238);}
if(finale.phase==FINALE_STABILIZE){rect(72,191,176,10,26,18,30);rect(75,194,(finale.stability*170)/100,4,81,230,241);}''')

# Integrate dash collision against the moving Warden into the real room-4 gameplay loop.
combat_old = 'if(room==4){finale_tick(&finale,gameplay.dash_timer>0);if(finale_hazard_active(&finale)'
combat_new = 'if(room==4){finale_tick(&finale,gameplay.dash_timer>0);if(finale.phase==FINALE_STABILIZE&&gameplay.dash_timer>0&&hit(px,py,12,18,finale_boss_x(&finale)-10,finale_boss_y(&finale)-15,58,72)&&finale_boss_hit(&finale)){score+=175;gameplay_reward(&gameplay,35);sfx(0x2f00);px+=facing?-24:24;}if(finale_hazard_active(&finale)'
if combat_old not in src:
    raise SystemExit("could not integrate Hour Warden combat")
src = src.replace(combat_old, combat_new, 1)

# Make the new artifact unmistakable in title and HUD.
title_old = 'FntPrint(font_id,"\\n\\n      M O K O\\n   THE LOST HOUR\\n\\n START - BEGIN\\n Find four shards. Remember why.");'
title_new = 'FntPrint(font_id,"\\n\\n      M O K O\\n   THE LOST HOUR\\n\\n BOSS REV 245\\n START - BEGIN\\n Find four shards. Remember why.");'
if title_old not in src:
    raise SystemExit("could not stamp title revision")
src = src.replace(title_old, title_new, 1)

hud_old = 'FntPrint(font_id,"%02d:%02d S%d/4 HP%d SCORE%d FOCUS%d\\n%s R1:DASH SELECT:JOURNAL EV%d%%",'
hud_new = 'FntPrint(font_id,"B245 %02d:%02d S%d/4 HP%d SCORE%d FOCUS%d\\n%s R1:DASH SELECT:JOURNAL EV%d%%",'
if hud_old not in src:
    raise SystemExit("could not stamp HUD revision")
src = src.replace(hud_old, hud_new, 1)

pathlib.Path(sys.argv[2]).write_text(src)
