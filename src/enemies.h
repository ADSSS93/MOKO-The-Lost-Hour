#ifndef MOKO_ENEMIES_H
#define MOKO_ENEMIES_H
#include <stdint.h>
typedef enum { ENEMY_TICKHOUND,ENEMY_RAINLING,ENEMY_SHADOW,ENEMY_GEARLING,ENEMY_WATCHER } MokoEnemyKind;
typedef struct { short x,y,home_x; signed char vx; uint8_t room,kind,hp,active,phase,hit_cooldown; } MokoEnemy;
#define MOKO_ENEMY_COUNT 12
typedef struct { MokoEnemy e[MOKO_ENEMY_COUNT]; } MokoEnemies;
void enemies_reset(MokoEnemies *s);
void enemies_tick(MokoEnemies *s,int room,int px,int py);
int enemies_touch(const MokoEnemies *s,int room,int px,int py,int radius);
int enemies_dash_hit(MokoEnemies *s,int room,int px,int py,int facing);
const MokoEnemy *enemies_get(const MokoEnemies *s,int index);
#endif
