import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V7 REV 295' not in src:
    raise SystemExit('Village v7 marker missing')
src=src.replace('VILLAGE 3D V7 REV 295','VILLAGE 3D V8 REV 296 / VILLAGE 3D V7 REV 295',1)

# REV296 is a coherence pass: what the player sees in XYZ must match the real
# mission collision/progression coordinates used by the vertical slice.
# Splinters now disappear as they are collected instead of appearing afterwards.
src=src.replace('if(motes>0)splinter(ot,pk,wx(112),115,wz(170),tick);','if(motes<1)splinter(ot,pk,wx(112),115,wz(170),tick);',1)
src=src.replace('if(motes>1)splinter(ot,pk,wx(236),92,wz(145),tick+11);','if(motes<2)splinter(ot,pk,wx(236),92,wz(145),tick+11);',1)
src=src.replace('if(motes>2)splinter(ot,pk,wx(274),120,wz(176),tick+23);','if(motes<3)splinter(ot,pk,wx(274),120,wz(176),tick+23);',1)

# The Shadow Boar is an authored encounter beat, not scenery. Keep it out of the
# street until all three splinters have been recovered so its visual presence
# agrees with the combat state.
old='boar(ot,pk,wx(258),wz(168),enemy_hp,tick);gate(ot,pk,clear,tick);dawn_gate_flourish(ot,pk,clear,tick);'
new='if(motes>=3)boar(ot,pk,wx(258),wz(168),enemy_hp,tick);gate(ot,pk,clear,tick);dawn_gate_flourish(ot,pk,clear,tick);'
if old not in src:
    raise SystemExit('rev296 boar draw anchor missing')
src=src.replace(old,new,1)

# Camera staging follows the same encounter geography: NPC ~205, Boar ~258,
# Dawn Gate ~385 in gameplay X. The gate reveal therefore frames the actual arch.
old='else if(px>=226&&px<286){desired_z-=34;}\n    else if(px>=286){desired_x=(desired_x*3+wx(296))/4;desired_z=(desired_z*3+1215)/4;}'
new='else if(px>=226&&px<330){desired_z-=34;}\n    else if(px>=330){desired_x=(desired_x*3+902)/4;desired_z=(desired_z*3+1360)/4;}'
if old not in src:
    raise SystemExit('rev296 camera geography anchor missing')
src=src.replace(old,new,1)
old2='else if(px>=226&&px<286)target_pitch=199;else if(px>=286){target_pitch=182;target_yaw=-6;}'
new2='else if(px>=226&&px<330)target_pitch=199;else if(px>=330){target_pitch=182;target_yaw=-6;}'
if old2 not in src:
    raise SystemExit('rev296 camera angle anchor missing')
src=src.replace(old2,new2,1)

# Keep a regression marker that CI can assert without confusing build success
# with emulator/visual validation.
src+='\n/* REV296 COHERENT XYZ MISSION SPACE: NPC 205 / BOAR 258 / GATE 385 */\n'
pathlib.Path(sys.argv[2]).write_text(src)
