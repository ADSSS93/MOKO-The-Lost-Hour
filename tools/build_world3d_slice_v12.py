import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V21 REV 311 / VILLAGE 3D V20 REV 310 / VILLAGE 3D V13 REV 303',1)

# REV311 follows real PCSX-Redux QA of run 455.  The structural reset made the
# Village readable, but two legacy REV297 side-fill quads and old tree calls were
# still capable of crossing the near plane and appearing as giant dark wedges.
# Remove those leftovers before authoring the new staging pass.
src=src.replace('quad3g(ot,pk,7,(V3){-1700,187,445},(V3){-470,187,445},(V3){-520,187,1250},(V3){-1550,187,1510},44,70,57,70,91,67);','/* REV311 legacy left near-plane fill removed */')
src=src.replace('quad3g(ot,pk,7,(V3){470,187,445},(V3){1700,187,445},(V3){1550,187,1510},(V3){520,187,1250},45,72,58,72,94,69);','/* REV311 legacy right near-plane fill removed */')
# Compatibility with builds where REV297 coordinates were not yet moved by REV303.
src=src.replace('quad3g(ot,pk,7,(V3){-1700,187,190},(V3){-470,187,190},(V3){-520,187,1250},(V3){-1550,187,1510},44,70,57,70,91,67);','/* REV311 legacy left near-plane fill removed */')
src=src.replace('quad3g(ot,pk,7,(V3){470,187,190},(V3){1700,187,190},(V3){1550,187,1510},(V3){520,187,1250},45,72,58,72,94,69);','/* REV311 legacy right near-plane fill removed */')
# The original procedural trees use very tall triangular crowns.  Until proper
# near-plane clipping exists, the authored REV311 foliage replaces them.
src=re.sub(r'\s*tree\(ot,pk,-?\d+,\d+\);','',src)

road_pat=re.compile(r'static void road\(uint32_t\*ot,char\*\*pk\)\{.*?\}\nstatic void awning',re.S)
road_rep=r'''static void road(uint32_t*ot,char**pk){
    int i;
    quad3g(ot,pk,7,(V3){-1500,188,760},(V3){1500,188,760},(V3){1120,188,1900},(V3){-1120,188,1900},55,67,63,86,91,73);
    for(i=0;i<6;i++){
        int z0=820+i*165,z1=z0+168;
        int c0=(i<2?-42:(i<4?0:36)),c1=(i<1?-42:(i<3?-12:(i<5?24:46)));
        int w0=330-i*12,w1=322-i*12;
        quad3g(ot,pk,6,(V3){c0-w0,182,z0},(V3){c0+w0,182,z0},(V3){c1+w1,182,z1},(V3){c1-w1,182,z1},
               139+(i&1)*8,112+(i&1)*6,79,169+(i&1)*6,136+(i&1)*5,88);
    }
    /* narrow grass shoulders: all vertices stay well behind the near plane */
    quad3g(ot,pk,6,(V3){-560,185,900},(V3){-350,185,900},(V3){-280,185,1810},(V3){-720,185,1810},65,73,60,82,88,66);
    quad3g(ot,pk,6,(V3){350,185,900},(V3){560,185,900},(V3){720,185,1810},(V3){280,185,1810},65,73,60,82,88,66);
}
static void awning'''
src,n=road_pat.subn(road_rep,src,count=1)
if n!=1: raise SystemExit('rev311 road replacement failed')

pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\nstatic void playable_area_frame_v10',re.S)
replacement=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){(void)ot;(void)pk;(void)tick;}
static void playable_area_frame_v10'''
src,n=pat.subn(replacement,src,count=1)
if n!=1: raise SystemExit('rev311 foreground replacement failed')
src=src.replace('foreground_frame(ot,pk,tick);','/* REV311 old silhouette foreground disabled */')

anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if anchor not in src: raise SystemExit('rev311 playable-area anchor missing')
helper=r'''static void commercial_village_v21(uint32_t*ot,char**pk,int tick){
    int i,p=(tick/12)&3;
    /* Deep side walls: deliberately outside the centre gameplay lane. */
    house(ot,pk,-1320,1450,300,245,121,91,76);
    awning(ot,pk,-930,1370,205,138,82,62);
    house(ot,pk,-1230,1690,330,275,111,88,80);
    foliage(ot,pk,-760,1510,tick+7);
    lamp(ot,pk,-545,1425,tick);
    house(ot,pk,1020,1460,305,250,126,96,80);
    awning(ot,pk,690,1380,205,78,105,125);
    house(ot,pk,930,1700,335,278,119,91,83);
    foliage(ot,pk,750,1535,tick+17);
    lamp(ot,pk,545,1440,tick+5);
    /* Strong destination silhouette, but kept behind the mission actors. */
    arch(ot,pk,-145,1665,330);
    tower(ot,pk,88,1830);
    for(i=0;i<3;i++){
        int z=1280+i*165;
        box3(ot,pk,-525,164,z,42,22,34,102,78,58);
        box3(ot,pk,483,164,z+35,42,22,34,104,79,59);
        prism(ot,pk,-504,145-p,z-4,26,19,20,220,158,75);
        prism(ot,pk,504,145-((p+1)&3),z+31,26,19,20,220,158,75);
    }
}'''
src=re.sub(r'static void commercial_village_v\d+\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}', '', src, flags=re.S)
src=src.replace(anchor,helper+'\n'+anchor,1)
src=re.sub(r'\n\s*commercial_village_v\d+\(ot,pk,tick\);','',src)
fg='commercial_foreground_v13(ot,pk,tick);'
if fg not in src: raise SystemExit('rev311 foreground call missing')
src=src.replace(fg,fg+'\n    commercial_village_v21(ot,pk,tick);',1)

# Keep Moko compact: roughly one sixth of the vertical gameplay frame.
mesh_world_pat=re.compile(r'static V3 moko_mesh_world\(MokoMeshV v,int x,int y,int z,int facing,int step,int bob,int jump,int tick\)\{.*?\n\}',re.S)
mesh_world=r'''static V3 moko_mesh_world(MokoMeshV v,int x,int y,int z,int facing,int step,int bob,int jump,int tick){
    int vx=(v.x*4)/5,vy=(v.y*4)/5,vz=(v.z*4)/5;
    if(vy>16&&vx<0)vy+=(step*3)/4;if(vy>16&&vx>0)vy-=(step*3)/4;
    if(vx>36)vy+=((tick/5)&3)-1;
    if(!facing)vx=-vx;
    return (V3){x+vx,y+92+vy-bob-jump,z+vz};
}'''
src,n=mesh_world_pat.subn(mesh_world,src,count=1)
if n!=1: raise SystemExit('rev311 Moko mesh transform missing')

# A wider lens and lower horizon keep the play lane visible while retaining depth.
src=re.sub(r'gte_SetGeomOffset\(160,\d+\);gte_SetGeomScreen\(\d+\);','gte_SetGeomOffset(160,146);gte_SetGeomScreen(232);',src,count=1)
src=re.sub(r't\.vx=-cam_follow_x;t\.vy=-?\d+;t\.vz=\d+-\(cam_follow_z-1120\)/\d+;',
           't.vx=-cam_follow_x;t.vy=-54;t.vz=108-(cam_follow_z-1120)/20;',src,count=1)

src+='\n/* REV311 RUNTIME QA: LEGACY WEDGES REMOVED / DEEPER STAGING / SAFE SHOULDERS */\n'
pathlib.Path(sys.argv[2]).write_text(src)
