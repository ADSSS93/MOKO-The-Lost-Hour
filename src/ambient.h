#ifndef MOKO_AMBIENT_H
#define MOKO_AMBIENT_H
#include <stdint.h>
typedef enum { AMBIENT_DUST,AMBIENT_RAIN,AMBIENT_MOTE,AMBIENT_SPARK,AMBIENT_GEAR } MokoAmbientKind;
typedef struct { short x,y; signed char vx,vy; unsigned char life,kind,phase; } MokoAmbientParticle;
#define MOKO_AMBIENT_PARTICLES 28
typedef struct { MokoAmbientParticle p[MOKO_AMBIENT_PARTICLES]; uint16_t tick; uint8_t room; } MokoAmbient;
void ambient_reset(MokoAmbient *a,int room);
void ambient_set_room(MokoAmbient *a,int room);
void ambient_tick(MokoAmbient *a);
int ambient_count(const MokoAmbient *a);
const MokoAmbientParticle *ambient_particle(const MokoAmbient *a,int index);
#endif
