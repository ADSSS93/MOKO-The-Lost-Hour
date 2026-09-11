import pathlib,re,sys,subprocess
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V9 REV 297' not in src:
    raise SystemExit('Village v9 marker missing')
src=src.replace('VILLAGE 3D V9 REV 297','VILLAGE 3D V10 REV 299 / VILLAGE 3D V9 REV 297',1)

# Match the rendered collectibles exactly to REV298 gameplay coordinates.
src=src.replace('if(motes<2)splinter(ot,pk,wx(236),92,wz(145),tick+11);','if(motes<2)splinter(ot,pk,wx(244),92,wz(145),tick+11);',1)
src=src.replace('if(motes<3)splinter(ot,pk,wx(274),120,wz(176),tick+23);','if(motes<3)splinter(ot,pk,wx(285),120,wz(176),tick+23);',1)

# Give the Shadow Boar its own readable encounter pocket rather than overlapping
# the last collectible. This is the same X used by slice_tick().
src=src.replace('if(motes>=3)boar(ot,pk,wx(258),wz(168),enemy_hp,tick);','if(motes>=3)boar(ot,pk,wx(320),wz(168),enemy_hp,tick);',1)

# Re-stage the spring camera around the authored mission beats: clockmaker,
# collection lane, Boar arena, then Dawn Gate. No hard cuts.
src=src.replace('else if(px>=226&&px<330){desired_z-=34;}\n    else if(px>=330){desired_x=(desired_x*3+902)/4;desired_z=(desired_z*3+1360)/4;}',
'''else if(px>=226&&px<292){desired_z-=28;}\n    else if(px>=292&&px<352){desired_x=(desired_x*3+wx(320))/4;desired_z=(desired_z*3+wz(168))/4;}\n    else if(px>=352){desired_x=(desired_x*3+902)/4;desired_z=(desired_z*3+1360)/4;}''',1)
src=src.replace('else if(px>=226&&px<330)target_pitch=170;else if(px>=330){target_pitch=158;target_yaw=-6;}',
'''else if(px>=226&&px<292)target_pitch=168;else if(px>=292&&px<352){target_pitch=164;target_yaw=facing?5:-5;}else if(px>=352){target_pitch=156;target_yaw=-5;}''',1)

# Small world-space encounter framing: stone posts and lanterns define the Boar
# pocket without screen-space debug shapes.
anchor='static void foreground_frame(uint32_t*ot,char**pk,int tick){'
if anchor not in src: raise SystemExit('rev299 foreground anchor missing')
helper=r'''static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){
    int pulse=8+((tick/7)&3)*4;
    /* Clockmaker approach markers. */
    box3(ot,pk,wx(188),145,wz(151),12,40,14,98,76,54);
    prism(ot,pk,wx(194),126,wz(151)-2,25,23,16,206,153,76);
    /* Boar arena posts appear as the mission opens. */
    if(motes>=3&&!clear){
        box3(ot,pk,wx(292),130,wz(184),16,56,18,89,68,62);
        box3(ot,pk,wx(348),130,wz(184),16,56,18,89,68,62);
        prism(ot,pk,wx(300),118-pulse/4,wz(184)-4,18,23,13,181,86,126);
        prism(ot,pk,wx(356),118-pulse/4,wz(184)-4,18,23,13,181,86,126);
    }
    /* Gate lamps brighten only once the encounter is won. */
    if(enemy_hp<=0){
        prism(ot,pk,wx(369),92-pulse/3,wz(145),17,27,14,112,220,196);
        prism(ot,pk,wx(401),92-pulse/3,wz(145),17,27,14,112,220,196);
    }
}
'''
src=src.replace(anchor,helper+anchor,1)
needle='village_life_v7(ot,pk,tick,motes,enemy_hp,clear);'
if needle not in src: raise SystemExit('rev299 village-life anchor missing')
src=src.replace(needle,needle+'playable_area_frame_v10(ot,pk,motes,enemy_hp,clear,tick);',1)

src+='\n/* REV299 PLAYABLE AREA RENDER CONTRACT: SPLINTERS 112/244/285 BOAR 320 GATE 385 */\n'
out=pathlib.Path(sys.argv[2]);out.write_text(src)
subprocess.check_call([sys.executable,str(pathlib.Path(__file__).with_name('build_world3d_slice_v11.py')),str(out),str(out)])
subprocess.check_call([sys.executable,str(pathlib.Path(__file__).with_name('build_world3d_slice_v12.py')),str(out),str(out)])
subprocess.check_call([sys.executable,str(pathlib.Path(__file__).with_name('build_world3d_slice_v13.py')),str(out),str(out)])
