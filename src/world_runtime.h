#ifndef MOKO_WORLD_RUNTIME_H
#define MOKO_WORLD_RUNTIME_H
#include "ambient.h"
#include "enemies.h"
#include "npc.h"
typedef struct { MokoAmbient ambient; MokoEnemies enemies; int npc_nearby; int last_enemy_hit; } MokoWorldRuntime;
void world_runtime_bind_adventure(void *adventure);
void world_runtime_reset(MokoWorldRuntime *w,int room);
void world_runtime_tick(MokoWorldRuntime *w,int room,int px,int py);
int world_runtime_touch_enemy(const MokoWorldRuntime *w,int room,int px,int py);
int world_runtime_dash(MokoWorldRuntime *w,int room,int px,int py,int facing);
int world_runtime_near_npc(MokoWorldRuntime *w,int room,int px,int py,int radius);
const MokoNpcDef *world_runtime_npc(const MokoWorldRuntime *w);
#endif
