#include <psxapi.h>
#include "memcard.h"

#define MOKO_CARD_FILE "bu00:MOKOLOSTHOUR"
#define MOKO_CARD_CREATE_MODE 0x0202
#define MOKO_CARD_READ_MODE 0x0001

static int card_ready=0;

void moko_memcard_init(void){
    EnterCriticalSection();
    InitCARD(1);
    StartCARD();
    _bu_init();
    ExitCriticalSection();
    card_ready=1;
}

int moko_memcard_available(void){return card_ready;}

int moko_memcard_load(MokoSave *save){
    int fd,n;
    if(!card_ready)return 0;
    fd=open(MOKO_CARD_FILE,MOKO_CARD_READ_MODE);
    if(fd<0)return 0;
    n=read(fd,save,sizeof(*save));
    close(fd);
    if(n!=(int)sizeof(*save)||!moko_save_validate(save)){
        moko_save_defaults(save);
        return 0;
    }
    return 1;
}

int moko_memcard_store(const MokoSave *save){
    int fd,n;
    if(!card_ready||!moko_save_validate(save))return 0;
    fd=open(MOKO_CARD_FILE,MOKO_CARD_CREATE_MODE);
    if(fd<0)return 0;
    n=write(fd,save,sizeof(*save));
    close(fd);
    return n==(int)sizeof(*save);
}
