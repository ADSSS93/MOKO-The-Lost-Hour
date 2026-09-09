#include <stdint.h>
#include <psxgpu.h>
#include "moko_sprite.h"
#include "intro.h"

extern const uint8_t moko_tim[];
static TIM_IMAGE moko_image;
static int moko_ready=0;

static void intro_tile(int x,int y,int w,int h,int r,int g,int b){TILE t;setTile(&t);setXY0(&t,x,y);setWH(&t,w,h);setRGB0(&t,r,g,b);DrawPrim((const uint32_t*)&t);}
static void starfield(int t){int i;for(i=0;i<28;i++){int x=(i*73+t/(2+(i&3)))%320;int y=18+((i*37)%190);int v=45+((i*29+t)&63);intro_tile(x,y,(i%7)==0?2:1,(i%7)==0?2:1,v,v+8,v+20);}}
static void clock_face(int cx,int cy,int r,int pulse){int i;intro_tile(cx-r,cy-r,r*2,r*2,8,13,27);intro_tile(cx-r+4,cy-r+4,r*2-8,r*2-8,28,39,58);intro_tile(cx-r+8,cy-r+8,r*2-16,r*2-16,10,17,31);for(i=0;i<12;i++){int x=cx+((i%3)-1)*(r-13);int y=cy+(((i/3)%3)-1)*(r-13);intro_tile(x,y,2,2,145,150,165);}intro_tile(cx-2,cy-r+9,4,9,205,185,125);intro_tile(cx-2,cy,4,31,205,185,125);intro_tile(cx,cy-2,27,4,205,185,125);intro_tile(cx-4-pulse,cy-4-pulse,8+pulse*2,8+pulse*2,50,170,195);}
static void moko_silhouette(int x,int y,int pulse){
    /* Moko identity: purple cat, pointed ears, chest clock and hand-tail */
    intro_tile(x+7,y+5,26,20,86+pulse*8,48,126+pulse*10);
    intro_tile(x+8,y,8,11,61,31,94);intro_tile(x+25,y,8,11,61,31,94);
    intro_tile(x+10,y+9,20,14,116+pulse*6,66,158+pulse*7);
    intro_tile(x+14,y+13,4,4,238,242,250);intro_tile(x+15,y+14,2,2,20,18,30);
    intro_tile(x+24,y+17,3,3,236,80,146);
    intro_tile(x+9,y+25,24,31,75+pulse*7,38,111+pulse*8);
    intro_tile(x+15,y+31,12,12,201,174,106);intro_tile(x+18,y+34,6,6,241,226,172);intro_tile(x+21,y+35,2,5,28,22,31);
    intro_tile(x+5,y+29,7,23,90,45,129);intro_tile(x+30,y+29,7,23,90,45,129);
    intro_tile(x+12,y+54,8,13,52,28,82);intro_tile(x+24,y+54,8,13,52,28,82);
    /* long tail ending like a clock hand */
    intro_tile(x+34,y+39,13,4,213,62,132);intro_tile(x+44,y+35,4,8,213,62,132);intro_tile(x+46,y+32,3,6,214,176,91);
}
static void play_boot_intro(void){
    MokoIntro in;DRAWENV intro_draw,restore_draw;DISPENV intro_disp;int f,scene,t,pulse,i;
    intro_reset(&in);SetDefDispEnv(&intro_disp,0,0,320,240);SetDefDrawEnv(&intro_draw,0,0,320,240);SetDefDrawEnv(&restore_draw,0,240,320,240);
    intro_draw.isbg=1;setRGB0(&intro_draw,2,4,12);PutDispEnv(&intro_disp);PutDrawEnv(&intro_draw);SetDispMask(1);f=FntOpen(16,154,288,76,0,128);
    while(!intro_done(&in)){
        scene=intro_scene(&in);t=intro_scene_frame(&in);pulse=(t/7)&3;DrawSync(0);VSync(0);intro_tile(0,0,320,240,2,4,12);starfield(t);
        if(scene==INTRO_STUDIO){
            intro_tile(54,61,212,1,35,80,110);intro_tile(54,126,212,1,35,80,110);intro_tile(91,76,138,38,6,13,28);
            intro_tile(98,82,124,26,22,56+pulse*5,78+pulse*8);intro_tile(103,87,114,16,5,15,27);
            for(i=0;i<5;i++)intro_tile(106+i*23,91+(i&1)*4,13,3,65,180,205);
        }else if(scene==INTRO_CLOCK){
            clock_face(160,91,57,pulse);intro_tile(24,91,70,2,40,85,110);intro_tile(226,91,70,2,40,85,110);
            if(t>70){intro_tile(157,34,6,114,135+pulse*20,35,60);intro_tile(107,89,106,5,60,135+pulse*15,160+pulse*15);}
        }else if(scene==INTRO_FRACTURE){
            clock_face(160,88,49,0);intro_tile(158,25,4,127,175,38,66);intro_tile(89,68,71,3,55,150,180);intro_tile(160,112,78,3,55,150,180);
            for(i=0;i<9;i++){int fx=(37+i*31+(t*(i%3+1)))%290;int fy=42+((i*43+t/2)%91);intro_tile(fx,fy,3+(i&1),3+(i&1),55+i*14,120+i*8,160+i*7);}
        }else if(scene==INTRO_MOKO){
            intro_tile(0,132,320,3,18,50,68);intro_tile(0,135,320,48,5,11,22);moko_silhouette(137,62,pulse);
            intro_tile(36,45,78,2,38,95,120);intro_tile(206,45,78,2,38,95,120);
            if(t>70){intro_tile(58,42,204,2,60,155,180);intro_tile(58,146,204,2,60,155,180);}
        }
        FntPrint(f,"%s\n%s",intro_title(&in),intro_subtitle(&in));FntFlush(f);DrawSync(0);intro_tick(&in,0);
    }
    VSync(0);intro_tile(0,0,320,240,2,4,12);DrawSync(0);PutDrawEnv(&restore_draw);
}

void moko_sprite_init(void){GetTimInfo((const uint32_t *)moko_tim,&moko_image);LoadImage(moko_image.prect,moko_image.paddr);if(moko_image.mode&0x8)LoadImage(moko_image.crect,moko_image.caddr);DrawSync(0);moko_ready=1;play_boot_intro();}

void moko_sprite_draw(int x,int y,int facing,int walk_tick,int invuln,int anim_tick,uint32_t *ot,char **next_packet){
    SPRT *spr;DR_TPAGE *page;TILE *shadow;int moving=(walk_tick>0);int pose=moving?1+((walk_tick/7)&1):0;int frame=(facing?0:3)+pose;int bob=moving?((walk_tick/7)&1):((anim_tick/24)&1);
    if(!moko_ready)return;if(invuln>0&&((anim_tick/3)&1))return;
    shadow=(TILE*)(*next_packet);setTile(shadow);setXY0(shadow,x+2,y+21);setWH(shadow,13,3);setRGB0(shadow,12,16,25);addPrim(ot+1,shadow);*next_packet+=sizeof(TILE);
    spr=(SPRT *)(*next_packet);setSprt(spr);setXY0(spr,x,y-bob);setWH(spr,16,24);setUV0(spr,frame*16,0);setRGB0(spr,170,170,170);addPrim(ot,spr);*next_packet+=sizeof(SPRT);
    page=(DR_TPAGE *)(*next_packet);setDrawTPage(page,0,0,getTPage(2,0,moko_image.prect->x,moko_image.prect->y));addPrim(ot,page);*next_packet+=sizeof(DR_TPAGE);
}
