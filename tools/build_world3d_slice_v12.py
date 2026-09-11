import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V17 REV 307 / VILLAGE 3D V16 REV 306 / VILLAGE 3D V15 REV 305 / VILLAGE 3D V14 REV 304 / VILLAGE 3D V13 REV 303',1)

# Runtime QA showed that any small near-camera box/prism can still explode into
# dark wedges on PS1 projection. Keep foreground strictly as wide ground quads.
pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}',re.S)
replacement=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){
    (void)tick;
    quad3g(ot,pk,7,(V3){-1500,188,610},(V3){1500,188,610},(V3){1260,188,800},(V3){-1260,188,800},73,64,57,90,75,61);
    quad3g(ot,pk,7,(V3){-1260,188,805},(V3){1260,188,805},(V3){1040,188,1010},(V3){-1040,188,1010},90,75,61,111,88,65);
    quad3g(ot,pk,6,(V3){-430,184,615},(V3){430,184,615},(V3){350,184,1015},(V3){-350,184,1015},126,103,73,159,128,80);
}'''
src,n=pat.subn(replacement,src,count=1)
if n!=1: raise SystemExit('rev307 foreground replacement failed')
src=src.replace('foreground_frame(ot,pk,tick);','/* REV307 old foreground disabled */')
# The original V3 staging included two near-side trees at z~900. Runtime proved
# their triangular crowns were the dark corner wedges, so keep only deeper trees.
src=src.replace('tree(ot,pk,-1120,900);','/* REV307 near-left tree removed */')
src=src.replace('tree(ot,pk,1120,945);','/* REV307 near-right tree removed */')

# Bring Moko toward a commercial late-PS1 2.5D on-screen scale and preserve a
# friendly cat-like silhouette instead of the earlier tall horned/primitive read.
src=src.replace('{-26,-82,2},{-44,-112,8},{-10,-91,4},{26,-82,2},{44,-112,8},{10,-91,4},',
                '{-27,-72,2},{-43,-99,8},{-11,-83,4},{27,-72,2},{43,-99,8},{11,-83,4},',1)
src=src.replace('{-24,24,-8},{-25,65,-5},{-8,68,3},{24,24,-8},{25,65,-5},{8,68,3},',
                '{-29,24,-8},{-34,67,-5},{-7,72,3},{29,24,-8},{34,67,-5},{7,72,3},',1)
anchor='int vx=v.x,vy=v.y,vz=v.z;'
if anchor not in src: raise SystemExit('rev307 mesh scale anchor missing')
src=src.replace(anchor,anchor+'vx=(vx*5)/4;vy=(vy*5)/4;vz=(vz*5)/4;',1)

old='''tri3(ot,pk,1,(V3){x-13,gy+76-bob-jump,z-29},(V3){x-5,gy+76-bob-jump,z-30},(V3){x-9,gy+82-bob-jump,z-31},225,215,235);\n    tri3(ot,pk,1,(V3){x+5,gy+76-bob-jump,z-30},(V3){x+13,gy+76-bob-jump,z-29},(V3){x+9,gy+82-bob-jump,z-31},225,215,235);'''
new='''tri3(ot,pk,1,(V3){x-17,gy+70-bob-jump,z-37},(V3){x-5,gy+70-bob-jump,z-38},(V3){x-11,gy+80-bob-jump,z-39},238,231,245);\n    tri3(ot,pk,1,(V3){x+5,gy+70-bob-jump,z-38},(V3){x+17,gy+70-bob-jump,z-37},(V3){x+11,gy+80-bob-jump,z-39},238,231,245);\n    tri3(ot,pk,1,(V3){x-4,gy+84-bob-jump,z-40},(V3){x+4,gy+84-bob-jump,z-40},(V3){x,gy+90-bob-jump,z-41},229,111,151);'''
if old not in src: raise SystemExit('rev307 face anchor missing')
src=src.replace(old,new,1)

src=src.replace('gte_SetGeomOffset(160,148);gte_SetGeomScreen(260);','gte_SetGeomOffset(160,174);gte_SetGeomScreen(286);',1)
src=src.replace('t.vx=-cam_follow_x;t.vy=-30;t.vz=126-(cam_follow_z-1120)/22;',
                't.vx=-cam_follow_x;t.vy=-18;t.vz=148-(cam_follow_z-1120)/22;',1)

src+='\n/* REV307 TOMBI-BENCHMARKED RUNTIME PASS: SIDE WEDGES REMOVED / CLEANER PLAYFIELD */\n'
pathlib.Path(sys.argv[2]).write_text(src)
