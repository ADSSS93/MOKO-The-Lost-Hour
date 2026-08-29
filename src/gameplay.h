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
    int echoes;
    int shards;
    int best_combo;
} MokoGameplay;

void gameplay_reset(MokoGameplay *g);
void gameplay_tick(MokoGameplay *g, int moving);
int gameplay_try_dash(MokoGameplay *g);
int gameplay_move_speed(const MokoGameplay *g);
int gameplay_dash_active(const MokoGameplay *g);
void gameplay_reward(MokoGameplay *g, int amount);
void gameplay_echo_collected(MokoGameplay *g);
void gameplay_shard_collected(MokoGameplay *g);
void gameplay_player_hurt(MokoGameplay *g);
int gameplay_score_bonus(const MokoGameplay *g);
int gameplay_focus_percent(const MokoGameplay *g);

#endif
