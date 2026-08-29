#ifndef MOKO_WORLD3D_H
#define MOKO_WORLD3D_H
#include <stdint.h>
#include <psxgpu.h>
void world3d_init(void);
void world3d_draw_station(int player_x,int player_y,int facing,int tick,uint32_t *ot,char **packet);
#endif
