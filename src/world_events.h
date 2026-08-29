#ifndef MOKO_WORLD_EVENTS_H
#define MOKO_WORLD_EVENTS_H
#include <stdint.h>
#include "quests.h"
#define MOKO_WORLD_EVENT_COUNT 64
typedef enum { WORLD_EVENT_PICKUP=0, WORLD_EVENT_INSPECT=1, WORLD_EVENT_SECRET=2 } MokoWorldEventKind;
typedef struct { uint8_t collected[MOKO_WORLD_EVENT_COUNT]; uint8_t room_visits[5]; uint16_t interactions; } MokoWorldEvents;
typedef struct { int room; int x; int y; int quest; int kind; int requires; const char *label; } MokoWorldEventDef;
void world_events_reset(MokoWorldEvents *w);
void world_events_enter_room(MokoWorldEvents *w,int room,MokoQuests *q);
int world_events_interact(MokoWorldEvents *w,MokoQuests *q,int room,int x,int y,int radius);
int world_events_near(const MokoWorldEvents *w,int room,int x,int y,int radius);
int world_events_remaining(const MokoWorldEvents *w,int room);
const MokoWorldEventDef *world_event_def(int index);
int world_event_unlocked(const MokoWorldEvents *w,const MokoQuests *q,int index);
#endif
