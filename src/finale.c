#include "finale.h"

void finale_reset(MokoFinale *f){
 int i; for(i=0;i<4;i++)f->socket[i]=0;
 f->charge=0; f->phase=FINALE_DORMANT; f->phase_timer=0;
 f->sweep_tick=0; f->stability=0; f->perfect_chain=1;
}

void finale_begin(MokoFinale *f,int shards){
 if(shards>=4&&f->phase==FINALE_DORMANT){f->phase=FINALE_RESTORE;f->phase_timer=0;f->sweep_tick=0;f->stability=0;}
}

int finale_activate_socket(MokoFinale *f,int index,int shards){
 if(shards<4||f->phase!=FINALE_RESTORE||index<0||index>3||f->socket[index])return 0;
 f->socket[index]=1; f->charge++; f->stability+=20;
 if(f->charge>=4){f->phase=FINALE_STABILIZE;f->phase_timer=360;f->stability=40;}
 return 1;
}

void finale_tick(MokoFinale *f,int dashing){
 if(f->phase==FINALE_DORMANT||f->phase==FINALE_COMPLETE)return;
 f->sweep_tick++;
 if(f->phase==FINALE_RESTORE){if(f->stability>0&&(f->sweep_tick%90)==0)f->stability--;return;}
 if(f->phase==FINALE_STABILIZE){
  if(f->phase_timer>0)f->phase_timer--;
  if(dashing){if(f->stability<100)f->stability+=2;}
  else if((f->sweep_tick%6)==0&&f->stability>0)f->stability--;
  if(f->stability<=0){f->stability=20;f->phase_timer+=90;f->perfect_chain=0;}
  if(f->phase_timer<=0){f->phase=FINALE_COMPLETE;f->stability=100;}
 }
}

int finale_sweep_x(const MokoFinale *f){int span=252,t=(f->sweep_tick*3)%(span*2);if(t>span)t=span*2-t;return 34+t;}
int finale_sweep_y(const MokoFinale *f){int span=112,t=(f->sweep_tick*2+37)%(span*2);if(t>span)t=span*2-t;return 82+t;}
int finale_hazard_active(const MokoFinale *f){return f->phase==FINALE_RESTORE||f->phase==FINALE_STABILIZE;}
int finale_complete(const MokoFinale *f){return f->phase==FINALE_COMPLETE;}
int finale_score_bonus(const MokoFinale *f){int b=f->charge*125+f->stability*5;if(f->perfect_chain&&f->phase==FINALE_COMPLETE)b+=1000;return b;}
