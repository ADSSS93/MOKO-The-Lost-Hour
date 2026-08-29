#ifndef MOKO_SPRITE_H
#define MOKO_SPRITE_H

#include <stdint.h>

void moko_sprite_init(void);
void moko_sprite_draw(int x, int y, int facing, int walk_tick, int invuln, int anim_tick, uint32_t *ot, char **next_packet);

#endif
