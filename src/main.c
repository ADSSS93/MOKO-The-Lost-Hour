#include <stdio.h>
#include <stdlib.h>
#include <psxgpu.h>
#include <psxgte.h>
#include <psxpad.h>
#include <psxetc.h>

#define OT_LEN 8
#define PACKET_LEN 32768
#define SCREEN_W 320
#define SCREEN_H 240

typedef struct { DISPENV disp; DRAWENV draw; u_long ot[1 << OT_LEN]; char packets[PACKET_LEN]; } DB;
static DB db[2]; static int active=0; static char *next_packet;
static int player_x=150, player_y=180;

static void init(void){
 ResetGraph(0); InitGeom(); InitPAD(NULL,0,NULL,0); StartPAD(); ChangeClearPAD(0);
 SetDefDispEnv(&db[0].disp,0,0,SCREEN_W,SCREEN_H); SetDefDrawEnv(&db[0].draw,0,SCREEN_H,SCREEN_W,SCREEN_H);
 SetDefDispEnv(&db[1].disp,0,SCREEN_H,SCREEN_W,SCREEN_H); SetDefDrawEnv(&db[1].draw,0,0,SCREEN_W,SCREEN_H);
 db[0].draw.isbg=db[1].draw.isbg=1; setRGB0(&db[0].draw,8,8,18); setRGB0(&db[1].draw,8,8,18);
 PutDispEnv(&db[0].disp); PutDrawEnv(&db[0].draw); SetDispMask(1);
 FntLoad(960,0); FntOpen(8,8,304,64,0,256);
}
static void rect(int x,int y,int w,int h,int r,int g,int b){ TILE *p=(TILE*)next_packet; setTile(p); setXY0(p,x,y); setWH(p,w,h); setRGB0(p,r,g,b); addPrim(db[active].ot,p); next_packet+=sizeof(TILE); }
static void frame(void){ DrawSync(0); VSync(0); PutDispEnv(&db[active].disp); PutDrawEnv(&db[active].draw); DrawOTag(db[active].ot+(1<<OT_LEN)-1); active^=1; ClearOTagR(db[active].ot,1<<OT_LEN); next_packet=db[active].packets; }
int main(void){
 init(); ClearOTagR(db[active].ot,1<<OT_LEN); next_packet=db[active].packets;
 int clock=60*60; int crystals=0;
 while(1){
  u_long pad=PadRead(0); if(pad&PADLleft) player_x-=2; if(pad&PADLright) player_x+=2; if(pad&PADLup) player_y-=2; if(pad&PADLdown) player_y+=2;
  if(player_x<8)player_x=8; if(player_x>300)player_x=300; if(player_y<70)player_y=70; if(player_y>220)player_y=220;
  if(clock>0) clock--;
  rect(0,64,320,176,12,14,28); rect(40,120,70,8,55,45,70); rect(190,150,90,8,55,45,70); rect(player_x,player_y,12,18,220,190,120);
  FntPrint("MOKO: THE LOST HOUR\nTIME %02d:%02d   MEMORY SHARDS %d/4\nD-PAD MOVE   START: PAUSE\nFind the four memory shards before the hour is lost.",clock/3600,(clock/60)%60,crystals); FntFlush(-1);
  frame();
 }
 return 0;
}
