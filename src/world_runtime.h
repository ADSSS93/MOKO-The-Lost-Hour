#ifndef MOKO_WORLD_RUNTIME_H
#define MOKO_WORLD_RUNTIME_H
#include "ambient.h"
#include "enemies.h"
#include "npc.h"
typedef struct { MokoAmbient ambient; MokoEnemies enemies; int npc_nearby; int last_enemy_hit; uint8_t room_clear_rewarded[5]; int combat_notice_timer; int combat_notice_room; int pending_combat_reward; } MokoWorldRuntime;
void world_runtime_bind_adventure(void *adventure);
void world_runtime_reset(MokoWorldRuntime *w,int room);
void world_runtime_tick(MokoWorldRuntime *w,int room,int px,int py);
int world_runtime_touch_enemy(const MokoWorldRuntime *w,int room,int px,int py);
int world_runtime_dash(MokoWorldRuntime *w,int room,int px,int py,int facing);
int world_runtime_near_npc(MokoWorldRuntime *w,int room,int px,int py,int radius);
int world_runtime_room_remaining(const MokoWorldRuntime *w,int room);
int world_runtime_room_clear_reward(MokoWorldRuntime *w,int room);
int world_runtime_take_combat_reward(MokoWorldRuntime *w);
int world_runtime_defeats(const MokoWorldRuntime *w);
int world_runtime_boss_active(const MokoWorldRuntime *w);
int world_runtime_boss_hp(const MokoWorldRuntime *w);
int world_runtime_boss_max_hp(const MokoWorldRuntime *w);
const MokoNpcDef *world_runtime_npc(const MokoWorldRuntime *w);
#endif
