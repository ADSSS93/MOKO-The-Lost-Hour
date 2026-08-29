#include "intro.h"
static const uint16_t lengths[]={105,150,165,180};
void intro_reset(MokoIntro*i){i->frame=0;i->scene=INTRO_STUDIO;i->finished=0;}
void intro_tick(MokoIntro*i,int skip){if(!i||i->finished)return;if(skip){i->scene=INTRO_DONE;i->finished=1;return;}i->frame++;if(i->scene<INTRO_MOKO&&i->frame>=lengths[i->scene]){i->scene++;i->frame=0;}else if(i->scene==INTRO_MOKO&&i->frame>=lengths[INTRO_MOKO]){i->scene=INTRO_DONE;i->finished=1;}}
int intro_done(const MokoIntro*i){return !i||i->finished;}
int intro_scene(const MokoIntro*i){return i?i->scene:INTRO_DONE;}
int intro_scene_frame(const MokoIntro*i){return i?i->frame:0;}
const char*intro_title(const MokoIntro*i){if(!i)return "";switch(i->scene){case INTRO_STUDIO:return "ADSSS93 PRESENTS";case INTRO_CLOCK:return "AT 00:00, ONE HOUR VANISHED.";case INTRO_FRACTURE:return "TIME BROKE. MEMORIES FELL BETWEEN SECONDS.";case INTRO_MOKO:return "M O K O";default:return "";}}
const char*intro_subtitle(const MokoIntro*i){if(!i)return "";switch(i->scene){case INTRO_STUDIO:return "A PLAYSTATION STORY";case INTRO_CLOCK:return "NO ONE REMEMBERS WHERE IT WENT.";case INTRO_FRACTURE:return "ONE MEMORY STILL REFUSED TO DISAPPEAR.";case INTRO_MOKO:return "THE LOST HOUR";default:return "";}}
