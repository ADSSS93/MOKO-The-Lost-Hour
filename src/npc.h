#ifndef MOKO_NPC_H
#define MOKO_NPC_H
#include <stdint.h>
typedef enum { NPC_PORTER,NPC_GIRL,NPC_WIDOW,NPC_MECHANIC,NPC_CLOCKKEEPER,NPC_CAT } MokoNpcKind;
typedef struct { uint8_t room,kind; short x,y; uint8_t quest; const char *name; const char *line_before; const char *line_after; } MokoNpcDef;
#define MOKO_NPC_COUNT 10
const MokoNpcDef *npc_get(int index);
int npc_near(int room,int px,int py,int radius);
int npc_count_room(int room);
#endif
