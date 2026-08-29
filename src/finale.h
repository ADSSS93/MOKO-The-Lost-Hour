#ifndef MOKO_FINALE_H
#define MOKO_FINALE_H

#include <stdint.h>

typedef enum {
    FINALE_DORMANT=0,
    FINALE_RESTORE,
    FINALE_STABILIZE,
    FINALE_COMPLETE
} MokoFinalePhase;

typedef struct {
    uint8_t socket[4];
    uint8_t charge;
    uint8_t phase;
    int phase_timer;
    int sweep_tick;
    int stability;
    int perfect_chain;
} MokoFinale;

void finale_reset(MokoFinale *f);
void finale_begin(MokoFinale *f,int shards);
int finale_activate_socket(MokoFinale *f,int index,int shards);
void finale_tick(MokoFinale *f,int dashing);
int finale_sweep_x(const MokoFinale *f);
int finale_sweep_y(const MokoFinale *f);
int finale_hazard_active(const MokoFinale *f);
int finale_complete(const MokoFinale *f);
int finale_score_bonus(const MokoFinale *f);

#endif
