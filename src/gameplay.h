#ifndef MOKO_GAMEPLAY_H
#define MOKO_GAMEPLAY_H

typedef struct {
    int dash_timer;
    int dash_cooldown;
    int focus;
    int combo;
    int combo_timer;
    int room_time;
    int deaths;
} MokoGameplay;

void gameplay_reset(MokoGameplay *g);
void gameplay_tick(MokoGameplay *g, int moving);
int gameplay_try_dash(MokoGameplay *g);
void gameplay_reward(MokoGameplay *g, int amount);
int gameplay_score_bonus(const MokoGameplay *g);

#endif
