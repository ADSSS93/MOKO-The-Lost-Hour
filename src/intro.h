#ifndef MOKO_INTRO_H
#define MOKO_INTRO_H
#include <stdint.h>
typedef enum { INTRO_STUDIO=0, INTRO_CLOCK=1, INTRO_FRACTURE=2, INTRO_MOKO=3, INTRO_DONE=4 } MokoIntroScene;
typedef struct { uint16_t frame; uint8_t scene; uint8_t finished; } MokoIntro;
void intro_reset(MokoIntro *i);
void intro_tick(MokoIntro *i,int skip);
int intro_done(const MokoIntro *i);
int intro_scene(const MokoIntro *i);
int intro_scene_frame(const MokoIntro *i);
const char *intro_title(const MokoIntro *i);
const char *intro_subtitle(const MokoIntro *i);
#endif
