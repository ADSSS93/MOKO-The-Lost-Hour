#include "gameplay.h"

void gameplay_reset(MokoGameplay *g){
    g->dash_timer=0;
    g->dash_cooldown=0;
    g->focus=100;
    g->combo=0;
    g->combo_timer=0;
    g->room_time=0;
    g->deaths=0;
}

void gameplay_tick(MokoGameplay *g,int moving){
    g->room_time++;
    if(g->dash_timer>0)g->dash_timer--;
    if(g->dash_cooldown>0)g->dash_cooldown--;
    if(g->combo_timer>0){
        g->combo_timer--;
        if(g->combo_timer==0)g->combo=0;
    }
    if(!moving&&g->focus<100&&((g->room_time&3)==0))g->focus++;
}

int gameplay_try_dash(MokoGameplay *g){
    if(g->dash_cooldown||g->focus<20)return 0;
    g->focus-=20;
    g->dash_timer=10;
    g->dash_cooldown=28;
    return 1;
}

void gameplay_reward(MokoGameplay *g,int amount){
    (void)amount;
    if(g->combo<8)g->combo++;
    g->combo_timer=180;
    if(g->focus<95)g->focus+=5;else g->focus=100;
}

int gameplay_score_bonus(const MokoGameplay *g){
    return g->combo*25;
}
