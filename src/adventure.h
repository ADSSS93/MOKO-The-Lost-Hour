#ifndef MOKO_ADVENTURE_H
#define MOKO_ADVENTURE_H
#include <stdint.h>
#include "quests.h"
#include "world_events.h"
#include "items.h"
typedef struct { MokoQuests quests; MokoWorldEvents world; MokoInventory inventory; int last_event; int last_reward; int notice_timer; int dash_count; int current_room; } MokoAdventure;
void adventure_reset(MokoAdventure *a);
void adventure_tick(MokoAdventure *a,int room,int shards,int echoes,int combo,int health,int focus);
int adventure_interact(MokoAdventure *a,int room,int px,int py);
void adventure_dash(MokoAdventure *a);
int adventure_completion(const MokoAdventure *a);
const char *adventure_notice(const MokoAdventure *a);
int adventure_near_event(const MokoAdventure *a,int room,int px,int py,int radius);
int adventure_room_remaining(const MokoAdventure *a,int room);
const MokoWorldEventDef *adventure_event(const MokoAdventure *a,int index);
int adventure_item_count(const MokoAdventure *a,int item);
#endif
