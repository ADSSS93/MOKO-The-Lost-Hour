#ifndef MOKO_ENEMIES_H
#define MOKO_ENEMIES_H
#include <stdint.h>
typedef enum { ENEMY_TICKHOUND,ENEMY_RAINLING,ENEMY_SHADOW,ENEMY_GEARLING,ENEMY_WATCHER,ENEMY_HOUR_WARDEN } MokoEnemyKind;
typedef struct { short x,y,home_x,home_y; signed char vx,vy; uint8_t room,kind,hp,active,phase,hit_cooldown; } MokoEnemy;
#define MOKO_ENEMY_COUNT 13
typedef struct { MokoEnemy e[MOKO_ENEMY_COUNT]; uint16_t defeats; uint8_t room_defeats[5]; } MokoEnemies;
void enemies_reset(MokoEnemies *s);
void enemies_tick(MokoEnemies *s,int room,int px,int py);
int enemies_touch(const MokoEnemies *s,int room,int px,int py,int radius);
int enemies_dash_hit(MokoEnemies *s,int room,int px,int py,int facing);
int enemies_room_remaining(const MokoEnemies *s,int room);
int enemies_room_cleared(const MokoEnemies *s,int room);
int enemies_defeats(const MokoEnemies *s);
int enemies_is_boss(int kind);
int enemies_max_hp(int kind);
const MokoEnemy *enemies_get(const MokoEnemies *s,int index);
#endif
