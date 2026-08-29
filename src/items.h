#ifndef MOKO_ITEMS_H
#define MOKO_ITEMS_H
#include <stdint.h>
typedef enum {ITEM_TICKET=0,ITEM_LETTER,ITEM_BLUE_KEY,ITEM_UMBRELLA,ITEM_PORTRAIT,ITEM_TEACUP,ITEM_TINY_GEAR,ITEM_LUNCHBOX,ITEM_LOOSE_COG,ITEM_COUNT} MokoItemId;
typedef struct {uint8_t count[ITEM_COUNT];} MokoInventory;
void items_reset(MokoInventory*i);
void items_add(MokoInventory*i,int id,int amount);
int items_has(const MokoInventory*i,int id,int amount);
int items_take(MokoInventory*i,int id,int amount);
const char*items_name(int id);
#endif
