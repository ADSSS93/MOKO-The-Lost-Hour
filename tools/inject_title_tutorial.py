import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

if 'PAUSE REV 267' not in src or 'COMPASS REV 265' not in src:
    raise SystemExit('title/tutorial revision anchors missing')

state_anchor = 'static void reset_game(void);'
if state_anchor not in src:
    raise SystemExit('title/tutorial state anchor missing')
src = src.replace(state_anchor, 'static int title_choice=0,title_tick=0;\nstatic uint8_t tutorial_flags=0;\n' + state_anchor, 1)

anchor = 'static int warden_phase_level(void)'
helpers = r'''static void title_clock_art(int cx,int cy){
    int p=(title_tick/10)&3,hand=(title_tick/12)&7,i;
    rect(0,0,320,240,5,7,18);
    for(i=0;i<16;i++){int x=(i*47+title_tick/3)%340-10,y=22+((i*31+title_tick/7)%180);rect(x,y,2,2,45+(i&1)*30,42,78+(i%3)*12);}
    rect(cx-44,cy-44,88,88,20,22,45);rect(cx-39,cy-39,78,78,73,43,101);rect(cx-34,cy-34,68,68,9,14,29);
    rect(cx-2,cy-2,5,5,232,197,117);
    if(hand==0)rect(cx-1,cy-27,3,27,211,155,235);
    else if(hand==1){rect(cx,cy-18,3,18,211,155,235);rect(cx+3,cy-18,15,3,211,155,235);}
    else if(hand==2)rect(cx,cy,28,3,211,155,235);
    else if(hand==3){rect(cx,cy,3,19,211,155,235);rect(cx+3,cy+16,15,3,211,155,235);}
    else if(hand==4)rect(cx-1,cy,3,28,211,155,235);
    else if(hand==5){rect(cx-18,cy+16,18,3,211,155,235);rect(cx-18,cy,3,16,211,155,235);}
    else if(hand==6)rect(cx-27,cy,27,3,211,155,235);
    else{rect(cx-18,cy-18,3,18,211,155,235);rect(cx-18,cy-18,18,3,211,155,235);}
    rect(cx-50-p,cy-2-p,5+p*2,5+p*2,87,192,215);rect(cx+46-p,cy+12-p,4+p*2,4+p*2,154,79,191);
}
static void title_moko_art(void){
    int p=(title_tick/9)&3;
    rect(128,153,64,8,18,22,39);rect(135,160,50,3,42,45,70);
    moko_sprite_draw(154,151,1,(title_tick/7)&7,0,title_tick,db[active].ot,&next_packet);
    rect(170,169,14+p,3,180,83,216);rect(181+p,166,3,8,225,181,245);
}
static void title_screen_art(void){
    int can_continue=profile.has_checkpoint?1:0;
    if(!can_continue&&title_choice)title_choice=0;
    title_tick++;
    title_clock_art(160,93);title_moko_art();
    rect(55,184,210,42,8,11,26);rect(59,188,202,34,17,20,40);
    rect(68,191+title_choice*14,184,12,49,31,69);
    if(title_choice==0)rect(72,194,5,5,213,158,235);else rect(72,208,5,5,213,158,235);
    FntPrint(journal_font_id," M O K O :  T H E  L O S T  H O U R\n\n\n\n\n\n\n\n\n\n\n\n       %s NEW GAME\n       %s CONTINUE\n\n",title_choice==0?">":" ",title_choice==1?">":" ");
    if(can_continue)FntPrint(journal_font_id," CARD: SHARDS %d/4  BEST %lu  CLEARS %lu\n",profile.checkpoint_shards,(unsigned long)profile.best_score,(unsigned long)profile.clears);
    else FntPrint(journal_font_id," CARD: NO CHECKPOINT - BEGIN A NEW MEMORY\n");
    FntPrint(journal_font_id," UP/DOWN SELECT  CROSS CONFIRM   TITLE REV 268");
}
static void tutorial_input(uint16_t n){
    if(!(n&PAD_LEFT)||!(n&PAD_RIGHT)||!(n&PAD_UP)||!(n&PAD_DOWN))tutorial_flags|=1;
    if(pressed(n,PAD_CROSS))tutorial_flags|=2;
    if(pressed(n,PAD_R1))tutorial_flags|=4;
    if(pressed(n,PAD_SQUARE))tutorial_flags|=8;
}
static void tutorial_art(void){
    int step=-1,p=(anim_tick/9)&3;
    if(tutorial_flags==15||room>0)return;
    if(!(tutorial_flags&1))step=0;else if(!(tutorial_flags&2))step=1;else if(!(tutorial_flags&4))step=2;else if(!(tutorial_flags&8))step=3;
    if(step<0)return;
    rect(20,177,280,29,7,10,23);rect(24,181,272,21,21,24,43);rect(24,181,4+p,21,114,58,150);
    if(step==0)FntPrint(font_id,"\nMEMORY LESSON 1/4  D-PAD - MOVE MOKO");
    else if(step==1)FntPrint(font_id,"\nMEMORY LESSON 2/4  CROSS - INTERACT");
    else if(step==2)FntPrint(font_id,"\nMEMORY LESSON 3/4  R1 - MEMORY DASH");
    else FntPrint(font_id,"\nMEMORY LESSON 4/4  SQUARE - CLOCK GUARD");
}
'''
if anchor not in src:
    raise SystemExit('title/tutorial helper anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

reset_anchor = 'static void reset_game(void){int i;px=20;py=190;room=0;'
if reset_anchor not in src:
    raise SystemExit('new game tutorial reset anchor missing')
src = src.replace(reset_anchor, 'static void reset_game(void){int i;tutorial_flags=0;px=20;py=190;room=0;', 1)
continue_anchor = 'static void continue_game(void){int i;reset_game();'
if continue_anchor not in src:
    raise SystemExit('continue tutorial anchor missing')
src = src.replace(continue_anchor, 'static void continue_game(void){int i;reset_game();tutorial_flags=15;', 1)

play_anchor = '}else if(state==STATE_PLAY){update_play(n);room_art();hud();}'
if play_anchor not in src:
    raise SystemExit('play tutorial hook missing')
src = src.replace(play_anchor, '}else if(state==STATE_PLAY){tutorial_input(n);update_play(n);room_art();hud();tutorial_art();}', 1)

title_pattern = re.compile(r'if\(state==STATE_TITLE\)\{.*?\}else if\(state==STATE_PLAY\)', re.S)
title_replacement = r'''if(state==STATE_TITLE){
    title_screen_art();FntFlush(journal_font_id);
    if(pressed(n,PAD_UP)||pressed(n,PAD_DOWN)){if(profile.has_checkpoint){title_choice^=1;sfx(0x0d00);}else title_choice=0;}
    if(profile.has_checkpoint&&pressed(n,PAD_TRIANGLE)){title_choice=1;continue_game();}
    else if(pressed(n,PAD_START)){title_choice=0;reset_game();}
    else if(pressed(n,PAD_CROSS)){if(title_choice==1&&profile.has_checkpoint)continue_game();else reset_game();}
}else if(state==STATE_PLAY)'''
src, count = title_pattern.subn(lambda _m: title_replacement, src, count=1)
if count != 1:
    raise SystemExit('title screen state anchor missing')

pathlib.Path(sys.argv[2]).write_text(src)
