#include <stdint.h>
#include <psxgpu.h>
#include "moko_sprite.h"
#include "intro.h"

extern const uint8_t moko_tim[];
static TIM_IMAGE moko_image;
static int moko_ready=0;

static void intro_tile(int x,int y,int w,int h,int r,int g,int b){TILE t;setTile(&t);setXY0(&t,x,y);setWH(&t,w,h);setRGB0(&t,r,g,b);DrawPrim((const uint32_t*)&t);}
static void play_boot_intro(void){
    MokoIntro in;
    DRAWENV intro_draw,restore_draw;
    DISPENV intro_disp;
    int f,scene,t,pulse;
    intro_reset(&in);
    SetDefDispEnv(&intro_disp,0,0,320,240);
    SetDefDrawEnv(&intro_draw,0,0,320,240);
    SetDefDrawEnv(&restore_draw,0,240,320,240);
    intro_draw.isbg=1;setRGB0(&intro_draw,3,4,11);
    PutDispEnv(&intro_disp);PutDrawEnv(&intro_draw);SetDispMask(1);
    f=FntOpen(18,150,284,72,0,128);
    while(!intro_done(&in)){
        scene=intro_scene(&in);t=intro_scene_frame(&in);pulse=(t/8)&3;
        DrawSync(0);VSync(0);intro_tile(0,0,320,240,3,4,11);
        if(scene==INTRO_STUDIO){
            intro_tile(88,74,144,2,65,85,120);intro_tile(116,92,88,28,12,20,38);
            intro_tile(122,98,76,16,45+pulse*8,80+pulse*10,115+pulse*12);
        }else if(scene==INTRO_CLOCK){
            intro_tile(112,48,96,96,15,20,35);intro_tile(119,55,82,82,45,50,65);
            intro_tile(157,62,6,42,205,190,145);intro_tile(159,101,34,5,205,190,145);
            intro_tile(151-pulse,95-pulse,18+pulse*2,18+pulse*2,45,110,130);
        }else if(scene==INTRO_FRACTURE){
            intro_tile(158,35,4,105,150,45,70);intro_tile(110,68,50,3,75,150,180);intro_tile(160,104,55,3,75,150,180);
            intro_tile(82+(t%145),86,5,5,90,220,235);intro_tile(250-(t%120),126,4,4,210,75,120);
        }else if(scene==INTRO_MOKO){
            intro_tile(145,64,30,52,18,34,50);intro_tile(151,72,18,18,180,155,135);
            intro_tile(148,112,7,28,65,105,135);intro_tile(166,112,7,28,65,105,135);
            if(t>70){intro_tile(75,45,170,2,55,120,145);intro_tile(75,143,170,2,55,120,145);}
        }
        FntPrint(f,"%s\n%s",intro_title(&in),intro_subtitle(&in));FntFlush(f);
        DrawSync(0);intro_tick(&in,0);
    }
    VSync(0);intro_tile(0,0,320,240,3,4,11);DrawSync(0);
    PutDrawEnv(&restore_draw);
}

void moko_sprite_init(void){
    GetTimInfo((const uint32_t *)moko_tim,&moko_image);
    LoadImage(moko_image.prect,moko_image.paddr);
    if(moko_image.mode&0x8)LoadImage(moko_image.crect,moko_image.caddr);
    DrawSync(0);
    moko_ready=1;
    play_boot_intro();
}

void moko_sprite_draw(int x,int y,int facing,int walk_tick,int invuln,int anim_tick,uint32_t *ot,char **next_packet){
    SPRT *spr;
    DR_TPAGE *page;
    int moving=(walk_tick>0);
    int pose=moving ? 1+((walk_tick/7)&1) : 0;
    int frame=(facing?0:3)+pose;
    int bob=moving ? ((walk_tick/7)&1) : ((anim_tick/24)&1);
    if(!moko_ready)return;
    if(invuln>0&&((anim_tick/3)&1))return;
    spr=(SPRT *)(*next_packet);
    setSprt(spr);
    setXY0(spr,x,y-bob);
    setWH(spr,16,24);
    setUV0(spr,frame*16,0);
    setRGB0(spr,128,128,128);
    addPrim(ot,spr);
    *next_packet+=sizeof(SPRT);
    page=(DR_TPAGE *)(*next_packet);
    setDrawTPage(page,0,0,getTPage(2,0,moko_image.prect->x,moko_image.prect->y));
    addPrim(ot,page);
    *next_packet+=sizeof(DR_TPAGE);
}
