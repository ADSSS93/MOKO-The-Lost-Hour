import pathlib, re, sys

src = pathlib.Path(sys.argv[1]).read_text()

body = r'''int i;/* Distinct enemy/NPC renderer tied to live gameplay state */
for(i=0;i<ambient_count(&living.ambient);i++){const MokoAmbientParticle*p=ambient_particle(&living.ambient,i);if(!p)continue;if(p->kind==AMBIENT_RAIN)rect(p->x,p->y,1,5,90,120,170);else if(p->kind==AMBIENT_SPARK)rect(p->x,p->y,2,2,235,160,55);else if(p->kind==AMBIENT_GEAR)rect(p->x,p->y,4,4,145,100,40);else rect(p->x,p->y,2,2,75,100,115);}
/* NPC silhouettes */
for(i=0;i<MOKO_NPC_COUNT;i++){const MokoNpcDef*n=npc_get(i);int pending,bob;if(!n||n->room!=room)continue;bob=(anim_tick/16+i)&1;if(n->kind==NPC_CAT){rect(n->x-7,n->y-10-bob,16,9,75,95,125);rect(n->x-5,n->y-15-bob,5,7,60,78,108);rect(n->x+4,n->y-15-bob,5,7,60,78,108);rect(n->x+5,n->y-8-bob,3,3,238,194,115);rect(n->x-8,n->y-2-bob,5,3,154,93,160);}else{rect(n->x-5,n->y-16-bob,12,17,50,82,108);rect(n->x-3,n->y-22-bob,8,8,194,166,137);rect(n->x-4,n->y-24-bob,10,3,33,45,67);rect(n->x+7,n->y-11-bob,3,8,94,194,215);}pending=adventure_npc_delivery_required(i)?!adventure_npc_delivered(&adventure,i):!quests_is_clear(&adventure.quests,n->quest);if(!adventure_npc_met(&adventure,i))rect(n->x-2,n->y-31,6,7,245,205,74);else if(pending)rect(n->x-2,n->y-31,6,6,68,218,239);}
/* Every live enemy kind gets a unique readable silhouette. Flash white on dash damage. */
for(i=0;i<MOKO_ENEMY_COUNT;i++){const MokoEnemy*e=enemies_get(&living.enemies,i);int f,b;if(!e||!e->active||e->room!=room||e->kind==ENEMY_HOUR_WARDEN)continue;f=e->hit_cooldown&&((anim_tick/2)&1);b=(anim_tick/6+i)&1;
if(e->kind==ENEMY_TICKHOUND){rect(e->x-9,e->y-10,19,10,f?245:142,f?245:55,f?245:78);rect(e->x+6,e->y-15,8,8,f?245:181,f?245:76,f?245:84);rect(e->x+10,e->y-13,3,3,250,213,91);rect(e->x-7,e->y,4,6,55,28,39);rect(e->x+4,e->y,4,6,55,28,39);rect(e->x-13,e->y-8,6,3,199,65,105);}
else if(e->kind==ENEMY_RAINLING){rect(e->x-7,e->y-15-b,15,20,f?245:51,f?245:126,f?245:176);rect(e->x-10,e->y-14-b,5,13,70,168,209);rect(e->x+8,e->y-14-b,5,13,70,168,209);rect(e->x-3,e->y-11-b,3,3,230,248,255);rect(e->x+3,e->y-11-b,3,3,230,248,255);rect(e->x-2,e->y+5,2,6,98,195,226);rect(e->x+4,e->y+5,2,8,98,195,226);}
else if(e->kind==ENEMY_SHADOW){rect(e->x-8,e->y-18,17,22,f?245:43,f?245:25,f?245:68);rect(e->x-5,e->y-24,11,9,f?245:68,f?245:32,f?245:91);rect(e->x-4,e->y-20,3,3,225,68,232);rect(e->x+3,e->y-20,3,3,225,68,232);rect(e->x-12-b,e->y-7,5,12,61,31,84);rect(e->x+9+b,e->y-7,5,12,61,31,84);}
else if(e->kind==ENEMY_GEARLING){rect(e->x-9,e->y-11,19,19,f?245:157,f?245:95,f?245:34);rect(e->x-5,e->y-7,11,11,f?245:227,f?245:155,f?245:49);rect(e->x-2,e->y-4,5,5,55,36,22);rect(e->x-11,e->y-3,4,5,211,126,38);rect(e->x+8,e->y-3,4,5,211,126,38);rect(e->x-2,e->y-13-b,4,4,244,187,59);}
else if(e->kind==ENEMY_WATCHER){rect(e->x-9,e->y-17,19,19,f?245:73,f?245:90,f?245:125);rect(e->x-6,e->y-14,13,9,25,33,53);rect(e->x-3,e->y-12,7,5,237,80,112);rect(e->x-2,e->y-11,3,3,255,218,118);rect(e->x-4,e->y+2,5,10,55,65,88);rect(e->x+2,e->y+2,5,10,55,65,88);if((e->phase&15)<8)rect(e->x-16,e->y-9,7,2,218,61,102);}
else if(e->kind==ENEMY_CHRONO_MITE){rect(e->x-8,e->y-7-b,17,9,f?245:92,f?245:174,f?245:181);rect(e->x-5,e->y-11-b,11,6,f?245:135,f?245:218,f?245:214);rect(e->x-3,e->y-9-b,3,3,27,50,55);rect(e->x+3,e->y-9-b,3,3,27,50,55);rect(e->x-10,e->y+1-b,5,2,76,133,145);rect(e->x+7,e->y+1-b,5,2,76,133,145);}
else if(e->kind==ENEMY_PENDULUM_WISP){rect(e->x-6,e->y-16-b,13,13,f?245:130,f?245:62,f?245:176);rect(e->x-3,e->y-13-b,7,7,f?255:217,f?255:108,f?255:231);rect(e->x,e->y-3-b,2,12,184,126,201);rect(e->x-4,e->y+8-b,10,3,228,174,92);rect(e->x-2,e->y+11-b,6,4,126,68,157);}
/* HP pips appear only for multi-hit enemies, so damage is legible. */
if(enemies_max_hp(e->kind)>1){int h;for(h=0;h<enemies_max_hp(e->kind);h++)rect(e->x-8+h*6,e->y-29,5,2,h<e->hp?232:58,h<e->hp?82:35,h<e->hp?103:48);}
}
'''

pattern = r"static void living_art\(void\)\{.*?\}\nstatic void room_art"
repl = "static void living_art(void){" + body + "}\nstatic void room_art"
src, count = re.subn(pattern, repl, src, count=1, flags=re.S)
if count != 1:
    raise SystemExit("could not replace living_art")

# The finale owns the Hour Warden now. Disable the legacy world-runtime boss instance
# after each new-game reset so there is one boss, one collision model and one HP source.
needle = "world_runtime_reset(&living,0);for(i=0;i<4;i++)"
replacement = "world_runtime_reset(&living,0);living.enemies.e[12].active=0;living.enemies.e[12].hp=0;for(i=0;i<4;i++)"
if needle not in src:
    raise SystemExit("could not disable legacy duplicate Warden")
src = src.replace(needle, replacement, 1)

src = src.replace("BOSS REV 245", "ENEMY REV 249", 1)
src = src.replace("B245 %02d:%02d", "E249 %02d:%02d", 1)

pathlib.Path(sys.argv[2]).write_text(src)
