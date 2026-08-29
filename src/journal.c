#include "journal.h"
static int quest_visible(const MokoQuests*q,int id){return id>=0&&id<MOKO_QUEST_COUNT&&q->state[id]!=QUEST_LOCKED;}
static int item_visible(const MokoInventory*i,int id){return id>=0&&id<ITEM_COUNT&&i->count[id]>0;}
void journal_reset(MokoJournal*j){j->quest_cursor=0;j->item_cursor=0;j->tab=0;}
void journal_toggle_tab(MokoJournal*j){j->tab=j->tab?0:1;}
void journal_next_quest(MokoJournal*j,const MokoQuests*q,int dir){int n,id=j->quest_cursor;if(dir==0)dir=1;for(n=0;n<MOKO_QUEST_COUNT;n++){id=(id+(dir>0?1:MOKO_QUEST_COUNT-1))%MOKO_QUEST_COUNT;if(quest_visible(q,id)){j->quest_cursor=id;return;}}}
void journal_next_item(MokoJournal*j,const MokoInventory*i,int dir){int n,id=j->item_cursor;if(dir==0)dir=1;for(n=0;n<ITEM_COUNT;n++){id=(id+(dir>0?1:ITEM_COUNT-1))%ITEM_COUNT;if(item_visible(i,id)){j->item_cursor=id;return;}}}
int journal_quest(const MokoJournal*j){return j->quest_cursor;}
int journal_item(const MokoJournal*j){return j->item_cursor;}
const char*journal_quest_name(const MokoJournal*j){return quests_name(j->quest_cursor);}
const char*journal_quest_hint(const MokoJournal*j){return quests_hint(j->quest_cursor);}
int journal_quest_progress(const MokoJournal*j,const MokoQuests*q){int id=j->quest_cursor;return(id>=0&&id<MOKO_QUEST_COUNT)?q->progress[id]:0;}
int journal_quest_target(const MokoJournal*j,const MokoQuests*q){int id=j->quest_cursor;return(id>=0&&id<MOKO_QUEST_COUNT)?q->target[id]:0;}
const char*journal_item_name(const MokoJournal*j){return items_name(j->item_cursor);}
int journal_item_count(const MokoJournal*j,const MokoInventory*i){int id=j->item_cursor;return(id>=0&&id<ITEM_COUNT)?i->count[id]:0;}
