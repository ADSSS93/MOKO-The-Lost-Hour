#include "level_data.h"
#define P(x,y,w,h,r,g,b,f) {x,y,w,h,r,g,b,f}
static const MokoLevelProp station[]={
 P(0,58,320,164,13,18,35,MOKO_PROP_DECOR),P(0,194,320,28,28,34,52,MOKO_PROP_DECOR),P(0,218,320,4,95,84,70,MOKO_PROP_SOLID),
 P(18,72,48,34,20,35,62,MOKO_PROP_DECOR),P(86,72,48,34,20,35,62,MOKO_PROP_DECOR),P(154,72,48,34,20,35,62,MOKO_PROP_DECOR),P(222,72,48,34,20,35,62,MOKO_PROP_DECOR),
 P(92,114,136,7,65,76,100,MOKO_PROP_DECOR),P(112,180,18,28,85,100,150,MOKO_PROP_SOLID),P(151,124,18,18,205,190,130,MOKO_PROP_DECOR)
};
static const MokoLevelProp street[]={
 P(0,58,320,164,27,13,35,MOKO_PROP_DECOR),P(0,202,320,20,42,24,45,MOKO_PROP_DECOR),P(145,176,18,46,170,45,65,MOKO_PROP_SOLID),P(220,195,18,27,170,45,65,MOKO_PROP_SOLID),
 P(70,190,14,14,150,60,70,MOKO_PROP_DECOR),P(270,110,14,14,150,60,70,MOKO_PROP_DECOR),P(0,112,320,3,72,38,75,MOKO_PROP_DECOR)
};
static const MokoLevelProp house[]={
 P(0,58,320,164,11,29,29,MOKO_PROP_DECOR),P(0,205,320,17,37,49,43,MOKO_PROP_DECOR),P(16,72,288,8,30,58,52,MOKO_PROP_DECOR),P(125,95,12,127,45,150,115,MOKO_PROP_SOLID),P(260,130,12,92,45,150,115,MOKO_PROP_SOLID),P(88,178,60,5,65,88,72,MOKO_PROP_DECOR)
};
static const MokoLevelProp works[]={
 P(0,58,320,164,31,22,10,MOKO_PROP_DECOR),P(0,210,320,12,62,43,20,MOKO_PROP_SOLID),P(90,190,45,6,215,130,35,MOKO_PROP_SOLID),P(200,110,45,6,215,130,35,MOKO_PROP_SOLID),P(150,84,22,22,180,115,35,MOKO_PROP_DECOR),P(178,136,5,74,235,70,55,MOKO_PROP_SOLID),P(238,62,5,94,235,70,55,MOKO_PROP_SOLID)
};
static const MokoLevelProp chamber[]={
 P(0,58,320,164,27,7,12,MOKO_PROP_DECOR),P(0,210,320,12,52,19,25,MOKO_PROP_SOLID),P(104,70,112,92,43,19,28,MOKO_PROP_DECOR),P(116,78,88,76,72,42,49,MOKO_PROP_DECOR),P(128,82,64,64,90,55,65,MOKO_PROP_DECOR),P(144,98,32,32,205,185,120,MOKO_PROP_LIGHT)
};
static const MokoLevelDef levels[MOKO_LEVEL_COUNT]={
 {"SILENT STATION",13,18,35,station,sizeof(station)/sizeof(station[0])},
 {"BACKWARD STREET",27,13,35,street,sizeof(street)/sizeof(street[0])},
 {"HOUSE WITHOUT MORNING",11,29,29,house,sizeof(house)/sizeof(house[0])},
 {"CLOCKWORKS",31,22,10,works,sizeof(works)/sizeof(works[0])},
 {"CLOCK CHAMBER",27,7,12,chamber,sizeof(chamber)/sizeof(chamber[0])}
};
const MokoLevelDef *moko_level_get(int room){return(room>=0&&room<MOKO_LEVEL_COUNT)?&levels[room]:0;}
static int overlap(int a,int b,int c,int d,int e,int f,int g,int h){return a<e+g&&a+c>e&&b<f+h&&b+d>f;}
int moko_level_collides(int room,int x,int y,int w,int h){int i;const MokoLevelDef*l=moko_level_get(room);if(!l)return 0;for(i=0;i<l->prop_count;i++){const MokoLevelProp*p=&l->props[i];if((p->flags&MOKO_PROP_SOLID)&&overlap(x,y,w,h,p->x,p->y,p->w,p->h))return 1;}return 0;}
