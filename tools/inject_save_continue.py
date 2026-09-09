import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

src = src.replace('#include "world_runtime.h"', '#include "world_runtime.h"\n#include "save.h"\n#include "memcard.h"', 1)

needle = 'static uint8_t shard_taken[4]={0},puzzle_done[4]={0},echo_seen[4]={0};static int switch_a=0,switch_b=0,dialogue_id=0,dialogue_npc=-1,dialogue_started=0,invuln=0;static MokoGameplay gameplay;static MokoFinale finale;static MokoAdventure adventure;static MokoWorldRuntime living;'
replacement = needle + 'static MokoSave profile;static int profile_loaded=0,save_notice=0;'
if needle not in src: raise SystemExit('save globals anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'world_runtime_reset(&living,0);}'
replacement = 'world_runtime_reset(&living,0);moko_memcard_init();moko_save_defaults(&profile);profile_loaded=moko_memcard_load(&profile);}'
if needle not in src: raise SystemExit('init anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'anim_tick++;if(area_banner>0)area_banner--;}'
replacement = 'anim_tick++;if(area_banner>0)area_banner--;if(save_notice>0)save_notice--;}'
src = src.replace(needle, replacement, 1)

anchor = 'static void reset_game(void)'
helpers = r'''static void reset_game(void);
static uint8_t mask4(const uint8_t*v){int i;uint8_t m=0;for(i=0;i<4;i++)if(v[i])m|=(uint8_t)(1u<<i);return m;}
static void persist_checkpoint(void){uint8_t sm=(switch_a?1:0)|(switch_b?2:0);moko_save_set_checkpoint(&profile,checkpoint_room,shards,checkpoint_score,checkpoint_time,mask4(puzzle_done),mask4(shard_taken),mask4(echo_seen),sm);if(moko_memcard_store(&profile)){profile_loaded=1;save_notice=150;}else save_notice=90;}
static void continue_game(void){int i;reset_game();for(i=0;i<4;i++){puzzle_done[i]=(profile.puzzle_mask>>i)&1;shard_taken[i]=(profile.shard_mask>>i)&1;echo_seen[i]=(profile.echo_mask>>i)&1;}switch_a=profile.switch_mask&1;switch_b=(profile.switch_mask>>1)&1;shards=profile.checkpoint_shards;checkpoint_room=profile.checkpoint_room;checkpoint_score=(int)profile.checkpoint_score;checkpoint_time=(int)profile.checkpoint_time;room=checkpoint_room;score=checkpoint_score;timer_frames=checkpoint_time>1800?checkpoint_time:1800;px=20;py=190;health=3;invuln=90;area_banner=120;gameplay_reset(&gameplay);for(i=0;i<shards;i++)gameplay_record_shard(&gameplay);for(i=0;i<4;i++)if(echo_seen[i])gameplay_record_echo(&gameplay);adventure_reset(&adventure);for(i=0;i<4;i++){if(shard_taken[i])adventure_story_progress(&adventure,16,1);if(echo_seen[i])adventure_story_progress(&adventure,17,1);}if(puzzle_done[0])adventure_story_clear(&adventure,1);if(switch_a)adventure_story_progress(&adventure,4,1);if(switch_b)adventure_story_progress(&adventure,4,1);if(puzzle_done[2])adventure_story_clear(&adventure,8);if(puzzle_done[3])adventure_story_clear(&adventure,12);world_runtime_reset(&living,room);living.enemies.e[12].active=0;living.enemies.e[12].hp=0;moko_audio_set_room(room);state=STATE_PLAY;sfx(0x2600);save_notice=120;}
'''
if anchor not in src: raise SystemExit('reset anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

needle = 'checkpoint_time=timer_frames;sfx(0x2400);say(8);'
replacement = 'checkpoint_time=timer_frames;persist_checkpoint();sfx(0x2400);say(8);'
if needle not in src: raise SystemExit('checkpoint anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'if(finale_complete(&finale)){adventure_story_clear(&adventure,21);score+=finale_score_bonus(&finale)+timer_frames/60;sfx(0x2f00);state=STATE_ENDING;}'
replacement = 'if(finale_complete(&finale)){adventure_story_clear(&adventure,21);score+=finale_score_bonus(&finale)+timer_frames/60;moko_save_record_clear(&profile,score,gameplay.best_combo,gameplay.echoes,gameplay.deaths);moko_save_clear_checkpoint(&profile);moko_memcard_store(&profile);profile_loaded=1;sfx(0x2f00);state=STATE_ENDING;}'
if needle not in src: raise SystemExit('ending save anchor missing')
src = src.replace(needle, replacement, 1)

src = src.replace('ENEMY REV 249', 'SAVE REV 252', 1)
src = src.replace('E249 %02d:%02d', 'S252 %02d:%02d', 1)

needle = 'FntFlush(font_id);if(pressed(n,PAD_START)||pressed(n,PAD_CROSS))reset_game();'
replacement = 'if(profile_loaded)FntPrint(font_id,"\\nCARD OK  BEST %lu  CLEARS %lu",(unsigned long)profile.best_score,(unsigned long)profile.clears);if(profile.has_checkpoint)FntPrint(font_id,"\\nTRIANGLE - CONTINUE  SHARDS %d/4",profile.checkpoint_shards);else FntPrint(font_id,"\\nNO SAVED CHECKPOINT");FntFlush(font_id);if(profile.has_checkpoint&&pressed(n,PAD_TRIANGLE))continue_game();else if(pressed(n,PAD_START)||pressed(n,PAD_CROSS))reset_game();'
if needle not in src: raise SystemExit('title continue anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'if(adventure.notice_timer>0)FntPrint(font_id,"\\nEVENT CLEAR: %s",adventure_notice(&adventure));'
replacement = 'if(save_notice>0)FntPrint(font_id,"\\nMEMORY CARD: %s",moko_memcard_available()?"CHECKPOINT SAVED":"SAVE FAILED");if(adventure.notice_timer>0)FntPrint(font_id,"\\nEVENT CLEAR: %s",adventure_notice(&adventure));'
if needle not in src: raise SystemExit('HUD save notice anchor missing')
src = src.replace(needle, replacement, 1)

pathlib.Path(sys.argv[2]).write_text(src)
