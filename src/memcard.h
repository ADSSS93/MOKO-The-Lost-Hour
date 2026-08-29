#ifndef MOKO_MEMCARD_H
#define MOKO_MEMCARD_H

#include "save.h"

/* BIOS memory-card backend. Slot 0 maps to bu00:. */
void moko_memcard_init(void);
int moko_memcard_load(MokoSave *save);
int moko_memcard_store(const MokoSave *save);
int moko_memcard_available(void);

#endif
