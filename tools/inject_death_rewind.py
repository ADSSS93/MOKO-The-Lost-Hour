import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Track a short presentation timer so the failure state has readable PS1 feedback.
needle = 'static int warden_attack_tick=0,warden_attack_flash=0,warden_phase_notice=0;'
replacement = needle + 'static int death_rewind_tick=0;'
if needle not in src: raise SystemExit('death rewind globals anchor missing')
src = src.replace(needle, replacement, 1)

# Every fresh run resets the game-over presentation state.
needle = 'warden_attack_tick=0;warden_attack_flash=0;warden_phase_notice=0;'
replacement = needle + 'death_rewind_tick=0;'
if needle not in src: raise SystemExit('death rewind reset anchor missing')
src = src.replace(needle, replacement, 1)

anchor = 'static int warden_phase_level(void)'
helpers = r'''static void death_rewind_art(void){
    int i,p=(death_rewind_tick/5)&3;
    /* Broken purple clock: visually echoes Moko's clock motif instead of a flat red screen. */
    rect(0,0,320,240,15,5,25);
    rect(104-p,57-p,112+p*2,112+p*2,31,14,49);
    rect(112,65,96,96,72,35,104);
    rect(120,73,80,80,18,11,28);
    /* Cat-ear silhouette around the clock face. */
    rect(114,51,18,17,92,44,130);rect(188,51,18,17,92,44,130);
    /* Split hands and flying time fragments. */
    rect(158,89,4,33,226,174,71);rect(160,119,28,4,226,174,71);
    rect(157,119,6,6,244,219,130);
    for(i=0;i<6;i++){
        int x=160+(((death_rewind_tick*(i+1)+i*43)%150)-75);
        int y=118+(((death_rewind_tick*(2+i)+i*31)%104)-52);
        rect(x,y,3+(i&1),3+(i&1),104,57,148);
    }
}
static void death_rewind_retry(void){
    death_rewind_tick=0;
    /* Prefer the persisted v3 checkpoint so quest/event/world state is restored too. */
    if(profile_loaded&&profile.has_checkpoint){continue_game();return;}
    room=checkpoint_room;px=20;py=190;health=3;score=checkpoint_score;
    timer_frames=checkpoint_time>1800?checkpoint_time:1800;invuln=90;
    gameplay_break_combo(&gameplay);gameplay.focus=100;
    world_runtime_reset(&living,room);living.enemies.e[12].active=0;living.enemies.e[12].hp=0;
    moko_audio_set_room(room);area_banner=120;state=STATE_PLAY;sfx(0x2600);
}
'''
if anchor not in src: raise SystemExit('death rewind helper anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

# Replace the old flat game-over branch with a visible rewind/checkpoint loop.
old = '''else if(state==STATE_GAMEOVER){rect(0,0,320,240,24,5,10);FntPrint(font_id,"\\n THE HOUR IS LOST\\n SCORE %d BEST x%d\\n\\nCROSS - CHECKPOINT\\nSTART - NEW GAME",score,gameplay.best_combo);FntFlush(font_id);if(pressed(n,PAD_CROSS)){room=checkpoint_room;px=20;py=190;health=3;score=checkpoint_score;timer_frames=checkpoint_time>1800?checkpoint_time:1800;invuln=90;state=STATE_PLAY;}if(pressed(n,PAD_START))reset_game();}'''
new = '''else if(state==STATE_GAMEOVER){death_rewind_tick++;death_rewind_art();FntPrint(font_id,"\\n THE HOUR SHATTERED\\n %s\\n SCORE %d  BEST x%d\\n\\nCROSS - REWIND TO CHECKPOINT\\nSTART - NEW TIMELINE\\n\\nREWIND REV 261",timer_frames<=0?"TIME EXPIRED":"MOKO FELL OUT OF TIME",score,gameplay.best_combo);if(profile_loaded&&profile.has_checkpoint)FntPrint(font_id,"\\nMEMORY CARD CHECKPOINT - SHARDS %d/4",profile.checkpoint_shards);else FntPrint(font_id,"\\nLOCAL CHECKPOINT - ROOM %d",checkpoint_room+1);FntFlush(font_id);if(pressed(n,PAD_CROSS))death_rewind_retry();if(pressed(n,PAD_START))reset_game();}'''
if old not in src: raise SystemExit('game over branch anchor missing')
src = src.replace(old, new, 1)

# Make the runtime build marker unambiguous in the normal HUD too.
src = src.replace('WARDEN REV 260','REWIND REV 261',1)
src = src.replace('W260 %02d:%02d','R261 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
