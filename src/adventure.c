#include "adventure.h"
static int event_item(int id){switch(id){case 0:return ITEM_TICKET;case 7:return ITEM_LETTER;case 8:return ITEM_BLUE_KEY;case 10:return ITEM_UMBRELLA;case 12:return ITEM_PORTRAIT;case 13:return ITEM_TEACUP;case 18:case 19:return ITEM_TINY_GEAR;case 20:return ITEM_LUNCHBOX;case 22:return ITEM_LOOSE_COG;default:return -1;}}
void adventure_reset(MokoAdventure*a){quests_reset(&a->quests);world_events_reset(&a->world);items_reset(&a->inventory);a->last_event=-1;a->last_reward=0;a->notice_timer=0;a->dash_count=0;a->current_room=0;world_events_enter_room(&a->world,0,&a->quests);}
void adventure_tick(MokoAdventure*a,int room,int shards,int echoes,int combo,int health,int focus){if(room!=a->current_room){a->current_room=room;world_events_enter_room(&a->world,room,&a->quests);}quests_tick(&a->quests,room,shards,echoes,combo,health,focus);if(a->notice_timer>0)a->notice_timer--;}
int adventure_interact(MokoAdventure*a,int room,int px,int py){int id=world_events_near(&a->world,room,px,py,24),item,reward;if(id<0||!world_event_unlocked(&a->world,&a->quests,id))return 0;reward=world_events_interact(&a->world,&a->quests,room,px,py,24);if(!reward)return 0;item=event_item(id);if(item>=0)items_add(&a->inventory,item,1);a->last_event=id;a->last_reward=reward>1?reward:0;a->notice_timer=150;return reward;}
void adventure_dash(MokoAdventure*a){a->dash_count++;quests_trigger(&a->quests,40);quests_add(&a->quests,40,1);quests_trigger(&a->quests,41);quests_add(&a->quests,41,1);}
int adventure_completion(const MokoAdventure*a){return quests_completion(&a->quests);}
const char*adventure_notice(const MokoAdventure*a){const MokoWorldEventDef*d;if(a->last_event<0)return "";d=world_event_def(a->last_event);return d?d->label:"";}
int adventure_near_event(const MokoAdventure*a,int room,int px,int py,int radius){int id=world_events_near(&a->world,room,px,py,radius);return(id>=0&&world_event_unlocked(&a->world,&a->quests,id))?id:-1;}
int adventure_room_remaining(const MokoAdventure*a,int room){return world_events_remaining(&a->world,room);}
const MokoWorldEventDef*adventure_event(const MokoAdventure*a,int index){(void)a;return world_event_def(index);}
int adventure_item_count(const MokoAdventure*a,int item){return(item>=0&&item<ITEM_COUNT)?a->inventory.count[item]:0;}
