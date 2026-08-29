#include "items.h"
static const char*names[ITEM_COUNT]={"00:00 TICKET","SOAKED LETTER","BLUE KEY","LOST UMBRELLA","PORTRAIT PIECE","COLD TEACUP","TINY GEAR","LUNCHBOX","LOOSE COG"};
void items_reset(MokoInventory*i){int n;for(n=0;n<ITEM_COUNT;n++)i->count[n]=0;}
void items_add(MokoInventory*i,int id,int amount){int v;if(id<0||id>=ITEM_COUNT||amount<=0)return;v=i->count[id]+amount;i->count[id]=(uint8_t)(v>255?255:v);}
int items_has(const MokoInventory*i,int id,int amount){return id>=0&&id<ITEM_COUNT&&amount>0&&i->count[id]>=amount;}
int items_take(MokoInventory*i,int id,int amount){if(!items_has(i,id,amount))return 0;i->count[id]-=(uint8_t)amount;return 1;}
const char*items_name(int id){return(id>=0&&id<ITEM_COUNT)?names[id]:"UNKNOWN ITEM";}
