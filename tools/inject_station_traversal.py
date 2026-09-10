import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

# Add authored traversal visuals inside the scrolling half of Silent Station.
art_anchor = 'static void station_scroll_art(void){'
if art_anchor not in src:
    raise SystemExit('station_scroll_art anchor missing')

art = r'''static void station_route_art(void){
    int i,cart;
    if(room!=0)return;
    /* Broken temporal track: three dangerous floor gaps under the catwalk route. */
    for(i=0;i<3;i++){
        int x=(i==0?282:(i==1?418:538));
        int w=(i==0?74:(i==1?54:48));
        rect(x,199,w,17,8,10,19);
        tri(x,199,x+w,199,x+w-7,205,58,24,42);
        tri(x,216,x+w,216,x+7,208,28,17,31);
        rect(x+5,207,w-10,2,120+((anim_tick+i*7)&31),35,65);
    }
    /* Maintenance arches make the route read as a real station structure. */
    for(i=0;i<3;i++){
        int x=326+i*104;
        rect(x,105,7,88,42,46,66);rect(x+70,105,7,88,42,46,66);
        tri(x-5,105,x+82,105,x+38,88,72,62,80);
        rect(x+19,96,40,4,126,105,73);
    }
    /* Moving baggage cart: a readable, animated ground hazard. */
    cart=346+((anim_tick*2)%170);
    rect(cart,177,31,13,67,48,62);rect(cart+4,173,22,6,92,65,76);
    tri(cart+2,177,cart+15,165,cart+28,177,98,71,84);
    rect(cart+5,190,6,3,22,25,35);rect(cart+21,190,6,3,22,25,35);
    /* Destination clock above the high catwalk visually pulls the player forward. */
    rect(486,136,28,28,38,27,52);rect(491,141,18,18,112,74,139);
    rect(499,144,2,8,225,190,100);rect(500,150,7,2,225,190,100);
    tri(482,139,518,139,500,123,76,47,91);
    /* Exit signal tower at the far end of the extended level. */
    rect(598,92,20,88,39,40,58);rect(602,99,12,32,17,24,39);
    rect(605,103,6,6,shard_taken[0]?55:188,shard_taken[0]?220:62,shard_taken[0]?112:70);
    rect(605,116,6,6,puzzle_done[0]?210:92,puzzle_done[0]?173:75,70);
}
'''
src = src.replace(art_anchor, art + art_anchor, 1)

station_start = 'static void station_scroll_art(void){\n    int i,pulse=(anim_tick/10)&3;\n    if(room!=0)return;'
if station_start not in src:
    raise SystemExit('station scroll body anchor missing')
src = src.replace(station_start, station_start + '\n    station_route_art();', 1)

# Real gameplay consequences for the new geometry. The low track is unsafe, but
# the upper/depth lane remains a valid alternate route; raised catwalks are safe.
update_anchor = 'static void update_play(uint16_t n)'
if update_anchor not in src:
    raise SystemExit('update_play anchor missing')
logic = r'''static void station_traversal_tick(uint16_t n){
    int cart;
    (void)n;
    if(room!=0)return;
    /* Temporal rail gaps punish staying on the low base floor. Jumping onto a
       catwalk or moving into the rear lane avoids them, creating route choice. */
    if(py>170&&moko_floor_z==0&&(moko_z-moko_floor_z)<112){
        if((px>=282&&px<=356)||(px>=418&&px<=472)||(px>=538&&px<=586))hurt();
    }
    /* Moving baggage cart can be cleared with a proper jump. */
    cart=346+((anim_tick*2)%170);
    if(moko_floor_z==0&&(moko_z-moko_floor_z)<150&&hit(px,py,12,18,cart-5,166,41,29))hurt();
}
'''
src = src.replace(update_anchor, logic + update_anchor, 1)

input_anchor = 'moko_jump_tick(n);moko_tail_tick(n);'
if input_anchor not in src:
    raise SystemExit('platform tick anchor missing')
src = src.replace(input_anchor, input_anchor + 'station_traversal_tick(n);', 1)

# Keep a visible diagnostic marker in the actual executable/BIN.
marker = 'CAMERA REV 275'
if marker not in src:
    raise SystemExit('camera marker missing')
src = src.replace(marker, 'STATION LEVEL REV 276  CAMERA REV 275', 1)

pathlib.Path(sys.argv[2]).write_text(src)
