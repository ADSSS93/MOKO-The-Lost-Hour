#ifndef MOKO_LEVEL_DATA_H
#define MOKO_LEVEL_DATA_H

typedef enum { MOKO_PROP_SOLID=1, MOKO_PROP_DECOR=2, MOKO_PROP_LIGHT=4 } MokoPropFlags;
typedef struct { short x,y,w,h; unsigned char r,g,b,flags; } MokoLevelProp;
typedef struct { const char *name; unsigned char bg_r,bg_g,bg_b; const MokoLevelProp *props; int prop_count; } MokoLevelDef;

#define MOKO_LEVEL_COUNT 5
const MokoLevelDef *moko_level_get(int room);
int moko_level_collides(int room,int x,int y,int w,int h);

#endif
