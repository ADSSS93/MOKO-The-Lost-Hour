import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V20 REV 310' not in src:
    raise SystemExit('REV310 structural reset missing')
src=src.replace('VILLAGE 3D V20 REV 310','VILLAGE 3D V22 REV 312 / VILLAGE 3D V21 REV 311 / VILLAGE 3D V20 REV 310',1)

# The REV310 runtime still exposed classic PS1 near-plane wedges. Never use one
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
        quad3g(ot,pk,7,(V3){c0-w0-145,186,z0},(V3){c0-w0-10,186,z0},(V3){c1-w1-10,186,z1},(V3){c1-w1-150,186,z1},
               61,75,62,78,91,67);
        quad3g(ot,pk,7,(V3){c0+w0+10,186,z0},(V3){c0+w0+145,186,z0},(V3){c1+w1+150,186,z1},(V3){c1+w1+10,186,z1},
               61,75,62,78,91,67);
    }
}
static void awning'''
src,n=pat.subn(road,src,count=1)
if n!=1: raise SystemExit('REV312 road replacement failed')

# Runtime proof from run458: the remaining giant dark wedges line up with the
# four original tree() calls authored before the safe presentation passes. The
# two at z~900 are especially close to the camera. Remove all four; later
# foliage is already supplied deeper in the scene by commercial_village_v20.
for call in (
    'tree(ot,pk,-835,1190);',
    'tree(ot,pk,745,1170);',
    'tree(ot,pk,-1120,900);',
    'tree(ot,pk,1120,945);',
):
    src=src.replace(call,'/* REV312 near-camera tree removed */')

# Lower the optical centre without zooming the character back up.
src=re.sub(r'gte_SetGeomOffset\(160,\d+\);gte_SetGeomScreen\(\d+\);','gte_SetGeomOffset(160,174);gte_SetGeomScreen(238);',src,count=1)
src=re.sub(r't\.vx=-cam_follow_x;t\.vy=-?\d+;t\.vz=\d+-\(cam_follow_z-1120\)/\d+;',
           't.vx=-cam_follow_x;t.vy=-26;t.vz=112-(cam_follow_z-1120)/20;',src,count=1)

src+='\n/* REV312 RUNTIME FIX: SEGMENTED LANE / ORIGINAL NEAR TREES REMOVED */\n'
pathlib.Path(sys.argv[2]).write_text(src)
