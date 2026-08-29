#ifndef MOKO_JOURNAL_H
#define MOKO_JOURNAL_H
#include "quests.h"
#include "items.h"
typedef struct {int quest_cursor;int item_cursor;int tab;} MokoJournal;
void journal_reset(MokoJournal*j);
void journal_sync(MokoJournal*j,const MokoQuests*q,const MokoInventory*i);
void journal_next_quest(MokoJournal*j,const MokoQuests*q,int dir);
void journal_next_item(MokoJournal*j,const MokoInventory*i,int dir);
void journal_toggle_tab(MokoJournal*j);
int journal_quest(const MokoJournal*j);
int journal_item(const MokoJournal*j);
const char*journal_quest_name(const MokoJournal*j);
const char*journal_quest_hint(const MokoJournal*j);
const char*journal_quest_status(const MokoJournal*j,const MokoQuests*q);
int journal_quest_progress(const MokoJournal*j,const MokoQuests*q);
int journal_quest_target(const MokoJournal*j,const MokoQuests*q);
int journal_quest_cleared(const MokoQuests*q);
int journal_quest_active(const MokoQuests*q);
int journal_quest_discovered(const MokoQuests*q);
const char*journal_item_name(const MokoJournal*j);
int journal_item_count(const MokoJournal*j,const MokoInventory*i);
int journal_has_items(const MokoInventory*i);
#endif
