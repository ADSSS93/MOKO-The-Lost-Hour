import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()
if '#include "world3d.h"' not in src:
    anchor='#include "world_runtime.h"\n'
    if anchor not in src: raise SystemExit('3d slice: include anchor missing')
    src=src.replace(anchor,anchor+'#include "world3d.h"\n',1)
# Inject one-minute state if earlier slice pass is not present.
if 'ONE MINUTE SLICE REV 285' not in src:
    anchor='static void station_art(void){'
    if anchor not in src: raise SystemExit('3d slice: station_art missing')
    block=r'''/* ONE MINUTE SLICE REV 285: collect -> talk -> fight -> exit */
static void hurt(void);
static int slice_motes=0,slice_enemy_hp=3,slice_clear=0,slice_notice=0,slice_talked=0;
static unsigned char slice_taken[3]={0,0,0};
static void slice_tick(uint16_t n){
    int i;
    static const int sx[3]={185,348,452};
    static const int sy[3]={176,153,141};
    if(room!=0||slice_clear)return;
    for(i=0;i<3;i++)if(!slice_taken[i]&&hit(px,py,12,18,sx[i]-16,sy[i]-18,32,36)){slice_taken[i]=1;slice_motes++;score+=75;sfx(0x2400);slice_notice=55;}
    if(!slice_talked&&slice_motes>=1&&hit(px,py,12,18,250,145,56,60)&&pressed(n,PAD_CROSS)){slice_talked=1;score+=50;sfx(0x2400);slice_notice=75;}
    if(slice_motes==3&&slice_enemy_hp>0&&hit(px,py,12,18,490,150,70,55)){
        if(pressed(n,PAD_CIRCLE)){slice_enemy_hp--;score+=125;sfx(0x2400);slice_notice=45;if(px<515)px-=10;else px+=10;}
        else if((moko_z-moko_floor_z)<90)hurt();
    }
    if(slice_enemy_hp<=0&&px>585){slice_clear=1;score+=500;sfx(0x2400);slice_notice=180;}
    if(slice_notice>0)slice_notice--;
}
static void slice_hud(void){
    if(room!=0)return;
    if(slice_clear)FntPrint(font_id,"\nDAWN PATH OPEN  +500");
    else if(slice_motes<3)FntPrint(font_id,"\nTIME SPLINTERS  %d/3",slice_motes);
    else if(slice_enemy_hp>0)FntPrint(font_id,"\nSHADOW BOAR  HP %d   O ATTACK",slice_enemy_hp);
    else FntPrint(font_id,"\nREACH THE DAWN GATE");
}
'''
    src=src.replace(anchor,block+'\n'+anchor,1)
    for needle in ('moko_jump_tick(n);moko_tail_tick(n);station_traversal_tick(n);','moko_jump_tick(n);moko_tail_tick(n);'):
        if needle in src:
            src=src.replace(needle,needle+'slice_tick(n);',1);break
    else: raise SystemExit('3d slice: controller tick anchor missing')
    if 'FntFlush(font_id);\n}static void draw_journal' in src:
        src=src.replace('FntFlush(font_id);\n}static void draw_journal','slice_hud();FntFlush(font_id);\n}static void draw_journal',1)
    elif 'FntFlush(font_id);\n}\nstatic void draw_journal' in src:
        src=src.replace('FntFlush(font_id);\n}\nstatic void draw_journal','slice_hud();FntFlush(font_id);\n}\nstatic void draw_journal',1)
    else: raise SystemExit('3d slice: hud anchor missing')
# Replace room_art dispatch by wrapping the complete existing function.
needle='static void room_art(void){'
pos=src.find(needle)
if pos<0: raise SystemExit('3d slice: room_art missing')
start=pos; brace=src.find('{',pos); depth=0; end=None
for i in range(brace,len(src)):
    if src[i]=='{': depth+=1
    elif src[i]=='}':
        depth-=1
        if depth==0:
            end=i+1;break
if end is None: raise SystemExit('3d slice: room_art parse failed')
old=src[start:end]
legacy=old.replace('static void room_art(void)','static void room_art_legacy(void)',1)
wrapper='''\nstatic void room_art(void){\n    if(room==0){\n        world3d_draw_village(px,py,facing,anim_tick,slice_motes,slice_enemy_hp,slice_clear,db[active].ot,&next_packet);\n        return;\n    }\n    room_art_legacy();\n}\n'''
src=src[:start]+legacy+wrapper+src[end:]
src+='\n/* REAL 3D VERTICAL SLICE REV 286 */\n'
pathlib.Path(sys.argv[2]).write_text(src)
