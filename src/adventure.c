#include "adventure.h"
void adventure_reset(MokoAdventure*a){quests_reset(&a->quests);world_events_reset(&a->world);a->last_event=-1;a->last_reward=0;a->notice_timer=0;a->dash_count=0;a->current_room=0;world_events_enter_room(&a->world,0,&a->quests);}
void adventure_tick(MokoAdventure*a,int room,int shards,int echoes,int combo,int health,int focus){if(room!=a->current_room){a->current_room=room;world_events_enter_room(&a->world,room,&a->quests);}quests_tick(&a->quests,room,shards,echoes,combo,health,focus);if(a->notice_timer>0)a->notice_timer--;}
int adventure_interact(MokoAdventure*a,int room,int px,int py){int id=world_events_near(&a->world,room,px,py,24);int reward;if(id<0)return 0;reward=world_events_interact(&a->world,&a->quests,room,px,py,24);if(!reward)return 0;a->last_event=id;a->last_reward=reward>1?reward:0;a->notice_timer=150;return reward;}
void adventure_dash(MokoAdventure*a){a->dash_count++;quests_trigger(&a->quests,40);quests_add(&a->quests,40,1);quests_trigger(&a->quests,41);quests_add(&a->quests,41,1);}
int adventure_completion(const MokoAdventure*a){return quests_completion(&a->quests);}
const char*adventure_notice(const MokoAdventure*a){const MokoWorldEventDef*d;if(a->last_event<0)return "";d=world_event_def(a->last_event);return d?d->label:"";}
int adventure_near_event(const MokoAdventure*a,int room,int px,int py,int radius){return world_events_near(&a->world,room,px,py,radius);}
int adventure_room_remaining(const MokoAdventure*a,int room){return world_events_remaining(&a->world,room);}
const MokoWorldEventDef*adventure_event(const MokoAdventure*a,int index){(void)a;return world_event_def(index);}
