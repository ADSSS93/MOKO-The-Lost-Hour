#include <stdint.h>
#include <psxgpu.h>
#include "moko_sprite.h"

extern const uint8_t moko_tim[];
static TIM_IMAGE moko_image;
static int moko_ready=0;

void moko_sprite_init(void){
    if(GetTimInfo((unsigned int *)moko_tim,&moko_image)!=0)return;
    LoadImage(moko_image.prect,moko_image.paddr);
    if(moko_image.mode&0x8)LoadImage(moko_image.crect,moko_image.caddr);
    DrawSync(0);
    moko_ready=1;
}

void moko_sprite_draw(int x,int y,int facing,int walk_tick,int invuln,int anim_tick,unsigned int *ot,char **next_packet){
    SPRT *spr;
    DR_TPAGE *page;
    int bob=(walk_tick/6)&1;
    if(!moko_ready)return;
    if(invuln>0&&((anim_tick/3)&1))return;
    spr=(SPRT *)(*next_packet);
    setSprt(spr);
    setXY0(spr,x,y-bob);
    setWH(spr,16,24);
    setUV0(spr,0,0);
    setRGB0(spr,128,128,128);
    (void)facing;
    addPrim(ot,spr);
    *next_packet+=sizeof(SPRT);
    page=(DR_TPAGE *)(*next_packet);
    setDrawTPage(page,0,0,getTPage(2,0,moko_image.prect->x,moko_image.prect->y));
    addPrim(ot,page);
    *next_packet+=sizeof(DR_TPAGE);
}
