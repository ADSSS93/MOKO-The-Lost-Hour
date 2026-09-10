import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()

anchor='static void station_art(void){'
if anchor not in src: raise SystemExit('vertical slice: station_art missing')
block=r'''/* ONE MINUTE SLICE REV 285: authored start -> collect -> fight -> exit loop */
static int slice_motes=0,slice_enemy_hp=3,slice_clear=0,slice_notice=0;
static unsigned char slice_taken[3]={0,0,0};
static void slice_art(void){
    int i,bob=(anim_tick/8)&3,ex=500+((anim_tick/10)&1)*3;
    if(room!=0)return;
    /* foreground signage and route landmarks */
    tri(132,186,205,186,195,198,45,52,67);tri(132,186,195,198,140,198,28,34,48);
    tri(292,174,371,174,358,187,52,60,76);tri(292,174,358,187,302,187,31,38,55);
    tri(430,162,515,162,503,177,58,62,79);tri(430,162,503,177,440,177,35,40,58);
    /* three memory motes, each deliberately placed farther along the route */
    for(i=0;i<3;i++)if(!slice_taken[i]){
        int x=(i==0?185:(i==1?348:452)),y=(i==0?176:(i==1?153:141));
        tri(x,y-7-bob,x+6,y,x,y+7+bob,78,210,231);tri(x,y-7-bob,x-6,y,x,y+7+bob,163,88,219);
        rect(x-1,y-2,3,4,241,224,143);
    }
    /* bespoke station sentinel: readable silhouette, not a loose debug rectangle */
    if(slice_motes==3&&slice_enemy_hp>0){
        tri(ex-10,184,ex+10,184,ex,164,88,43,101);tri(ex-12,184,ex+12,184,ex,195,55,29,74);
        rect(ex-6,169,12,12,115,56,136);rect(ex-3,172,2,2,245,204,93);rect(ex+2,172,2,2,245,204,93);
        tri(ex-13,178,ex-5,175,ex-8,188,190,63,116);tri(ex+13,178,ex+5,175,ex+8,188,190,63,116);
        rect(ex-9,196,7,3,38,24,54);rect(ex+2,196,7,3,38,24,54);
    }
    /* final signal gate only opens after the fight */
    rect(596,132,5,65,54,57,70);rect(620,132,5,65,54,57,70);tri(594,132,627,132,611,119,75,65,82);
    if(slice_enemy_hp<=0){rect(603,144,15,28,24,73,72);rect(607,150,7,16,73,215,175);}
    else{rect(603,144,15,28,65,25,43);rect(607,150,7,16,205,58,91);}
}
static void slice_tick(uint16_t n){
    int i,ex=500+((anim_tick/10)&1)*3;
    if(room!=0||slice_clear)return;
    for(i=0;i<3;i++)if(!slice_taken[i]){
        int x=(i==0?185:(i==1?348:452)),y=(i==0?176:(i==1?153:141));
        if(hit(px,py,12,18,x-12,y-14,24,28)){slice_taken[i]=1;slice_motes++;gameplay_reward(&gameplay,50);score+=50;sfx(0x2400);slice_notice=80;}
    }
    if(slice_motes==3&&slice_enemy_hp>0){
        if(hit(px,py,12,18,ex-13,164,26,34)){
            if(pressed(n,PAD_CIRCLE)){slice_enemy_hp--;score+=100;sfx(0x2400);slice_notice=55;if(px<ex)px-=8;else px+=8;}
            else if((moko_z-moko_floor_z)<90)hurt();
        }
    }
    if(slice_enemy_hp<=0&&px>592){slice_clear=1;score+=500;sfx(0x2400);slice_notice=180;}
    if(slice_notice>0)slice_notice--;
}
static void slice_hud(void){
    if(room!=0)return;
    if(slice_clear)FntPrint(font_id,"\nSTATION SIGNAL RESTORED  +500");
    else if(slice_motes<3)FntPrint(font_id,"\nRECOVER MEMORY SPARKS  %d/3",slice_motes);
    else if(slice_enemy_hp>0)FntPrint(font_id,"\nCLEAR THE SENTINEL  HP %d",slice_enemy_hp);
    else FntPrint(font_id,"\nREACH THE GREEN EXIT SIGNAL");
}
'''
src=src.replace(anchor,block+'\n'+anchor,1)
# render slice as part of active station world
needle='static void station_art(void){\n    int i,p=(anim_tick/10)&3;'
if needle not in src: raise SystemExit('vertical slice: commercial station body missing')
src=src.replace(needle,needle+'\n    slice_art();',1)
# gameplay call after existing platform/traversal ticks
for needle2 in ('moko_jump_tick(n);moko_tail_tick(n);station_traversal_tick(n);','moko_jump_tick(n);moko_tail_tick(n);'):
    if needle2 in src:
        src=src.replace(needle2,needle2+'slice_tick(n);',1);break
else: raise SystemExit('vertical slice: controller tick anchor missing')
# append mission line to compact HUD before flush
needle3='FntFlush(font_id);\n}static void draw_journal'
if needle3 in src: src=src.replace(needle3,'slice_hud();FntFlush(font_id);\n}static void draw_journal',1)
else:
    needle3='FntFlush(font_id);\n}\nstatic void draw_journal'
    if needle3 not in src: raise SystemExit('vertical slice: hud flush anchor missing')
    src=src.replace(needle3,'slice_hud();FntFlush(font_id);\n}\nstatic void draw_journal',1)
src+='\n/* ONE MINUTE SLICE REV 285 */\n'
pathlib.Path(sys.argv[2]).write_text(src)
