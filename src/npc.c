#include "npc.h"
static const MokoNpcDef npcs[MOKO_NPC_COUNT]={
{0,NPC_PORTER,52,176,1,"PORTER","The station stopped breathing at midnight.","You brought the signal back. I heard a train."},
{0,NPC_CAT,278,184,27,"TICK","...mrrr?","The clockwork cat watches the empty rails."},
{1,NPC_GIRL,118,188,29,"ELI","My letter keeps coming back before I send it.","So it really was mine... thank you."},
{1,NPC_PORTER,252,174,6,"UMBRELLA MAN","Rain climbs here. Umbrellas are useless.","You found the one thing the rain could not take."},
{2,NPC_WIDOW,54,184,32,"MARA","Every morning I forget one face in the portrait.","All four faces. We were a family."},
{2,NPC_GIRL,218,184,35,"BIRD GIRL","The little bird refuses to sing before dawn.","Listen... it remembers morning."},
{3,NPC_MECHANIC,58,184,38,"ORIN","Machines remember hunger better than people.","My lunchbox! Maybe this hour is not hopeless."},
{3,NPC_MECHANIC,272,184,36,"GEAR KID","Seven gears ran away when the minute cracked.","I can hear them clicking back into place."},
{4,NPC_CLOCKKEEPER,72,184,44,"CLOCKKEEPER","Do not trust the clock. Listen between its ticks.","Three whispers. Now you know what the clock hides."},
{4,NPC_CLOCKKEEPER,254,184,21,"THE LAST KEEPER","Four memories open it. One choice closes it.","Hold the hour together, Moko."}
};
const MokoNpcDef*npc_get(int index){return(index>=0&&index<MOKO_NPC_COUNT)?&npcs[index]:0;}
static int abs_i(int v){return v<0?-v:v;}
int npc_near(int room,int px,int py,int radius){int i;for(i=0;i<MOKO_NPC_COUNT;i++)if(npcs[i].room==room&&abs_i(px-npcs[i].x)<=radius&&abs_i(py-npcs[i].y)<=radius)return i;return -1;}
int npc_count_room(int room){int i,n=0;for(i=0;i<MOKO_NPC_COUNT;i++)if(npcs[i].room==room)n++;return n;}
