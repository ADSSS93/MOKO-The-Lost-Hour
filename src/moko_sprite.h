#ifndef MOKO_SPRITE_H
#define MOKO_SPRITE_H

void moko_sprite_init(void);
void moko_sprite_draw(int x, int y, int facing, int walk_tick, int invuln, int anim_tick, unsigned int *ot, char **next_packet);

#endif
