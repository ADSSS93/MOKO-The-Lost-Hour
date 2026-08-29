#include "world_events.h"
static const MokoWorldEventDef events[MOKO_WORLD_EVENT_COUNT]={
 {0,64,178,24,WORLD_EVENT_PICKUP,"00:00 TICKET"},{0,278,94,25,WORLD_EVENT_SECRET,"PLATFORM 13"},{0,148,116,26,WORLD_EVENT_INSPECT,"PHANTOM TRAIN"},{0,238,184,27,WORLD_EVENT_SECRET,"CLOCKWORK CAT"},{0,94,86,2,WORLD_EVENT_INSPECT,"GLASS ECHO"},{0,205,151,1,WORLD_EVENT_INSPECT,"DEAD SIGNAL"},
 {1,52,96,28,WORLD_EVENT_INSPECT,"REVERSE RAIN"},{1,266,181,29,WORLD_EVENT_PICKUP,"SOAKED LETTER"},{1,188,92,30,WORLD_EVENT_PICKUP,"BLUE KEY"},{1,292,116,31,WORLD_EVENT_SECRET,"WALKING LAMP"},{1,116,182,6,WORLD_EVENT_PICKUP,"LOST UMBRELLA"},{1,224,138,7,WORLD_EVENT_INSPECT,"STREET ECHO"},
 {2,70,91,32,WORLD_EVENT_PICKUP,"PORTRAIT PIECE"},{2,126,174,33,WORLD_EVENT_PICKUP,"COLD TEACUP"},{2,214,190,34,WORLD_EVENT_SECRET,"UNDER THE BED"},{2,274,82,35,WORLD_EVENT_INSPECT,"MORNING BIRD"},{2,166,111,10,WORLD_EVENT_INSPECT,"EMPTY BREAKFAST"},{2,244,146,11,WORLD_EVENT_INSPECT,"HOUSE ECHO"},
 {3,54,176,36,WORLD_EVENT_PICKUP,"TINY GEAR"},{3,104,96,36,WORLD_EVENT_PICKUP,"TINY GEAR"},{3,162,180,38,WORLD_EVENT_PICKUP,"LUNCHBOX"},{3,218,92,39,WORLD_EVENT_SECRET,"HIDDEN BELL"},{3,268,172,14,WORLD_EVENT_PICKUP,"LOOSE COG"},{3,292,112,15,WORLD_EVENT_INSPECT,"CLOCKWORK ECHO"}
};
static int near(int ax,int ay,int bx,int by,int r){int dx=ax-bx,dy=ay-by;return dx*dx+dy*dy<=r*r;}
void world_events_reset(MokoWorldEvents*w){int i;w->interactions=0;for(i=0;i<MOKO_WORLD_EVENT_COUNT;i++)w->collected[i]=0;for(i=0;i<5;i++)w->room_visits[i]=0;}
void world_events_enter_room(MokoWorldEvents*w,int room,MokoQuests*q){if(room<0||room>4)return;if(w->room_visits[room]<255)w->room_visits[room]++;if(room==0){quests_trigger(q,24);quests_trigger(q,25);quests_trigger(q,26);quests_trigger(q,27);}else if(room==1){quests_trigger(q,28);quests_trigger(q,29);quests_trigger(q,30);quests_trigger(q,31);}else if(room==2){quests_trigger(q,32);quests_trigger(q,33);quests_trigger(q,34);quests_trigger(q,35);}else if(room==3){quests_trigger(q,36);quests_trigger(q,37);quests_trigger(q,38);quests_trigger(q,39);}}
int world_events_interact(MokoWorldEvents*w,MokoQuests*q,int room,int x,int y,int radius){int i,reward=0;for(i=0;i<MOKO_WORLD_EVENT_COUNT;i++){const MokoWorldEventDef*d=&events[i];if(w->collected[i]||d->room!=room||!near(x,y,d->x,d->y,radius))continue;w->collected[i]=1;w->interactions++;quests_trigger(q,d->quest);reward=quests_add(q,d->quest,1);
/* Physical event chains: one discovery can advance a larger multi-step memory. */
if(d->quest==26){quests_add(q,26,2);} /* the train is heard as it crosses both temporal rails */
if(d->quest==28){quests_add(q,28,2);} /* reverse-rain cluster contains three streams */
if(d->quest==30){quests_add(q,30,1);} /* blue key immediately opens the nearby red lock */
if(d->quest==32){quests_add(q,32,3);} /* portrait pickup restores the remaining fragments */
if(d->quest==33){quests_add(q,33,1);} /* teacup is returned to the frozen table */
if(d->quest==36){quests_add(q,36,2);} /* each visible gear represents part of the escaped set */
return reward?reward:1;}return 0;}
int world_events_near(const MokoWorldEvents*w,int room,int x,int y,int radius){int i;for(i=0;i<MOKO_WORLD_EVENT_COUNT;i++)if(!w->collected[i]&&events[i].room==room&&near(x,y,events[i].x,events[i].y,radius))return i;return -1;}
int world_events_remaining(const MokoWorldEvents*w,int room){int i,n=0;for(i=0;i<MOKO_WORLD_EVENT_COUNT;i++)if(!w->collected[i]&&events[i].room==room)n++;return n;}
const MokoWorldEventDef *world_event_def(int index){return(index>=0&&index<MOKO_WORLD_EVENT_COUNT)?&events[index]:0;}
