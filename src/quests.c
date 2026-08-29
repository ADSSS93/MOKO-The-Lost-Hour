#include "quests.h"

typedef struct { const char *name; const char *hint; uint16_t reward; uint8_t target; uint8_t kind; } QuestDef;
static const QuestDef defs[MOKO_QUEST_COUNT]={
 {"Wake Between Minutes","Reach the Silent Station clock.",100,1,QUEST_MAIN},
 {"Station Signal","Restore the dead platform signal.",150,1,QUEST_MAIN},
 {"Echo in the Glass","Find the Station Memory Echo.",125,1,QUEST_SIDE},
 {"No Time to Wait","Clear Station without taking damage.",200,1,QUEST_SIDE},
 {"Two Red Switches","Activate both street switches.",175,2,QUEST_MAIN},
 {"Against the Current","Cross both backward pulses.",150,2,QUEST_SIDE},
 {"Lost Umbrella","Search the far end of Backward Street.",125,1,QUEST_SIDE},
 {"Street Echo","Find the memory hiding in the rain.",125,1,QUEST_SIDE},
 {"House Without Dawn","Open the sealed morning room.",200,1,QUEST_MAIN},
 {"Three Cold Windows","Inspect three frozen windows.",150,3,QUEST_SIDE},
 {"Breakfast Never Came","Find what was left on the table.",175,1,QUEST_SIDE},
 {"House Echo","Recover the family's Memory Echo.",125,1,QUEST_SIDE},
 {"Wake the Clockworks","Restart the central gear.",225,1,QUEST_MAIN},
 {"Dash the Red Gates","Pass two temporal gates while dashing.",200,2,QUEST_SIDE},
 {"Gear Collector","Recover three loose time cogs.",225,3,QUEST_SIDE},
 {"Clockworks Echo","Find the machinist's Memory Echo.",125,1,QUEST_SIDE},
 {"Four Missing Hours","Recover all four Memory Shards.",500,4,QUEST_MAIN},
 {"Memory Keeper","Recover every Memory Echo.",400,4,QUEST_SIDE},
 {"Chain of Eight","Reach an eight-action memory combo.",300,8,QUEST_SIDE},
 {"Perfect Focus","Reach a chamber with full Focus.",200,1,QUEST_SIDE},
 {"Restore the Sockets","Return four shards to the clock.",400,4,QUEST_MAIN},
 {"Hold the Lost Hour","Stabilize the fractured clock.",600,1,QUEST_MAIN},
 {"Nothing Forgotten","Clear every optional event.",750,1,QUEST_SECRET},
 {"The Hidden Minute","Discover the secret after 100 percent.",1000,1,QUEST_SECRET}
};

void quests_reset(MokoQuests *q){int i;q->ap=0;q->cleared=0;q->secrets=0;for(i=0;i<MOKO_QUEST_COUNT;i++){q->state[i]=QUEST_LOCKED;q->progress[i]=0;q->target[i]=defs[i].target;}q->state[0]=QUEST_ACTIVE;q->state[2]=QUEST_ACTIVE;q->state[3]=QUEST_ACTIVE;}
int quests_trigger(MokoQuests *q,int id){if(id<0||id>=MOKO_QUEST_COUNT||q->state[id]!=QUEST_LOCKED)return 0;q->state[id]=QUEST_ACTIVE;return 1;}
int quests_clear(MokoQuests *q,int id){if(id<0||id>=MOKO_QUEST_COUNT||q->state[id]==QUEST_CLEAR)return 0;q->state[id]=QUEST_CLEAR;q->progress[id]=q->target[id];q->ap+=defs[id].reward;q->cleared++;if(defs[id].kind==QUEST_SECRET)q->secrets++;return defs[id].reward;}
int quests_add(MokoQuests *q,int id,int amount){if(id<0||id>=MOKO_QUEST_COUNT||q->state[id]==QUEST_LOCKED||q->state[id]==QUEST_CLEAR)return 0;if(amount<1)amount=1;if(q->progress[id]+amount>=q->target[id])return quests_clear(q,id);q->progress[id]+=amount;return 0;}
int quests_is_clear(const MokoQuests *q,int id){return id>=0&&id<MOKO_QUEST_COUNT&&q->state[id]==QUEST_CLEAR;}
int quests_completion(const MokoQuests *q){return (q->cleared*100)/MOKO_QUEST_COUNT;}
int quests_all_clear(const MokoQuests *q){return q->cleared>=MOKO_QUEST_COUNT;}
const char *quests_name(int id){return (id>=0&&id<MOKO_QUEST_COUNT)?defs[id].name:"Unknown Event";}
const char *quests_hint(int id){return (id>=0&&id<MOKO_QUEST_COUNT)?defs[id].hint:"";}
int quests_reward(int id){return (id>=0&&id<MOKO_QUEST_COUNT)?defs[id].reward:0;}
int quests_kind(int id){return (id>=0&&id<MOKO_QUEST_COUNT)?defs[id].kind:QUEST_SIDE;}

void quests_tick(MokoQuests *q,int room,int shards,int echoes,int combo,int health,int focus){
 if(room>=1){quests_clear(q,0);quests_trigger(q,4);quests_trigger(q,6);quests_trigger(q,7);}
 if(room>=2){quests_trigger(q,8);quests_trigger(q,9);quests_trigger(q,10);quests_trigger(q,11);}
 if(room>=3){quests_trigger(q,12);quests_trigger(q,13);quests_trigger(q,14);quests_trigger(q,15);}
 if(room>=4){quests_trigger(q,19);quests_trigger(q,20);quests_trigger(q,21);if(focus>=100)quests_clear(q,19);}
 if(shards>=4)quests_clear(q,16);else {quests_trigger(q,16);q->progress[16]=(uint8_t)shards;}
 if(echoes>=4)quests_clear(q,17);else {quests_trigger(q,17);q->progress[17]=(uint8_t)echoes;}
 if(combo>=8)quests_clear(q,18);else {quests_trigger(q,18);if(combo>q->progress[18])q->progress[18]=(uint8_t)combo;}
 if(room==0&&health>=3)quests_trigger(q,3);
 if(q->cleared>=22){quests_trigger(q,22);quests_clear(q,22);quests_trigger(q,23);}
}
