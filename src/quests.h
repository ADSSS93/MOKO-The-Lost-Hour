#ifndef MOKO_QUESTS_H
#define MOKO_QUESTS_H
#include <stdint.h>
#define MOKO_QUEST_COUNT 48
typedef enum { QUEST_LOCKED=0, QUEST_ACTIVE=1, QUEST_CLEAR=2 } MokoQuestState;
typedef enum { QUEST_MAIN=0, QUEST_SIDE=1, QUEST_SECRET=2 } MokoQuestKind;
typedef struct { uint8_t state[MOKO_QUEST_COUNT]; uint8_t progress[MOKO_QUEST_COUNT]; uint8_t target[MOKO_QUEST_COUNT]; uint32_t ap; uint8_t cleared; uint8_t secrets; } MokoQuests;
void quests_reset(MokoQuests *q);
void quests_tick(MokoQuests *q,int room,int shards,int echoes,int combo,int health,int focus);
int quests_trigger(MokoQuests *q,int id); int quests_add(MokoQuests *q,int id,int amount); int quests_clear(MokoQuests *q,int id); int quests_is_clear(const MokoQuests *q,int id); int quests_completion(const MokoQuests *q); int quests_all_clear(const MokoQuests *q);
const char *quests_name(int id); const char *quests_hint(int id); int quests_reward(int id); int quests_kind(int id);
#endif
