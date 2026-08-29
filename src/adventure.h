#ifndef MOKO_ADVENTURE_H
#define MOKO_ADVENTURE_H
#include <stdint.h>
#include "quests.h"
#include "world_events.h"
typedef struct { MokoQuests quests; MokoWorldEvents world; int last_event; int last_reward; int notice_timer; int dash_count; } MokoAdventure;
void adventure_reset(MokoAdventure *a);
void adventure_tick(MokoAdventure *a,int room,int shards,int echoes,int combo,int health,int focus);
int adventure_interact(MokoAdventure *a,int room,int px,int py);
void adventure_dash(MokoAdventure *a);
int adventure_completion(const MokoAdventure *a);
const char *adventure_notice(const MokoAdventure *a);
#endif
