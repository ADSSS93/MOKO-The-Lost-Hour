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
    save->has_checkpoint=0;
    save->checkpoint_room=0;
    save->checkpoint_shards=0;
    save->puzzle_mask=0;
    save->shard_mask=0;
    save->echo_mask=0;
    save->switch_mask=0;
    save->reserved=0;
    save->checkpoint_score=0;
    save->checkpoint_time=0;
    save->checksum=moko_save_checksum(save);
}

int moko_save_validate(const MokoSave *save){
    if(save->magic!=MOKO_SAVE_MAGIC||save->version!=MOKO_SAVE_VERSION)return 0;
    return save->checksum==moko_save_checksum(save);
}

static void refresh(MokoSave *save){save->checksum=0;save->checksum=moko_save_checksum(save);}

void moko_save_record_clear(MokoSave *save,int score,int combo,int echoes,int deaths){
    if(!moko_save_validate(save))moko_save_defaults(save);
    save->clears++;
    if(score>(int)save->best_score)save->best_score=(uint32_t)score;
    if(combo>(int)save->best_combo)save->best_combo=(uint16_t)combo;
    if(echoes>(int)save->best_echoes)save->best_echoes=(uint16_t)echoes;
    if(deaths<(int)save->best_deaths)save->best_deaths=(uint16_t)deaths;
    refresh(save);
}

void moko_save_set_checkpoint(MokoSave *save,int room,int shards,int score,int timer,uint8_t puzzle_mask,uint8_t shard_mask,uint8_t echo_mask,uint8_t switch_mask){
    if(!moko_save_validate(save))moko_save_defaults(save);
    save->has_checkpoint=1;
    save->checkpoint_room=(uint8_t)room;
    save->checkpoint_shards=(uint8_t)shards;
    save->checkpoint_score=(uint32_t)(score<0?0:score);
    save->checkpoint_time=(uint32_t)(timer<0?0:timer);
    save->puzzle_mask=puzzle_mask;
    save->shard_mask=shard_mask;
    save->echo_mask=echo_mask;
    save->switch_mask=switch_mask;
    refresh(save);
}

void moko_save_clear_checkpoint(MokoSave *save){
    if(!moko_save_validate(save))moko_save_defaults(save);
    save->has_checkpoint=0;
    save->checkpoint_room=0;
    save->checkpoint_shards=0;
    save->checkpoint_score=0;
    save->checkpoint_time=0;
    save->puzzle_mask=0;
    save->shard_mask=0;
    save->echo_mask=0;
    save->switch_mask=0;
    refresh(save);
}
