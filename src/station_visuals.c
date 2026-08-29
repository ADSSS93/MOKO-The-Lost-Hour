#include <psxgpu.h>
#include "station_visuals.h"

static void tile(uint32_t *ot,char **packet,int depth,int x,int y,int w,int h,int r,int g,int b){TILE*p=(TILE*)*packet;setTile(p);setXY0(p,x,y);setWH(p,w,h);setRGB0(p,r,g,b);addPrim(ot+depth,p);*packet+=sizeof(TILE);}
static void line(uint32_t *ot,char **packet,int depth,int x,int y,int w,int h,int r,int g,int b){tile(ot,packet,depth,x,y,w,h,r,g,b);}
static void lamp(uint32_t *ot,char **p,int x,int y,int glow){tile(ot,p,2,x-5,y-3,11,7,70+glow,62+glow,32);tile(ot,p,1,x-3,y-2,7,4,220,190,95);line(ot,p,2,x,y-13,1,10,72,76,88);}
static void clock_face(uint32_t *ot,char **p,int tick){int pulse=(tick/16)&1;tile(ot,p,2,142,69,36,36,31,36,49);tile(ot,p,1,146,73,28,28,185+pulse*10,174+pulse*8,137);tile(ot,p,1,149,76,22,22,35,39,48);line(ot,p,1,159,79,2,9,215,198,145);line(ot,p,1,160,87,8,2,215,198,145);tile(ot,p,1,158,86,4,4,230,210,155);}
static void bench(uint32_t *ot,char **p,int x,int y){tile(ot,p,2,x,y,48,5,72,66,62);tile(ot,p,2,x+2,y+7,44,5,88,76,65);line(ot,p,2,x+5,y+12,3,14,48,45,45);line(ot,p,2,x+39,y+12,3,14,48,45,45);line(ot,p,2,x+3,y+5,3,8,50,48,50);line(ot,p,2,x+42,y+5,3,8,50,48,50);}
static void poster(uint32_t *ot,char **p,int x,int y){tile(ot,p,2,x,y,25,34,62,56,69);tile(ot,p,1,x+2,y+2,21,30,25,48,62);tile(ot,p,1,x+6,y+7,13,2,185,161,95);tile(ot,p,1,x+5,y+13,15,2,92,138,146);tile(ot,p,1,x+8,y+19,9,8,112,55,75);}
void station_visuals_draw(int tick,uint32_t *ot,char **p){int i,blink=(tick/28)&1;
 /* far wall */
 tile(ot,p,6,0,58,320,164,9,14,28);tile(ot,p,5,0,63,320,8,22,31,49);tile(ot,p,5,0,174,320,20,18,24,37);
 /* tiled masonry */
 for(i=0;i<8;i++){line(ot,p,5,i*44-10,82,34,2,25,31,45);line(ot,p,5,i*44+11,112,34,2,22,28,42);line(ot,p,5,i*44-5,144,34,2,25,31,45);}
 /* tunnel openings */
 tile(ot,p,4,8,88,64,74,5,8,16);tile(ot,p,3,12,93,56,69,14,22,38);tile(ot,p,4,248,88,64,74,5,8,16);tile(ot,p,3,252,93,56,69,14,22,38);
 /* central station architecture */
 line(ot,p,3,80,92,160,4,73,76,82);line(ot,p,3,80,155,160,4,73,76,82);line(ot,p,3,84,96,4,59,54,58,68);line(ot,p,3,236,96,4,59,54,58,68);
 tile(ot,p,3,98,104,52,26,20,31,48);tile(ot,p,2,102,108,44,18,31,57,72);tile(ot,p,3,174,104,52,26,20,31,48);tile(ot,p,2,178,108,44,18,31,57,72);
 clock_face(ot,p,tick);
 /* sign */
 tile(ot,p,3,111,137,102,16,31,36,47);line(ot,p,2,116,141,92,2,171,151,91);line(ot,p,2,124,146,76,2,80,105,113);
 /* columns */
 tile(ot,p,3,75,91,9,103,50,55,66);tile(ot,p,2,77,94,3,96,83,84,87);tile(ot,p,3,236,91,9,103,50,55,66);tile(ot,p,2,238,94,3,96,83,84,87);
 /* platform */
 tile(ot,p,4,0,194,320,28,24,29,39);line(ot,p,3,0,194,320,4,113,101,72);line(ot,p,3,0,199,320,2,48,53,61);line(ot,p,3,0,218,320,4,85,72,54);for(i=0;i<11;i++)line(ot,p,3,i*32,204,21,1,43,48,57);
 /* track hints */
 line(ot,p,3,0,224,320,3,42,45,50);line(ot,p,3,0,234,320,3,58,57,54);for(i=0;i<12;i++)tile(ot,p,2,i*29,226,18,9,49,43,37);
 bench(ot,p,22,173);bench(ot,p,249,173);poster(ot,p,88,133);poster(ot,p,211,133);
 lamp(ot,p,52,84,blink*12);lamp(ot,p,268,84,blink*12);lamp(ot,p,105,84,0);lamp(ot,p,215,84,0);
 /* ticket machine / puzzle landmark */
 tile(ot,p,2,106,164,26,30,41,55,76);tile(ot,p,1,109,168,20,9,43,91,105);tile(ot,p,1,113,171,12,3,139,210,196);tile(ot,p,1,112,182,14,4,23,28,38);
 /* drifting time motes */
 for(i=0;i<5;i++){int x=(tick*(i+1)+i*67)%300+10;int y=76+((i*31+tick/3)%88);tile(ot,p,1,x,y,1+(i&1),1+(i&1),65,104,116);}
}
