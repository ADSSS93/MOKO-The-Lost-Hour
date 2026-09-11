import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V20 REV 310 / VILLAGE 3D V13 REV 303',1)

# REV310 is a structural presentation reset.  The previous passes kept stacking
# foreground solids into the camera and scaling Moko up.  This pass instead
# authors a readable Tombi-style 2.5D lane: play space in the middle, scenery
# pushed to the sides/back, and a compact protagonist occupying a modest amount
# of the 320x240 frame.
road_pat=re.compile(r'static void road\(uint32_t\*ot,char\*\*pk\)\{.*?\}\nstatic void awning',re.S)
road_rep=r'''static void road(uint32_t*ot,char**pk){
    int i;
    /* broad ground field first, then a six-segment warm stone gameplay lane */
    quad3g(ot,pk,7,(V3){-1500,188,760},(V3){1500,188,760},(V3){1120,188,1900},(V3){-1120,188,1900},55,67,63,86,91,73);
    for(i=0;i<6;i++){
        int z0=820+i*165,z1=z0+168;
        int c0=(i<2?-42:(i<4?0:36)),c1=(i<1?-42:(i<3?-12:(i<5?24:46)));
        int w0=330-i*12,w1=322-i*12;
        quad3g(ot,pk,6,(V3){c0-w0,182,z0},(V3){c0+w0,182,z0},(V3){c1+w1,182,z1},(V3){c1-w1,182,z1},
               139+(i&1)*8,112+(i&1)*6,79,169+(i&1)*6,136+(i&1)*5,88);
    }
    /* darker verge gives the lane a strong silhouette without near-plane props */
    quad3g(ot,pk,6,(V3){-620,185,820},(V3){-345,185,820},(V3){-275,185,1810},(V3){-820,185,1810},65,73,60,82,88,66);
    quad3g(ot,pk,6,(V3){345,185,820},(V3){620,185,820},(V3){820,185,1810},(V3){275,185,1810},65,73,60,82,88,66);
}
static void awning'''
src,n=road_pat.subn(road_rep,src,count=1)
if n!=1: raise SystemExit('rev310 road replacement failed')

# Delete all near-camera foreground decoration.  Foreground needs to be supplied
# only by the ground plane until proper clipping is implemented.
pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\nstatic void playable_area_frame_v10',re.S)
replacement=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){(void)ot;(void)pk;(void)tick;}
static void playable_area_frame_v10'''
src,n=pat.subn(replacement,src,count=1)
if n!=1: raise SystemExit('rev310 foreground replacement failed')
src=src.replace('foreground_frame(ot,pk,tick);','/* REV310 old silhouette foreground disabled */')

# Replace the accumulated commercial-village helper with a deliberately staged
# street.  Buildings form left/right walls; the centre remains readable for
# Moko, the Clockmaker, Splinters, Boar and Dawn Gate.
anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if anchor not in src: raise SystemExit('rev310 playable-area anchor missing')
helper=r'''static void commercial_village_v20(uint32_t*ot,char**pk,int tick){
    int i,p=(tick/12)&3;
    /* near/mid left facade rhythm */
    house(ot,pk,-1180,1280,300,245,121,91,76);
    awning(ot,pk,-865,1260,210,138,82,62);
    house(ot,pk,-1120,1540,330,275,111,88,80);
    foliage(ot,pk,-720,1405,tick+7);
    lamp(ot,pk,-520,1320,tick);
    /* near/mid right facade rhythm */
    house(ot,pk,880,1295,305,250,126,96,80);
    awning(ot,pk,620,1268,210,78,105,125);
    house(ot,pk,820,1550,335,278,119,91,83);
    foliage(ot,pk,690,1430,tick+17);
    lamp(ot,pk,510,1340,tick+5);
    /* far focal point: arch + clock tower gives the lane a destination */
    arch(ot,pk,-145,1635,330);
    tower(ot,pk,88,1775);
    /* low market clutter only at the sides, never across the playable centre */
    for(i=0;i<3;i++){
        int z=1190+i*170;
        box3(ot,pk,-505,164,z,42,22,34,102,78,58);
        box3(ot,pk,463,164,z+35,42,22,34,104,79,59);
        prism(ot,pk,-484,145-p,z-4,26,19,20,220,158,75);
        prism(ot,pk,484,145-((p+1)&3),z+31,26,19,20,220,158,75);
    }
}'''
# Remove any previous helper(s) bearing this family of names, then insert one source of truth.
src=re.sub(r'static void commercial_village_v\d+\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}', '', src, flags=re.S)
src=src.replace(anchor,helper+'\n'+anchor,1)
# Strip old calls and install exactly one staging call after foreground.
src=re.sub(r'\n\s*commercial_village_v\d+\(ot,pk,tick\);','',src)
fg='commercial_foreground_v13(ot,pk,tick);'
if fg not in src: raise SystemExit('rev310 foreground call missing')
src=src.replace(fg,fg+'\n    commercial_village_v20(ot,pk,tick);',1)

# Moko: reverse the giant-character trend.  Keep the mesh but scale it to 78%,
# with a slightly wider head/paws so the feline silhouette survives PS1 resolution.
mesh_world_pat=re.compile(r'static V3 moko_mesh_world\(MokoMeshV v,int x,int y,int z,int facing,int step,int bob,int jump,int tick\)\{.*?\n\}',re.S)
mesh_world=r'''static V3 moko_mesh_world(MokoMeshV v,int x,int y,int z,int facing,int step,int bob,int jump,int tick){
    int vx=(v.x*4)/5,vy=(v.y*4)/5,vz=(v.z*4)/5;
    if(vy>16&&vx<0)vy+=(step*3)/4;if(vy>16&&vx>0)vy-=(step*3)/4;
    if(vx>36)vy+=((tick/5)&3)-1;
    if(!facing)vx=-vx;
    return (V3){x+vx,y+92+vy-bob-jump,z+vz};
}'''
src,n=mesh_world_pat.subn(mesh_world,src,count=1)
if n!=1: raise SystemExit('rev310 Moko mesh transform missing')
# Eyes/nose are redrawn closer to the scaled mesh.
src=re.sub(r'\n\s*tri3\(ot,pk,1,\(V3\)\{x-\d+,gy\+\d+-bob-jump,z-\d+\}.*?;\n\s*tri3\(ot,pk,1,\(V3\)\{x\+\d+,gy\+\d+-bob-jump,z-\d+\}.*?;',
           '\n    tri3(ot,pk,1,(V3){x-12,gy+65-bob-jump,z-31},(V3){x-4,gy+65-bob-jump,z-32},(V3){x-8,gy+72-bob-jump,z-33},242,237,248);\n    tri3(ot,pk,1,(V3){x+4,gy+65-bob-jump,z-32},(V3){x+12,gy+65-bob-jump,z-31},(V3){x+8,gy+72-bob-jump,z-33},242,237,248);\n    tri3(ot,pk,1,(V3){x-4,gy+75-bob-jump,z-35},(V3){x+4,gy+75-bob-jump,z-35},(V3){x,gy+81-bob-jump,z-37},231,102,145);',
           src,count=1,flags=re.S)

# Camera: wider and calmer, closer to the late-PS1 2.5D benchmark.  Keep Moko in
# the lower-middle rather than filling the vertical frame.
src=re.sub(r'gte_SetGeomOffset\(160,\d+\);gte_SetGeomScreen\(\d+\);','gte_SetGeomOffset(160,142);gte_SetGeomScreen(238);',src,count=1)
src=re.sub(r't\.vx=-cam_follow_x;t\.vy=-?\d+;t\.vz=\d+-\(cam_follow_z-1120\)/\d+;',
           't.vx=-cam_follow_x;t.vy=-58;t.vz=102-(cam_follow_z-1120)/20;',src,count=1)

src+='\n/* REV310 STRUCTURAL RESET: WIDE 2.5D LANE / SIDE SCENERY / COMPACT MOKO */\n'
pathlib.Path(sys.argv[2]).write_text(src)
