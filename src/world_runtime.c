#include "world_runtime.h"
#include "adventure.h"
static MokoAdventure*bound_adventure=0;
static const MokoEnemy*boss(const MokoWorldRuntime*w){int i;for(i=0;i<MOKO_ENEMY_COUNT;i++){const MokoEnemy*e=enemies_get(&w->enemies,i);if(e&&enemies_is_boss(e->kind))return e;}return 0;}
void world_runtime_bind_adventure(void*a){bound_adventure=(MokoAdventure*)a;}
void world_runtime_reset(MokoWorldRuntime*w,int room){int i;ambient_reset(&w->ambient,room);enemies_reset(&w->enemies);w->npc_nearby=-1;w->last_enemy_hit=-1;w->combat_notice_timer=0;w->combat_notice_room=-1;w->pending_combat_reward=0;for(i=0;i<5;i++)w->room_clear_rewarded[i]=0;}
void world_runtime_tick(MokoWorldRuntime*w,int room,int px,int py){ambient_set_room(&w->ambient,room);ambient_tick(&w->ambient);enemies_tick(&w->enemies,room,px,py);w->npc_nearby=npc_near(room,px,py,24);if(w->combat_notice_timer>0)w->combat_notice_timer--;if(bound_adventure){if(room>=0&&room<5)quests_trigger(&bound_adventure->quests,48+room);adventure_challenge_position(bound_adventure,room,px,py,0);}}
int world_runtime_touch_enemy(const MokoWorldRuntime*w,int room,int px,int py){return enemies_touch(&w->enemies,room,px,py,14);}
int world_runtime_room_remaining(const MokoWorldRuntime*w,int room){return enemies_room_remaining(&w->enemies,room);}
int world_runtime_room_clear_reward(MokoWorldRuntime*w,int room){int reward,quest;if(room<0||room>=5||w->room_clear_rewarded[room]||!enemies_room_cleared(&w->enemies,room))return 0;w->room_clear_rewarded[room]=1;w->combat_notice_room=room;w->combat_notice_timer=150;quest=48+room;reward=quests_reward(quest);w->pending_combat_reward+=reward;if(bound_adventure){if(!quests_is_clear(&bound_adventure->quests,quest))adventure_story_clear(bound_adventure,quest);bound_adventure->challenge_notice_quest=quest;bound_adventure->challenge_notice_timer=150;}return reward;}
int world_runtime_dash(MokoWorldRuntime*w,int room,int px,int py,int facing){const MokoEnemy*e;if(bound_adventure)adventure_challenge_position(bound_adventure,room,px,py,1);w->last_enemy_hit=enemies_dash_hit(&w->enemies,room,px,py,facing);if(w->last_enemy_hit>=0){e=enemies_get(&w->enemies,w->last_enemy_hit);if(e&&!e->active){w->pending_combat_reward+=enemies_is_boss(e->kind)?750:50;if(bound_adventure&&room>=0&&room<5){adventure_story_progress(bound_adventure,48+room,1);bound_adventure->challenge_notice_quest=48+room;bound_adventure->challenge_notice_timer=90;}}world_runtime_room_clear_reward(w,room);}return w->last_enemy_hit;}
int world_runtime_near_npc(MokoWorldRuntime*w,int room,int px,int py,int radius){w->npc_nearby=npc_near(room,px,py,radius);return w->npc_nearby;}
int world_runtime_take_combat_reward(MokoWorldRuntime*w){int reward=w->pending_combat_reward;w->pending_combat_reward=0;return reward;}
int world_runtime_defeats(const MokoWorldRuntime*w){return enemies_defeats(&w->enemies);}
int world_runtime_boss_active(const MokoWorldRuntime*w){const MokoEnemy*e=boss(w);return e&&e->active&&e->hit_cooldown<90;}
int world_runtime_boss_hp(const MokoWorldRuntime*w){const MokoEnemy*e=boss(w);return(e&&e->active)?e->hp:0;}
int world_runtime_boss_max_hp(const MokoWorldRuntime*w){const MokoEnemy*e=boss(w);return e?enemies_max_hp(e->kind):0;}
const MokoNpcDef*world_runtime_npc(const MokoWorldRuntime*w){return npc_get(w->npc_nearby);}
