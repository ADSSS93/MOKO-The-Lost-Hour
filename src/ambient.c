#include "ambient.h"
static uint16_t rng=0x4d2bu;static uint16_t rnd(void){rng=(uint16_t)(rng*25173u+13849u);return rng;}
static void spawn(MokoAmbientParticle*p,int room,int i){uint16_t r=rnd();p->x=(short)(r%320);p->y=(short)(58+((r>>4)%160));p->phase=(unsigned char)(r+i*17);p->life=(unsigned char)(90+(r%150));if(room==0){p->kind=AMBIENT_DUST;p->vx=(i&1)?1:0;p->vy=-1;}else if(room==1){p->kind=AMBIENT_RAIN;p->vx=(i&1)?1:-1;p->vy=(i%3)?-2:-1;p->y=(short)(90+(r%120));}else if(room==2){p->kind=AMBIENT_MOTE;p->vx=(i%3)-1;p->vy=-1;}else if(room==3){p->kind=(i%4)?AMBIENT_SPARK:AMBIENT_GEAR;p->vx=(i&1)?1:-1;p->vy=(i%3)-1;}else{p->kind=AMBIENT_MOTE;p->vx=(i&1)?1:-1;p->vy=(i%2)?1:-1;}}
void ambient_reset(MokoAmbient*a,int room){int i;a->tick=0;a->room=(uint8_t)room;for(i=0;i<MOKO_AMBIENT_PARTICLES;i++)spawn(&a->p[i],room,i);}
void ambient_set_room(MokoAmbient*a,int room){if(room!=a->room)ambient_reset(a,room);}
void ambient_tick(MokoAmbient*a){int i;a->tick++;for(i=0;i<MOKO_AMBIENT_PARTICLES;i++){MokoAmbientParticle*p=&a->p[i];p->x+=p->vx;p->y+=p->vy;p->phase++;if(p->life)p->life--;if(!p->life||p->x<-8||p->x>328||p->y<54||p->y>224)spawn(p,a->room,i);}}
int ambient_count(const MokoAmbient*a){(void)a;return MOKO_AMBIENT_PARTICLES;}
const MokoAmbientParticle*ambient_particle(const MokoAmbient*a,int index){return(index>=0&&index<MOKO_AMBIENT_PARTICLES)?&a->p[index]:0;}
