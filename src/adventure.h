#ifndef MOKO_ADVENTURE_H
#define MOKO_ADVENTURE_H
#include <stdint.h>
#include "quests.h"
#include "world_events.h"
#include "items.h"
#include "journal.h"
typedef struct { MokoQuests quests; MokoWorldEvents world; MokoInventory inventory; MokoJournal journal; int last_event; int last_reward; int notice_timer; int dash_count; int current_room; int room_start_health; int challenge_notice_quest; int challenge_notice_timer; uint8_t challenge_flags[5]; uint8_t npc_met[10]; uint8_t npc_delivered[10]; } MokoAdventure;
void adventure_reset(MokoAdventure *a);
void adventure_tick(MokoAdventure *a,int room,int shards,int echoes,int combo,int health,int focus);
int adventure_interact(MokoAdventure *a,int room,int px,int py);
void adventure_dash(MokoAdventure *a);
void adventure_story_progress(MokoAdventure *a,int quest,int amount);
void adventure_story_clear(MokoAdventure *a,int quest);
void adventure_challenge_zone(MokoAdventure *a,int room,int zone,int dashing);
void adventure_challenge_position(MokoAdventure *a,int room,int px,int py,int dashing);
int adventure_npc_talk(MokoAdventure *a,int npc_index);
int adventure_npc_met(const MokoAdventure *a,int npc_index);
int adventure_npc_delivered(const MokoAdventure *a,int npc_index);
int adventure_npc_delivery_required(int npc_index);
int adventure_npc_reward(const MokoAdventure *a);
int adventure_completion(const MokoAdventure *a);
const char *adventure_notice(const MokoAdventure *a);
const char *adventure_challenge_notice(const MokoAdventure *a);
int adventure_near_event(const MokoAdventure *a,int room,int px,int py,int radius);
int adventure_room_remaining(const MokoAdventure *a,int room);
const MokoWorldEventDef *adventure_event(const MokoAdventure *a,int index);
int adventure_item_count(const MokoAdventure *a,int item);
void adventure_journal_sync(MokoAdventure *a);
void adventure_journal_move(MokoAdventure *a,int dir);
void adventure_journal_tab(MokoAdventure *a);
#endif
