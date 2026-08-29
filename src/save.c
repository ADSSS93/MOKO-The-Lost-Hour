#include <stddef.h>
#include "save.h"

uint16_t moko_save_checksum(const MokoSave *save){
    const uint8_t *p=(const uint8_t *)save;
    uint32_t sum=0;
    size_t i;
    for(i=0;i<sizeof(MokoSave);i++){
        if(i==offsetof(MokoSave,checksum)||i==offsetof(MokoSave,checksum)+1)continue;
        sum=(sum*33u)^p[i];
    }
    return (uint16_t)((sum^(sum>>16))&0xffffu);
}

void moko_save_defaults(MokoSave *save){
    save->magic=MOKO_SAVE_MAGIC;
    save->version=MOKO_SAVE_VERSION;
    save->checksum=0;
    save->clears=0;
    save->best_score=0;
    save->best_combo=0;
    save->best_echoes=0;
    save->best_deaths=0xffffu;
    save->reserved=0;
    save->checksum=moko_save_checksum(save);
}

int moko_save_validate(const MokoSave *save){
    if(save->magic!=MOKO_SAVE_MAGIC||save->version!=MOKO_SAVE_VERSION)return 0;
    return save->checksum==moko_save_checksum(save);
}

void moko_save_record_clear(MokoSave *save,int score,int combo,int echoes,int deaths){
    if(!moko_save_validate(save))moko_save_defaults(save);
    save->clears++;
    if(score>(int)save->best_score)save->best_score=(uint32_t)score;
    if(combo>(int)save->best_combo)save->best_combo=(uint16_t)combo;
    if(echoes>(int)save->best_echoes)save->best_echoes=(uint16_t)echoes;
    if(deaths<(int)save->best_deaths)save->best_deaths=(uint16_t)deaths;
    save->checksum=0;
    save->checksum=moko_save_checksum(save);
}
