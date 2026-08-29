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
typedef enum { STATE_TITLE, STATE_PLAY, STATE_PAUSE, STATE_DIALOGUE, STATE_GAMEOVER, STATE_ENDING } GameState;
static DB db[2]; static int active=0,font_id; static char *next_packet; static char pad_buffer[2][34];
static uint16_t old_btn=0xffff; static GameState state=STATE_TITLE;
static int px=20,py=190,room=0,shards=0,timer_frames=60*60*5,health=3,anim_tick=0,walk_tick=0,facing=1;
static uint8_t shard_taken[4]={0,0,0,0},puzzle_done[4]={0,0,0,0};
static int switch_a=0,switch_b=0,dialogue_id=0,invuln=0;

static void init(void){ResetGraph(0);InitGeom();EnterCriticalSection();InitPAD(pad_buffer[0],34,pad_buffer[1],34);StartPAD();ChangeClearPAD(0);ExitCriticalSection();SetDefDispEnv(&db[0].disp,0,0,SCREEN_W,SCREEN_H);SetDefDrawEnv(&db[0].draw,0,SCREEN_H,SCREEN_W,SCREEN_H);SetDefDispEnv(&db[1].disp,0,SCREEN_H,SCREEN_W,SCREEN_H);SetDefDrawEnv(&db[1].draw,0,0,SCREEN_W,SCREEN_H);db[0].draw.isbg=db[1].draw.isbg=1;setRGB0(&db[0].draw,6,7,15);setRGB0(&db[1].draw,6,7,15);PutDispEnv(&db[0].disp);PutDrawEnv(&db[0].draw);SetDispMask(1);FntLoad(960,0);font_id=FntOpen(8,8,304,54,0,256);ClearOTagR(db[0].ot,OT_SIZE);next_packet=db[0].packets;}
static void rect(int x,int y,int w,int h,int r,int g,int b){TILE*p=(TILE*)next_packet;setTile(p);setXY0(p,x,y);setWH(p,w,h);setRGB0(p,r,g,b);addPrim(db[active].ot,p);next_packet+=sizeof(TILE);}
static void frame(void){DrawSync(0);VSync(0);PutDispEnv(&db[active].disp);PutDrawEnv(&db[active].draw);DrawOTag(db[active].ot+OT_SIZE-1);active^=1;ClearOTagR(db[active].ot,OT_SIZE);next_packet=db[active].packets;anim_tick++;}
static uint16_t buttons(void){PADTYPE*p=(PADTYPE*)pad_buffer[0];return p->stat==0?p->btn:0xffff;}
static int pressed(uint16_t n,uint16_t k){return !(n&k)&&(old_btn&k);} static int hit(int ax,int ay,int aw,int ah,int bx,int by,int bw,int bh){return ax<bx+bw&&ax+aw>bx&&ay<by+bh&&ay+ah>by;}
static void say(int id){dialogue_id=id;state=STATE_DIALOGUE;}
static void reset_game(void){int i;px=20;py=190;room=0;shards=0;health=3;timer_frames=60*60*5;switch_a=switch_b=0;invuln=0;for(i=0;i<4;i++){shard_taken[i]=0;puzzle_done[i]=0;}state=STATE_PLAY;say(1);}
static void draw_moko(void){int bob=((walk_tick/6)&1),blink=(invuln>0&&((anim_tick/3)&1));if(blink)return;rect(px+2,py+2-bob,8,8,232,205,145);rect(px,py+9-bob,12,8,92,76,112);rect(px+2,py+17-bob,3,3,50,45,65);rect(px+7,py+17-bob,3,3,50,45,65);rect(px+(facing?8:3),py+4-bob,2,2,22,20,28);}
static void draw_shard(int sx,int sy){int pulse=(anim_tick/8)&3;rect(sx-2-pulse,sy-5-pulse,13+pulse*2,24+pulse*2,25,75,90);rect(sx,sy,9,14,80,215,245);rect(sx+2,sy-4,5,4,190,250,255);rect(sx+3,sy+3,3,6,230,255,255);}
static void atmosphere(void){int i,off=(anim_tick/2)%40;for(i=0;i<8;i++){int x=(i*47+off)%320,y=70+((i*29+anim_tick/4)%140);rect(x,y,1,1,70,75,100);}if(room==4){for(i=0;i<6;i++){int x=130+i*10,y=88+((anim_tick+i*9)%45);rect(x,y,2,2,170,125,85);}}}
static void room_art(void){int r=16,g=18,b=32;if(room==1){r=26;g=15;b=34;}else if(room==2){r=12;g=28;b=29;}else if(room==3){r=30;g=22;b=12;}else if(room==4){r=25;g=8;b=10;}rect(0,GAME_TOP,320,182,r,g,b);atmosphere();rect(0,222,320,18,42,38,52);
 if(room==0){rect(18,85,284,4,48,52,76);rect(30,96,55,38,32,37,58);rect(235,96,55,38,32,37,58);rect(112,180,18,28,85,100,150);rect(116,185,10,8,180,200,230);rect(156,76,8,8,115,125,160);}
 if(room==1){rect(0,94,320,4,66,38,72);rect(145,176,18,46,170,45,65);rect(220,195,18,27,170,45,65);rect(70,190,14,14,switch_a?60:150,switch_a?210:60,70);rect(270,110,14,14,switch_b?60:150,switch_b?210:60,70);rect(35,120,65,3,120,60,105);}
 if(room==2){rect(20,72,80,55,28,65,58);rect(125,95,12,127,45,150,115);rect(260,130,12,92,45,150,115);rect(45,82,30,20,70,125,110);rect(175,82,45,28,40,78,70);}
 if(room==3){rect(15,78,290,4,95,70,38);rect(90,190,45,6,215,130,35);rect(200,110,45,6,215,130,35);rect(150,84,22,22,180,115,35);rect(25,145,38,38,65,50,34);rect(268,85,25,92,80,58,35);}
 if(room==4){rect(96,70,128,5,80,42,50);rect(128,82,64,64,90,55,65);rect(144,98,32,32,205,185,120);rect(157,104,5,20,55,32,36);rect(150,111,20,5,55,32,36);}
 if(room<4&&!shard_taken[room]&&puzzle_done[room]){int sx=250-(room*35),sy=90+(room*28);draw_shard(sx,sy);}draw_moko();}
static void interact(uint16_t now){if(!pressed(now,PAD_CROSS))return;if(room==0&&hit(px,py,12,18,105,170,32,45)){puzzle_done[0]=1;say(2);return;}if(room==1){if(hit(px,py,12,18,60,180,34,34))switch_a=1;if(hit(px,py,12,18,260,100,34,34))switch_b=1;if(switch_a&&switch_b&&!puzzle_done[1]){puzzle_done[1]=1;say(3);return;}}if(room==2&&hit(px,py,12,18,35,72,50,40)){if(shards>=2){puzzle_done[2]=1;say(4);}else say(7);return;}if(room==3&&hit(px,py,12,18,140,74,42,42)){if(shards>=3){puzzle_done[3]=1;say(5);}else say(7);return;}if(room==4&&hit(px,py,12,18,120,74,80,80)&&shards<4)say(6);}
static void update_play(uint16_t now){int ox=px,oy=py,moved=0;if(!(now&PAD_LEFT)){px-=2;facing=0;moved=1;}if(!(now&PAD_RIGHT)){px+=2;facing=1;moved=1;}if(!(now&PAD_UP)){py-=2;moved=1;}if(!(now&PAD_DOWN)){py+=2;moved=1;}if(moved)walk_tick++;if(px<0){if(room>0){room--;px=306;}else px=0;}if(px>308){if(room<4){room++;px=2;}else px=308;}if(py<GAME_TOP+4)py=GAME_TOP+4;if(py>204)py=204;if(room==1&&(hit(px,py,12,18,145,176,18,46)||hit(px,py,12,18,220,195,18,27))){px=ox;py=oy;}if(room==2&&(hit(px,py,12,18,125,95,12,127)||hit(px,py,12,18,260,130,12,92))){px=ox;py=oy;}interact(now);if(room<4&&!shard_taken[room]&&puzzle_done[room]){int sx=250-(room*35),sy=90+(room*28);if(hit(px,py,12,18,sx-4,sy-5,17,23)){shard_taken[room]=1;shards++;say(8);}}if(invuln>0)invuln--;if(room==3&&invuln==0&&hit(px,py,12,18,90,184,45,18)){health--;invuln=60;px=30;py=190;if(health<=0)state=STATE_GAMEOVER;}if(room==4&&shards==4&&hit(px,py,12,18,125,78,70,72))state=STATE_ENDING;if(pressed(now,PAD_START))state=STATE_PAUSE;if(timer_frames>0)timer_frames--;else state=STATE_GAMEOVER;}
static void draw_hud(void){static const char*n[]={"SILENT STATION","BACKWARD STREET","HOUSE WITHOUT MORNING","CLOCKWORKS","CLOCK CHAMBER"};int s=timer_frames/60;FntPrint(font_id,"MOKO  %02d:%02d  SHARDS %d/4  HP %d\n%s  CROSS: INTERACT",s/60,s%60,shards,health,n[room]);FntFlush(font_id);}
static void draw_dialogue(void){room_art();rect(12,164,296,64,8,8,18);rect(15,167,290,2,75,95,125);if(dialogue_id==1)FntPrint(font_id,"A voice: The hour was broken.\nFind what you forgot.\nCROSS - continue");else if(dialogue_id==2)FntPrint(font_id,"The station clock wakes.\nA memory takes shape.\nCROSS - continue");else if(dialogue_id==3)FntPrint(font_id,"Both street signals glow.\nTime releases another memory.\nCROSS - continue");else if(dialogue_id==4)FntPrint(font_id,"The house recognizes you.\nThe locked morning returns.\nCROSS - continue");else if(dialogue_id==5)FntPrint(font_id,"The machine accepts the memories.\nThe final shard is exposed.\nCROSS - continue");else if(dialogue_id==6)FntPrint(font_id,"The Clock Chamber is incomplete.\nFour memories must become one.\nCROSS - continue");else if(dialogue_id==7)FntPrint(font_id,"Something is missing.\nRecover the earlier memories first.\nCROSS - continue");else FntPrint(font_id,"MEMORY SHARD RECOVERED.\nThe lost hour grows clearer.\nCROSS - continue");FntFlush(font_id);}
int main(void){init();for(;;){uint16_t now=buttons();if(state==STATE_TITLE){int glow=35+((anim_tick/4)%30);rect(0,0,320,240,7,8,20);rect(54,65,212,58,glow,24,48);rect(75,135,170,2,80,100,140);FntPrint(font_id,"\n\n      M O K O\n   THE LOST HOUR\n\n  START - BEGIN\n  Recover the four memories.");FntFlush(font_id);if(pressed(now,PAD_START)||pressed(now,PAD_CROSS))reset_game();}else if(state==STATE_PLAY){update_play(now);room_art();draw_hud();}else if(state==STATE_DIALOGUE){draw_dialogue();if(pressed(now,PAD_CROSS))state=STATE_PLAY;}else if(state==STATE_PAUSE){room_art();rect(80,90,160,55,8,8,18);FntPrint(font_id,"PAUSED\nSTART - RESUME");FntFlush(font_id);if(pressed(now,PAD_START))state=STATE_PLAY;}else if(state==STATE_GAMEOVER){rect(0,0,320,240,24,5,10);FntPrint(font_id,"\n\n   THE HOUR IS LOST\n\n   CROSS - TRY AGAIN\n   START - TITLE");FntFlush(font_id);if(pressed(now,PAD_CROSS))reset_game();if(pressed(now,PAD_START))state=STATE_TITLE;}else{int pulse=80+((anim_tick/3)%70);rect(0,0,320,240,8,22,28);rect(120,65,80,80,pulse,100,75);FntPrint(font_id,"\n\n   THE CLOCK REMEMBERS\n\nMoko restores the missing hour.\nThe four memories become one.\n\n       THE END\n\n   START - TITLE");FntFlush(font_id);if(pressed(now,PAD_START))state=STATE_TITLE;}old_btn=now;frame();}return 0;}
