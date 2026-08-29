#ifndef MOKO_SAVE_H
#define MOKO_SAVE_H

#include <stdint.h>

#define MOKO_SAVE_MAGIC 0x4d4f4b4fU
#define MOKO_SAVE_VERSION 1

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t checksum;
    uint32_t clears;
    uint32_t best_score;
    uint16_t best_combo;
    uint16_t best_echoes;
    uint16_t best_deaths;
    uint16_t reserved;
} MokoSave;

void moko_save_defaults(MokoSave *save);
int moko_save_validate(const MokoSave *save);
void moko_save_record_clear(MokoSave *save,int score,int combo,int echoes,int deaths);
uint16_t moko_save_checksum(const MokoSave *save);

#endif
