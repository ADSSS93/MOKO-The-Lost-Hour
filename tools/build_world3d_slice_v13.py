import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V20 REV 310' not in src:
    raise SystemExit('REV310 structural reset missing')
src=src.replace('VILLAGE 3D V20 REV 310','VILLAGE 3D V21 REV 311 / VILLAGE 3D V20 REV 310',1)

# The REV310 runtime still exposed classic PS1 near-plane wedges.  Never use one
# giant ground polygon here: tile the visible lane and verges into conservative
# quads whose projected vertices remain close to the 320x240 viewport.
pat=re.compile(r'static void road\(uint32_t\*ot,char\*\*pk\)\{.*?\}\nstatic void awning',re.S)
road=r'''static void road(uint32_t*ot,char**pk){
    int i;
    for(i=0;i<7;i++){
        int z0=900+i*135,z1=z0+138;
        int c0=-34+i*13,c1=-22+i*14;
        int w0=245-i*8,w1=239-i*8;
        quad3g(ot,pk,6,(V3){c0-w0,184,z0},(V3){c0+w0,184,z0},(V3){c1+w1,184,z1},(V3){c1-w1,184,z1},
               137+(i&1)*9,110+(i&1)*7,78,166+(i&1)*7,134+(i&1)*5,87);
        /* narrow grass/verge strips keep context without crossing the near plane */
        quad3g(ot,pk,7,(V3){c0-w0-145,186,z0},(V3){c0-w0-10,186,z0},(V3){c1-w1-10,186,z1},(V3){c1-w1-150,186,z1},
               61,75,62,78,91,67);
        quad3g(ot,pk,7,(V3){c0+w0+10,186,z0},(V3){c0+w0+145,186,z0},(V3){c1+w1+150,186,z1},(V3){c1+w1+10,186,z1},
               61,75,62,78,91,67);
    }
}
static void awning'''
src,n=pat.subn(road,src,count=1)
if n!=1: raise SystemExit('REV311 road replacement failed')

# Lower the optical centre without zooming the character back up.  The objective
# is a protagonist around the lower middle with enough ground visible to read
# movement/depth, similar to a commercial late-PS1 2.5D platformer framing.
src=re.sub(r'gte_SetGeomOffset\(160,\d+\);gte_SetGeomScreen\(\d+\);','gte_SetGeomOffset(160,174);gte_SetGeomScreen(238);',src,count=1)
src=re.sub(r't\.vx=-cam_follow_x;t\.vy=-?\d+;t\.vz=\d+-\(cam_follow_z-1120\)/\d+;',
           't.vx=-cam_follow_x;t.vy=-26;t.vz=112-(cam_follow_z-1120)/20;',src,count=1)

src+='\n/* REV311 PS1-SAFE LANE: SEGMENTED GROUND / NO GIANT NEAR-PLANE QUADS */\n'
pathlib.Path(sys.argv[2]).write_text(src)
