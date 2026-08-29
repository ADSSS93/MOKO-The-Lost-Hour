#include "world_runtime.h"
#include "adventure.h"
static MokoAdventure*bound_adventure=0;
void world_runtime_bind_adventure(void*a){bound_adventure=(MokoAdventure*)a;}
void world_runtime_reset(MokoWorldRuntime*w,int room){int i;ambient_reset(&w->ambient,room);enemies_reset(&w->enemies);w->npc_nearby=-1;w->last_enemy_hit=-1;w->combat_notice_timer=0;w->combat_notice_room=-1;for(i=0;i<5;i++)w->room_clear_rewarded[i]=0;}
void world_runtime_tick(MokoWorldRuntime*w,int room,int px,int py){ambient_set_room(&w->ambient,room);ambient_tick(&w->ambient);enemies_tick(&w->enemies,room,px,py);w->npc_nearby=npc_near(room,px,py,24);if(w->combat_notice_timer>0)w->combat_notice_timer--;if(bound_adventure)adventure_challenge_position(bound_adventure,room,px,py,0);}
int world_runtime_touch_enemy(const MokoWorldRuntime*w,int room,int px,int py){return enemies_touch(&w->enemies,room,px,py,14);}
int world_runtime_room_remaining(const MokoWorldRuntime*w,int room){return enemies_room_remaining(&w->enemies,room);}
int world_runtime_room_clear_reward(MokoWorldRuntime*w,int room){int reward,quest;if(room<0||room>=5||w->room_clear_rewarded[room]||!enemies_room_cleared(&w->enemies,room))return 0;w->room_clear_rewarded[room]=1;w->combat_notice_room=room;w->combat_notice_timer=150;quest=48+room;reward=quests_reward(quest);if(bound_adventure){quests_trigger(&bound_adventure->quests,quest);adventure_story_clear(bound_adventure,quest);}return reward;}
int world_runtime_dash(MokoWorldRuntime*w,int room,int px,int py,int facing){if(bound_adventure)adventure_challenge_position(bound_adventure,room,px,py,1);w->last_enemy_hit=enemies_dash_hit(&w->enemies,room,px,py,facing);if(w->last_enemy_hit>=0)world_runtime_room_clear_reward(w,room);return w->last_enemy_hit;}
int world_runtime_near_npc(MokoWorldRuntime*w,int room,int px,int py,int radius){w->npc_nearby=npc_near(room,px,py,radius);return w->npc_nearby;}
int world_runtime_defeats(const MokoWorldRuntime*w){return enemies_defeats(&w->enemies);}
const MokoNpcDef*world_runtime_npc(const MokoWorldRuntime*w){return npc_get(w->npc_nearby);}
