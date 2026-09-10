import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Three one-shot Time Anchors give the final arena readable recovery goals.
state_anchor = 'static int clock_relays=0;static uint8_t clock_relay_on[3]={0};'
if state_anchor not in src:
    raise SystemExit('Clockworks state anchor missing')
src = src.replace(state_anchor, state_anchor + '\nstatic int chamber_anchors=0;static uint8_t chamber_anchor_used[3]={0};', 1)

art_anchor = 'static void world_event_art(void)'
if art_anchor not in src:
    raise SystemExit('world event art anchor missing')
art = r'''static void hour_chamber_polish_art(void){
    int i,p=(anim_tick/6)&3;int ax[3]={58,160,262};int ay[3]={181,188,181};
    if(room!=4)return;
    rect(109,66,102,5,102,54,67);rect(109,157,102,5,102,54,67);
    rect(105,75,5,78,88,46,59);rect(210,75,5,78,88,46,59);
    for(i=0;i<8;i++){int tx=116+(i%4)*29,ty=77+(i/4)*68;rect(tx,ty,8,3,183,125,72);}
    rect(158,92,4,48,124,73,83);rect(160,112,28,4,124,73,83);rect(158,111,5,5,232,190,101);
    tri(30,207,96,165,115,207,42,23,31);tri(205,207,224,165,290,207,42,23,31);tri(118,207,160,169,202,207,55,28,37);
    for(i=0;i<3;i++){
        if(!chamber_anchor_used[i]){int glow=4+p;rect(ax[i]-glow,ay[i]-glow,10+glow*2,10+glow*2,43,27,58);rect(ax[i]-5,ay[i]-9,12,18,107,58,145);rect(ax[i]-2,ay[i]-5,6,8,225,177,91);rect(ax[i],ay[i]-3,1,5,46,38,48);rect(ax[i],ay[i],4,1,46,38,48);}
        else{rect(ax[i]-5,ay[i]+5,12,3,61,48,65);rect(ax[i]-1,ay[i],4,5,92,72,96);}
    }
    if(finale_hazard_active(&finale)){int sx=finale_sweep_x(&finale),sy=finale_sweep_y(&finale);rect(sx-5,202,13,3,241,161,75);rect(sx-2,198,7,3,184,85,82);if(finale.phase==FINALE_STABILIZE){rect(25,sy-2,7,7,231,137,75);rect(288,sy-2,7,7,231,137,75);}}
    if(finale.phase==FINALE_STABILIZE&&finale.boss_flash>0){int bx=finale_boss_x(&finale),by=finale_boss_y(&finale);rect(bx-9-p,by-9-p,38+p*2,38+p*2,116,52,141);rect(bx-4,by-4,28,28,232,166,91);}
}
'''
src = src.replace(art_anchor, art + art_anchor, 1)
room_old = 'else chamber_art();'
if room_old not in src: raise SystemExit('Hour Chamber render anchor missing')
src = src.replace(room_old, 'else {chamber_art();hour_chamber_polish_art();}', 1)
update_anchor = 'static void update_play(uint16_t n)'
if update_anchor not in src: raise SystemExit('update_play anchor missing')
logic = r'''static void hour_chamber_polish_tick(uint16_t n){
    int i;int ax[3]={58,160,262};int ay[3]={181,188,181};
    if(room!=4||finale.phase!=FINALE_STABILIZE)return;
    if(pressed(n,PAD_CROSS))for(i=0;i<3;i++)if(!chamber_anchor_used[i]&&hit(px,py,12,18,ax[i]-14,ay[i]-14,38,34)){
        chamber_anchor_used[i]=1;chamber_anchors++;finale.stability+=20;if(finale.stability>100)finale.stability=100;
        finale.phase_timer+=90;score+=125;gameplay_reward(&gameplay,45);sfx(0x3100);break;
    }
}
'''
src = src.replace(update_anchor, logic + update_anchor, 1)
tick_anchor = 'station_traversal_tick(n);backward_street_tick(n);forgotten_house_tick(n);clockworks_expansion_tick(n);'
if tick_anchor not in src: raise SystemExit('authored gameplay tick chain missing')
src = src.replace(tick_anchor, tick_anchor + 'hour_chamber_polish_tick(n);', 1)
hud_old = 'if(room==3&&px>315)FntPrint(font_id,"CHRONO RELAYS %d/3  SENTINEL %s\\n",clock_relays,sentinel_defeated?"DOWN":"ACTIVE");'
if hud_old not in src: raise SystemExit('Clockworks HUD anchor missing')
src = src.replace(hud_old, hud_old + 'if(room==4&&finale.phase==FINALE_STABILIZE)FntPrint(font_id,"TIME ANCHORS %d/3  STABILITY %d%%\\n",chamber_anchors,finale.stability);', 1)
reset_anchor = 'clock_relays=0;clock_relay_on[0]=clock_relay_on[1]=clock_relay_on[2]=0;'
if reset_anchor not in src: raise SystemExit('Clockworks reset anchor missing')
src = src.replace(reset_anchor, reset_anchor + 'chamber_anchors=0;chamber_anchor_used[0]=chamber_anchor_used[1]=chamber_anchor_used[2]=0;', 1)
marker = 'CLOCKWORKS EXPANSION REV 279'
if marker not in src: raise SystemExit('Clockworks marker missing')
src = src.replace(marker, 'HOUR CHAMBER POLISH REV 280  ' + marker, 1)
pathlib.Path(sys.argv[2]).write_text(src)
