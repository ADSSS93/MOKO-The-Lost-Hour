import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()
anchor = 'static void room_art(void)'
helpers = r'''static int delivery_target(int*x,int*y){
    if(room==1&&adventure_item_count(&adventure,ITEM_LETTER)>0&&!adventure_npc_delivered(&adventure,2)){*x=118;*y=188;return 1;}
    if(room==1&&adventure_item_count(&adventure,ITEM_UMBRELLA)>0&&!adventure_npc_delivered(&adventure,3)){*x=252;*y=174;return 2;}
    if(room==2&&adventure_item_count(&adventure,ITEM_PORTRAIT)>=4&&!adventure_npc_delivered(&adventure,4)){*x=54;*y=184;return 3;}
    if(room==3&&adventure_item_count(&adventure,ITEM_LUNCHBOX)>0&&!adventure_npc_delivered(&adventure,6)){*x=58;*y=184;return 4;}
    if(room==3&&adventure_item_count(&adventure,ITEM_TINY_GEAR)>=7&&!adventure_npc_delivered(&adventure,7)){*x=272;*y=184;return 5;}
    return 0;
}
static const char*delivery_text(void){int x,y,d=delivery_target(&x,&y);if(d==1)return "DELIVERY: SOAKED LETTER -> ELI";if(d==2)return "DELIVERY: LOST UMBRELLA -> UMBRELLA MAN";if(d==3)return "DELIVERY: 4 PORTRAITS -> MARA";if(d==4)return "DELIVERY: LUNCHBOX -> ORIN";if(d==5)return "DELIVERY: 7 TINY GEARS -> GEAR KID";return "";}
static void carried_item_icon(int kind){int y=py-12-((anim_tick/10)&1);rect(px+4,y,9,8,32,18,48);if(kind==1){rect(px+5,y+1,7,5,220,205,170);rect(px+7,y+2,3,2,115,65,80);}else if(kind==2){rect(px+7,y,2,6,85,185,225);rect(px+4,y+5,8,2,65,125,185);}else if(kind==3){rect(px+5,y+1,7,5,165,120,80);rect(px+6,y+2,5,3,225,190,135);}else if(kind==4){rect(px+5,y+2,7,5,180,75,45);rect(px+7,y,3,2,220,150,75);}else{rect(px+5,y+1,7,7,185,120,35);rect(px+7,y+3,3,3,55,35,20);}}
static void delivery_world_changes(void){int i;
    if(room==1&&adventure_npc_delivered(&adventure,2)){rect(92,166,20,18,42,35,55);rect(95,169,14,9,205,175,115);rect(99,173,6,3,95,210,225);}
    if(room==1&&adventure_npc_delivered(&adventure,3)){rect(236,150,4,34,55,65,85);rect(229,149,18,3,80,185,225);rect(231,146,14,3,110,215,245);}
    if(room==2&&adventure_npc_delivered(&adventure,4)){for(i=0;i<4;i++){int x=20+i*22;rect(x,74,18,24,72,51,37);rect(x+3,77,12,16,205,170,125);rect(x+6,80,6,8,88+i*18,70+i*12,72+i*14);}}
    if(room==3&&adventure_npc_delivered(&adventure,6)){rect(66,151,42,27,70,47,22);rect(70,155,34,19,135,88,28);rect(74,159,6,6,75,225,120);rect(88,159,12,4,225,165,55);}
    if(room==3&&adventure_npc_delivered(&adventure,7)){for(i=0;i<7;i++){int x=214+(i%4)*18,y=142+(i/4)*18;rect(x,y,12,12,112,72,24);rect(x+3,y+3,6,6,220,150,45);rect(x+5,y+5,2,2,55,35,20);}}
}
static void delivery_art(void){int x=0,y=0,d=delivery_target(&x,&y),p;if(d){p=2+((anim_tick/7)&3);rect(x-7-p,y-25-p,14+p*2,14+p*2,35,85,105);rect(x-5,y-23,10,10,90,225,240);rect(x-1,y-20,3,4,245,250,255);carried_item_icon(d);}delivery_world_changes();}
'''
if anchor not in src: raise SystemExit('room_art anchor missing')
src = src.replace(anchor, helpers + anchor, 1)
needle = 'draw_moko();}'
replacement = 'draw_moko();delivery_art();}'
if needle not in src: raise SystemExit('draw moko anchor missing')
src = src.replace(needle, replacement, 1)
needle = 'if(ni>=0){const MokoNpcDef*p=npc_get(ni);'
replacement = 'if(delivery_text()[0])FntPrint(font_id,"\\n%s",delivery_text());if(ni>=0){const MokoNpcDef*p=npc_get(ni);'
if needle not in src: raise SystemExit('HUD NPC anchor missing')
src = src.replace(needle, replacement, 1)
src = src.replace('MISSION REV 253','DELIVERY REV 254',1)
src = src.replace('M253 %02d:%02d','D254 %02d:%02d',1)
pathlib.Path(sys.argv[2]).write_text(src)
