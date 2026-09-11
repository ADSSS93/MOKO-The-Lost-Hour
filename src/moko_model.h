#ifndef MOKO_MODEL_H
#define MOKO_MODEL_H
#include <stdint.h>
/* Clean build generates this directly from assets/models/moko_lowpoly.obj. */
#include <moko_generated.h>
/* Legacy declaration retained for old source files, but clean_vertical_slice.c
   renders the generated mesh directly. */
void moko_model_draw(uint32_t *ot,char **packet,int x,int top_y,int z,int facing,int tick,int jump);
#endif
