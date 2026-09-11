import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V18 REV 308 / VILLAGE 3D V17 REV 307 / VILLAGE 3D V16 REV 306 / VILLAGE 3D V15 REV 305 / VILLAGE 3D V14 REV 304 / VILLAGE 3D V13 REV 303',1)

# REV308 is a structural presentation rebuild, not another decoration pass.  The
# reference target is a late-PS1 2.5D adventure frame: readable hero, a clear
# playable lane, dense mid-ground landmarks, and deeper background silhouettes.
# Keep the near plane free of little solids: previous runtime QA proved that they
# can explode into giant PS1 projection wedges.
pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}',re.S)
replacement=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){
    (void)tick;
    /* Three broad, safe ground bands establish perspective and fill the frame. */
    quad3g(ot,pk,7,(V3){-1540,188,690},(V3){1540,188,690},(V3){1280,188,880},(V3){-1280,188,880},58,54,54,81,67,58);
    quad3g(ot,pk,7,(V3){-1280,188,885},(V3){1280,188,885},(V3){1070,188,1080},(V3){-1070,188,1080},81,67,58,108,84,63);
    quad3g(ot,pk,6,(V3){-455,184,695},(V3){455,184,695},(V3){350,184,1088},(V3){-350,184,1088},115,96,70,167,132,79);
}'''
src,n=pat.subn(replacement,src,count=1)
if n!=1: raise SystemExit('rev308 foreground replacement failed')
src=src.replace('foreground_frame(ot,pk,tick);','/* REV308 old foreground disabled */')
src=src.replace('tree(ot,pk,-1120,900);','/* REV308 near-left tree removed */')
src=src.replace('tree(ot,pk,1120,945);','/* REV308 near-right tree removed */')

# Build a deliberately layered authored view.  It uses only original MOKO
# geometry/content but follows the reference's scene grammar: lane -> props/NPC ->
# architecture -> skyline landmark.  This is integrated in the real Village draw.
anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if anchor not in src:
    raise SystemExit('rev308 playable-area anchor missing')
helper=r'''static void commercial_village_v18(uint32_t*ot,char**pk,int tick){
    int i,p=(tick/10)&3;
    /* raised lane edges make the traversal strip read immediately */
    box3(ot,pk,-515,176,1020,34,12,520,119,94,65);
    box3(ot,pk,481,176,1020,34,12,520,119,94,65);
    for(i=0;i<5;i++){
        int z=1060+i*105;
        box3(ot,pk,-492,158,z,20,30,24,89,68,55);
        box3(ot,pk,472,158,z,20,30,24,89,68,55);
        prism(ot,pk,-482,137-(i&1)*3,z,28,20,19,226,165,78);
        prism(ot,pk,482,137-((i+1)&1)*3,z,28,20,19,226,165,78);
    }
    /* close mid-ground shopfronts: large silhouettes, never near-plane clutter */
    awning(ot,pk,-760,1220,215,126,77,65);
    awning(ot,pk,545,1215,215,73,96,118);
    house(ot,pk,-1050,1395,285,245,117,92,77);
    house(ot,pk,735,1405,300,252,126,98,82);
    /* plaza geometry pulls the eye to the objective corridor */
    quad3g(ot,pk,6,(V3){-520,181,1180},(V3){520,181,1180},(V3){445,181,1480},(V3){-445,181,1480},112,92,72,145,117,82);
    for(i=0;i<4;i++){
        int x=-330+i*220;
        box3(ot,pk,x,175,1298+(i&1)*30,138,8,60,160,132,91);
    }
    /* original clock arch/tower become the dominant skyline landmark */
    arch(ot,pk,-155,1510,310);
    tower(ot,pk,74,1680);
    /* vegetation is kept in the mid/deep layer only */
    foliage(ot,pk,-650,1325,tick+9);
    foliage(ot,pk,640,1340,tick+17);
    foliage(ot,pk,-390,1500,tick+23);
    foliage(ot,pk,395,1518,tick+31);
    /* banners and hanging clocks add PS1-era readable colour blocks */
    for(i=0;i<3;i++){
        int x=-250+i*250;
        box3(ot,pk,x-3,71,1512,6,94,8,82,57,48);
        prism(ot,pk,x,82+p,1504,42,31,10,126+i*28,72,151-i*18);
        prism(ot,pk,x,123,1498,26,28,10,218,174,84);
    }
}'''
src=src.replace(anchor,helper+'\n'+anchor,1)
road_call='commercial_foreground_v13(ot,pk,tick);'
if road_call not in src:
    raise SystemExit('rev308 foreground call missing')
src=src.replace(road_call,road_call+'\n    commercial_village_v18(ot,pk,tick);',1)

# Moko: increase the hero's screen presence and round the feline silhouette with
# more exaggerated ears/paws.  The old mesh remains the topology source but is
# now deliberately proportioned for a commercial 320x240 gameplay frame.
src=src.replace('{-27,-72,2},{-43,-99,8},{-11,-83,4},{27,-72,2},{43,-99,8},{11,-83,4},',
                '{-30,-67,2},{-48,-101,8},{-12,-79,4},{30,-67,2},{48,-101,8},{12,-79,4},',1)
src=src.replace('{-29,24,-8},{-34,67,-5},{-7,72,3},{29,24,-8},{34,67,-5},{7,72,3},',
                '{-31,24,-8},{-38,70,-5},{-8,76,3},{31,24,-8},{38,70,-5},{8,76,3},',1)
scale_anchor='int vx=v.x,vy=v.y,vz=v.z;'
if scale_anchor not in src:
    raise SystemExit('rev308 mesh scale anchor missing')
src=src.replace(scale_anchor,scale_anchor+'vx=(vx*3)/2;vy=(vy*3)/2;vz=(vz*3)/2;',1)

# The V11 face details are replaced by larger high-contrast features.  They sit in
# front of the mesh so Moko reads as a cat instead of an abstract purple shape.
old='''tri3(ot,pk,1,(V3){x-13,gy+76-bob-jump,z-29},(V3){x-5,gy+76-bob-jump,z-30},(V3){x-9,gy+82-bob-jump,z-31},225,215,235);\n    tri3(ot,pk,1,(V3){x+5,gy+76-bob-jump,z-30},(V3){x+13,gy+76-bob-jump,z-29},(V3){x+9,gy+82-bob-jump,z-31},225,215,235);'''
new='''tri3(ot,pk,1,(V3){x-20,gy+66-bob-jump,z-43},(V3){x-5,gy+66-bob-jump,z-44},(V3){x-13,gy+79-bob-jump,z-45},244,238,248);\n    tri3(ot,pk,1,(V3){x+5,gy+66-bob-jump,z-44},(V3){x+20,gy+66-bob-jump,z-43},(V3){x+13,gy+79-bob-jump,z-45},244,238,248);\n    tri3(ot,pk,1,(V3){x-6,gy+82-bob-jump,z-47},(V3){x+6,gy+82-bob-jump,z-47},(V3){x,gy+91-bob-jump,z-49},232,105,145);\n    tri3(ot,pk,1,(V3){x-28,gy+84-bob-jump,z-40},(V3){x-8,gy+88-bob-jump,z-46},(V3){x-31,gy+94-bob-jump,z-39},185,117,205);\n    tri3(ot,pk,1,(V3){x+28,gy+84-bob-jump,z-40},(V3){x+8,gy+88-bob-jump,z-46},(V3){x+31,gy+94-bob-jump,z-39},185,117,205);'''
if old not in src:
    raise SystemExit('rev308 face anchor missing')
src=src.replace(old,new,1)

# Reference-style framing: larger hero in lower-middle, broad view of the lane,
# and less empty sky.  This is the first intentional camera rebuild after #449.
src=src.replace('gte_SetGeomOffset(160,148);gte_SetGeomScreen(260);','gte_SetGeomOffset(160,168);gte_SetGeomScreen(318);',1)
src=src.replace('t.vx=-cam_follow_x;t.vy=-30;t.vz=126-(cam_follow_z-1120)/22;',
                't.vx=-cam_follow_x;t.vy=-8;t.vz=178-(cam_follow_z-1120)/24;',1)

src+='\n/* REV308 STRUCTURAL REBUILD: TOMBI-STYLE SCENE GRAMMAR / LARGE HERO / DENSE MIDGROUND */\n'
pathlib.Path(sys.argv[2]).write_text(src)
