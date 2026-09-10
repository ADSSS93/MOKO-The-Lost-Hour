import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

anchor = 'static int warden_phase_level(void)'
helpers = r'''static void story_setpiece_art(void){
    int p=(anim_tick/8)&3,i;
    /* Silent Station - the Last Train Home physically materialises as the chain advances. */
    if(room==0){
        if(adventure.world.collected[2]){rect(28,126,264,3,48,88,112);rect(36,130,248,2,24,48,68);}
        if(adventure.world.collected[3]){
            int tx=34+((anim_tick/3)%34);
            rect(tx,139,196,35,30,43,62);rect(tx+8,145,180,21,62,81,105);
            for(i=0;i<5;i++){rect(tx+15+i*34,148,22,12,106,174,190);rect(tx+19+i*34,151,14,6,183,226,232);}
            rect(tx+188,148,20,18,42,55,73);
            rect(tx+22,174,154,3,121,97,68);
        }
        if(adventure.world.collected[4]){rect(232,151,21,23,25,27,42);rect(237,154,11,13,110,87,123);rect(240,158,5,5,210,184,225);}
        if(adventure.world.collected[64]){
            rect(250-p,69-p,18+p*2,18+p*2,54,43,26);rect(253,72,12,12,223,184,86);rect(258,74,2,7,31,25,31);rect(258,78,5,2,31,25,31);
            FntPrint(font_id,"\nLAST TRAIN: CONDUCTOR'S WATCH RECOVERED");
        }
    }
    /* Backward Street - reverse rain becomes a visible skyward river and altar. */
    else if(room==1){
        if(adventure.world.collected[8])for(i=0;i<12;i++)rect(18+i*25,188-((anim_tick+i*11)%86),2,8,68,126,173);
        if(adventure.world.collected[9]){rect(104,178,72,6,26,52,73);rect(111,174,58,4,78,142,174);}
        if(adventure.world.collected[10])for(i=0;i<8;i++)rect(82+i*26,78-((anim_tick/2+i*9)%38),3,10,93,171,205);
        if(adventure.world.collected[65]){rect(122,69,30,22,47,28,72);rect(128,73,18,14,125,65,164);rect(135,66,4,28,214,143,229);}
        if(adventure.world.collected[66]){rect(182,63,38,5,72,136,170);rect(191,58,20,5,117,192,218);FntPrint(font_id,"\nRAIN TRAIL: FOLLOW THE DROP INTO THE SKY");}
    }
    /* House Without Morning - portrait wall and midnight table rebuild during their quests. */
    else if(room==2){
        int pieces=adventure.world.collected[17]+adventure.world.collected[18]+adventure.world.collected[19]+adventure.world.collected[20];
        if(pieces){rect(34,72,72,55,46,34,28);rect(39,77,62,45,20,28,31);for(i=0;i<pieces;i++){int x=43+(i&1)*29,y=81+(i>>1)*19;rect(x,y,25,16,112,91,74);rect(x+8,y+3,8,7,184,157,132);}}
        if(adventure.world.collected[21]){rect(118,166,96,8,68,54,42);rect(128,174,6,27,55,44,35);rect(198,174,6,27,55,44,35);}
        if(adventure.world.collected[22]){rect(145,157,14,8,185,174,142);rect(148,153,8,5,224,212,176);}
        if(adventure.world.collected[57]){rect(178,130,28,21,43,68,65);rect(183,134,18,13,134,184,167);}
        if(adventure.world.collected[67]||adventure.world.collected[68]){rect(169,158,12,8,190,175,140);rect(172,154,6,5,229,216,184);FntPrint(font_id,"\nMIDNIGHT TEA: THE SECOND CUP IS WARM");}
    }
    /* Clockworks - the hidden bell machine progressively returns to life. */
    else if(room==3){
        if(adventure.world.collected[36]){rect(202,72,42,34,62,43,21);rect(208,78,30,22,154,100,34);rect(220,82,6,14,44,31,19);}
        if(adventure.world.collected[60]){rect(72,66,46,24,72,50,24);for(i=0;i<4;i++)rect(78+i*9,72,6,11,173,112,35);}
        if(adventure.world.collected[69]){rect(160,65,46,5,194,126,38);rect(180,55,5,26,222,153,52);}
        if(adventure.world.collected[70]){int glow=65+p*25;rect(264-p,164-p,34+p*2,29+p*2,glow,48,22);rect(270,170,22,17,220,126,39);rect(278,174,7,7,250,197,86);}
        if(adventure.world.collected[71]){for(i=0;i<6;i++)rect(212+i*12,108-((anim_tick+i*5)%24),3,8,235,175,63);FntPrint(font_id,"\nBELL MACHINE: HEART BEATING AGAIN");}
    }
}
'''
if anchor not in src: raise SystemExit('story setpiece helper anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

needle = 'world_event_art();echo_art();temporal_pickups();'
replacement = 'story_setpiece_art();world_event_art();echo_art();temporal_pickups();'
if needle not in src: raise SystemExit('story setpiece room anchor missing')
src = src.replace(needle, replacement, 1)

src = src.replace('PICKUP REV 262','STORY REV 263',1)
src = src.replace('P262 %02d:%02d','S263 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
