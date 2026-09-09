#ifndef MOKO_SAVE_H
#define MOKO_SAVE_H

#include <stdint.h>

#define MOKO_SAVE_MAGIC 0x4d4f4b4fU
#define MOKO_SAVE_VERSION 2

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t checksum;
    uint32_t clears;
    uint32_t best_score;
    uint16_t best_combo;
    uint16_t best_echoes;
    uint16_t best_deaths;
    uint8_t has_checkpoint;
    uint8_t checkpoint_room;
    uint8_t checkpoint_shards;
    uint8_t puzzle_mask;
    uint8_t shard_mask;
    uint8_t echo_mask;
    uint8_t switch_mask;
    uint8_t reserved;
    uint32_t checkpoint_score;
    uint32_t checkpoint_time;
} MokoSave;

void moko_save_defaults(MokoSave *save);
int moko_save_validate(const MokoSave *save);
void moko_save_record_clear(MokoSave *save,int score,int combo,int echoes,int deaths);
void moko_save_set_checkpoint(MokoSave *save,int room,int shards,int score,int timer,uint8_t puzzle_mask,uint8_t shard_mask,uint8_t echo_mask,uint8_t switch_mask);
void moko_save_clear_checkpoint(MokoSave *save);
uint16_t moko_save_checksum(const MokoSave *save);

#endif
