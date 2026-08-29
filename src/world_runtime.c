#include "world_runtime.h"
void world_runtime_reset(MokoWorldRuntime*w,int room){ambient_reset(&w->ambient,room);enemies_reset(&w->enemies);w->npc_nearby=-1;w->last_enemy_hit=-1;}
void world_runtime_tick(MokoWorldRuntime*w,int room,int px,int py){ambient_set_room(&w->ambient,room);ambient_tick(&w->ambient);enemies_tick(&w->enemies,room,px,py);w->npc_nearby=npc_near(room,px,py,24);}
int world_runtime_touch_enemy(const MokoWorldRuntime*w,int room,int px,int py){return enemies_touch(&w->enemies,room,px,py,14);}
int world_runtime_dash(MokoWorldRuntime*w,int room,int px,int py,int facing){w->last_enemy_hit=enemies_dash_hit(&w->enemies,room,px,py,facing);return w->last_enemy_hit;}
int world_runtime_near_npc(MokoWorldRuntime*w,int room,int px,int py,int radius){w->npc_nearby=npc_near(room,px,py,radius);return w->npc_nearby;}
const MokoNpcDef*world_runtime_npc(const MokoWorldRuntime*w){return npc_get(w->npc_nearby);}
