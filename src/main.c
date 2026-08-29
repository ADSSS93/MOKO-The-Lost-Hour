#include <stdint.h>
#include <stdio.h>
#include <psxgpu.h>
#include <psxgte.h>
#include <psxpad.h>
#include <psxapi.h>
#include <psxetc.h>

#define OT_LEN 8
#define OT_SIZE (1 << OT_LEN)
#define PACKET_LEN 32768
#define SCREEN_W 320
#define SCREEN_H 240
#define GAME_TOP 58

typedef struct { DISPENV disp; DRAWENV draw; uint32_t ot[OT_SIZE]; char packets[PACKET_LEN]; } DB;
typedef enum { STATE_TITLE, STATE_PLAY, STATE_PAUSE, STATE_GAMEOVER, STATE_ENDING } GameState;

static DB db[2];
static int active=0, font_id;
static char *next_packet;
static char pad_buffer[2][34];
static uint16_t old_btn=0xffff;
static GameState state=STATE_TITLE;
static int px=20, py=190, room=0, shards=0, timer_frames=60*60*5, health=3;
static uint8_t shard_taken[4]={0,0,0,0};

static void init(void){
 ResetGraph(0); InitGeom();
 EnterCriticalSection(); InitPAD(pad_buffer[0],34,pad_buffer[1],34); StartPAD(); ChangeClearPAD(0); ExitCriticalSection();
 SetDefDispEnv(&db[0].disp,0,0,SCREEN_W,SCREEN_H); SetDefDrawEnv(&db[0].draw,0,SCREEN_H,SCREEN_W,SCREEN_H);
 SetDefDispEnv(&db[1].disp,0,SCREEN_H,SCREEN_W,SCREEN_H); SetDefDrawEnv(&db[1].draw,0,0,SCREEN_W,SCREEN_H);
 db[0].draw.isbg=db[1].draw.isbg=1; setRGB0(&db[0].draw,6,7,15); setRGB0(&db[1].draw,6,7,15);
 PutDispEnv(&db[0].disp); PutDrawEnv(&db[0].draw); SetDispMask(1); FntLoad(960,0); font_id=FntOpen(8,8,304,54,0,256);
 ClearOTagR(db[0].ot,OT_SIZE); next_packet=db[0].packets;
}
static void rect(int x,int y,int w,int h,int r,int g,int b){ TILE *p=(TILE*)next_packet; setTile(p); setXY0(p,x,y); setWH(p,w,h); setRGB0(p,r,g,b); addPrim(db[active].ot,p); next_packet+=sizeof(TILE); }
static void frame(void){ DrawSync(0); VSync(0); PutDispEnv(&db[active].disp); PutDrawEnv(&db[active].draw); DrawOTag(db[active].ot+OT_SIZE-1); active^=1; ClearOTagR(db[active].ot,OT_SIZE); next_packet=db[active].packets; }
static uint16_t buttons(void){ PADTYPE *p=(PADTYPE*)pad_buffer[0]; return p->stat==0 ? p->btn : 0xffff; }
static int pressed(uint16_t now,uint16_t key){ return !(now&key) && (old_btn&key); }
static int hit(int ax,int ay,int aw,int ah,int bx,int by,int bw,int bh){ return ax<bx+bw && ax+aw>bx && ay<by+bh && ay+ah>by; }
static void reset_game(void){ px=20;py=190;room=0;shards=0;health=3;timer_frames=60*60*5; shard_taken[0]=shard_taken[1]=shard_taken[2]=shard_taken[3]=0; state=STATE_PLAY; }
static void room_art(void){
 int r=16,g=18,b=32;
 if(room==1){r=26;g=15;b=34;} else if(room==2){r=12;g=28;b=29;} else if(room==3){r=30;g=22;b=12;} else if(room==4){r=25;g=8;b=10;}
 rect(0,GAME_TOP,320,182,r,g,b); rect(0,222,320,18,42,38,52);
 rect(35,105,72,7,65,58,78); rect(190,150,88,7,65,58,78);
 if(room<4 && !shard_taken[room]){ int sx=250-(room*35), sy=90+(room*28); rect(sx,sy,9,14,90,220,245); rect(sx+2,sy-3,5,3,180,250,255); }
 if(room==1){ rect(145,176,18,46,170,45,65); rect(220,195,18,27,170,45,65); }
 if(room==2){ rect(125,95,12,127,45,150,115); rect(260,130,12,92,45,150,115); }
 if(room==3){ rect(90,190,45,6,215,130,35); rect(200,110,45,6,215,130,35); }
 if(room==4){ rect(128,82,64,64,90,55,65); rect(144,98,32,32,205,185,120); }
 rect(px,py,12,18,220,190,120); rect(px+3,py+4,2,2,20,20,25); rect(px+8,py+4,2,2,20,20,25);
}
static void update_play(uint16_t now){
 int ox=px,oy=py;
 if(!(now&PAD_LEFT))px-=2; if(!(now&PAD_RIGHT))px+=2; if(!(now&PAD_UP))py-=2; if(!(now&PAD_DOWN))py+=2;
 if(px<0){ if(room>0){room--;px=306;}else px=0;} if(px>308){ if(room<4){room++;px=2;}else px=308;} if(py<GAME_TOP+4)py=GAME_TOP+4; if(py>222-18)py=204;
 if(room==1 && (hit(px,py,12,18,145,176,18,46)||hit(px,py,12,18,220,195,18,27))){px=ox;py=oy;}
 if(room==2 && (hit(px,py,12,18,125,95,12,127)||hit(px,py,12,18,260,130,12,92))){px=ox;py=oy;}
 if(room<4 && !shard_taken[room]){ int sx=250-(room*35),sy=90+(room*28); if(hit(px,py,12,18,sx-4,sy-5,17,23)){shard_taken[room]=1;shards++;} }
 if(room==3 && hit(px,py,12,18,90,184,45,18)){ health--; px=30;py=190; if(health<=0)state=STATE_GAMEOVER; }
 if(room==4 && shards==4 && hit(px,py,12,18,125,78,70,72)) state=STATE_ENDING;
 if(pressed(now,PAD_START))state=STATE_PAUSE;
 if(timer_frames>0)timer_frames--; else state=STATE_GAMEOVER;
}
static void draw_hud(void){
 static const char *names[]={"SILENT STATION","BACKWARD STREET","HOUSE WITHOUT MORNING","CLOCKWORKS","CLOCK CHAMBER"};
 int secs=timer_frames/60; FntPrint(font_id,"MOKO: THE LOST HOUR  %02d:%02d  SHARDS %d/4  HP %d\n%s",secs/60,secs%60,shards,health,names[room]); FntFlush(font_id);
}
int main(void){
 init();
 for(;;){
  uint16_t now=buttons();
  if(state==STATE_TITLE){ rect(0,0,320,240,7,8,20); rect(54,65,212,58,30,24,48); FntPrint(font_id,"\n\n      M O K O\n   THE LOST HOUR\n\n  START - BEGIN\n  Recover the four memories."); FntFlush(font_id); if(pressed(now,PAD_START)||pressed(now,PAD_CROSS))reset_game(); }
  else if(state==STATE_PLAY){ update_play(now); room_art(); draw_hud(); }
  else if(state==STATE_PAUSE){ room_art(); FntPrint(font_id,"PAUSED\nSTART - RESUME");FntFlush(font_id); if(pressed(now,PAD_START))state=STATE_PLAY; }
  else if(state==STATE_GAMEOVER){ rect(0,0,320,240,24,5,10); FntPrint(font_id,"\n\n   THE HOUR IS LOST\n\n   CROSS - TRY AGAIN\n   START - TITLE");FntFlush(font_id); if(pressed(now,PAD_CROSS))reset_game(); if(pressed(now,PAD_START))state=STATE_TITLE; }
  else { rect(0,0,320,240,8,22,28); FntPrint(font_id,"\n\n   THE CLOCK REMEMBERS\n\nMoko restores the missing hour.\nThe four memories become one.\n\n       THE END\n\n   START - TITLE");FntFlush(font_id); if(pressed(now,PAD_START))state=STATE_TITLE; }
  old_btn=now; frame();
 }
 return 0;
}
