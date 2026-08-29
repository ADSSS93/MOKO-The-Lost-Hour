#include "gameplay.h"

static int clamp100(int v){return v<0?0:(v>100?100:v);}

void gameplay_reset(MokoGameplay *g){
    g->dash_timer=0;
    g->dash_cooldown=0;
    g->focus=100;
    g->combo=0;
    g->combo_timer=0;
    g->room_time=0;
    g->deaths=0;
    g->echoes=0;
    g->shards=0;
    g->best_combo=0;
}

void gameplay_tick(MokoGameplay *g,int moving){
    g->room_time++;
    if(g->dash_timer>0)g->dash_timer--;
    if(g->dash_cooldown>0)g->dash_cooldown--;
    if(g->combo_timer>0){
        g->combo_timer--;
        if(g->combo_timer==0)g->combo=0;
    }
    /* Focus regenerates faster while standing still, encouraging deliberate
       movement instead of permanent dashing. */
    if(g->focus<100){
        if(!moving&&((g->room_time&1)==0))g->focus++;
        else if(moving&&((g->room_time&7)==0))g->focus++;
    }
}

int gameplay_try_dash(MokoGameplay *g){
    if(g->dash_cooldown>0||g->focus<20)return 0;
    g->focus-=20;
    g->dash_timer=10;
    g->dash_cooldown=28;
    return 1;
}

int gameplay_move_speed(const MokoGameplay *g){
    return g->dash_timer>0?5:2;
}

int gameplay_dash_active(const MokoGameplay *g){
    return g->dash_timer>0;
}

void gameplay_reward(MokoGameplay *g,int amount){
    int gain=amount>150?10:5;
    if(g->combo<8)g->combo++;
    if(g->combo>g->best_combo)g->best_combo=g->combo;
    g->combo_timer=180;
    g->focus=clamp100(g->focus+gain);
}

void gameplay_echo_collected(MokoGameplay *g){
    g->echoes++;
    gameplay_reward(g,75);
}

void gameplay_shard_collected(MokoGameplay *g){
    g->shards++;
    gameplay_reward(g,250);
}

void gameplay_player_hurt(MokoGameplay *g){
    g->combo=0;
    g->combo_timer=0;
    if(g->focus>15)g->focus-=15;else g->focus=0;
}

int gameplay_score_bonus(const MokoGameplay *g){
    return g->combo*25;
}

int gameplay_focus_percent(const MokoGameplay *g){
    return clamp100(g->focus);
}
