import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V14 REV 304 / VILLAGE 3D V13 REV 303',1)

# Runtime QA on run439 still showed two near-camera black wedges and too much dead
# lower-screen space. Remove the near-lantern foreground props entirely and replace
# them with broad, shallow road terraces that stay safely beyond the near plane.
pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}',re.S)
replacement=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){
    int p=(tick/16)&1;
    quad3g(ot,pk,7,(V3){-1300,188,520},(V3){1300,188,520},(V3){1120,188,760},(V3){-1120,188,760},77,66,56,96,79,62);
    quad3g(ot,pk,7,(V3){-1120,188,765},(V3){1120,188,765},(V3){980,188,1010},(V3){-980,188,1010},96,79,62,119,95,67);
    quad3g(ot,pk,6,(V3){-410,184,525},(V3){410,184,525},(V3){350,184,1015},(V3){-350,184,1015},132,108,74,159,128,80);
    box3(ot,pk,-448,178,610,24,9,310,134,106,71);
    box3(ot,pk,424,178,610,24,9,310,134,106,71);
    prism(ot,pk,-435,153-p,830,20,21,15,206,148,72);
    prism(ot,pk,435,153-p,830,20,21,15,206,148,72);
}'''
src,n=pat.subn(replacement,src,count=1)
if n!=1: raise SystemExit('rev304 foreground replacement failed')

# Bring Moko toward the on-screen scale used by commercial late-PS1 2.5D platformers:
# a readable mascot rather than a tiny scene marker. Shorten the ears, widen the feet,
# and scale the authored mesh coherently before projection.
src=src.replace('{-26,-82,2},{-44,-112,8},{-10,-91,4},{26,-82,2},{44,-112,8},{10,-91,4},',
                '{-27,-72,2},{-43,-99,8},{-11,-83,4},{27,-72,2},{43,-99,8},{11,-83,4},',1)
src=src.replace('{-24,24,-8},{-25,65,-5},{-8,68,3},{24,24,-8},{25,65,-5},{8,68,3},',
                '{-29,24,-8},{-34,67,-5},{-7,72,3},{29,24,-8},{34,67,-5},{7,72,3},',1)
anchor='int vx=v.x,vy=v.y,vz=v.z;'
if anchor not in src: raise SystemExit('rev304 mesh scale anchor missing')
src=src.replace(anchor,anchor+'vx=(vx*5)/4;vy=(vy*5)/4;vz=(vz*5)/4;',1)

# Refine facial readability at native 320x240: larger bright eyes and a small nose.
old='''tri3(ot,pk,1,(V3){x-13,gy+76-bob-jump,z-29},(V3){x-5,gy+76-bob-jump,z-30},(V3){x-9,gy+82-bob-jump,z-31},225,215,235);\n    tri3(ot,pk,1,(V3){x+5,gy+76-bob-jump,z-30},(V3){x+13,gy+76-bob-jump,z-29},(V3){x+9,gy+82-bob-jump,z-31},225,215,235);'''
new='''tri3(ot,pk,1,(V3){x-17,gy+70-bob-jump,z-37},(V3){x-5,gy+70-bob-jump,z-38},(V3){x-11,gy+80-bob-jump,z-39},238,231,245);\n    tri3(ot,pk,1,(V3){x+5,gy+70-bob-jump,z-38},(V3){x+17,gy+70-bob-jump,z-37},(V3){x+11,gy+80-bob-jump,z-39},238,231,245);\n    tri3(ot,pk,1,(V3){x-4,gy+84-bob-jump,z-40},(V3){x+4,gy+84-bob-jump,z-40},(V3){x,gy+90-bob-jump,z-41},229,111,151);'''
if old not in src: raise SystemExit('rev304 face anchor missing')
src=src.replace(old,new,1)

# Reframe after the run439 capture: slightly larger projection and lower optical centre
# so ground, Moko and architecture share the frame instead of leaving a dead lower third.
src=src.replace('gte_SetGeomOffset(160,148);gte_SetGeomScreen(260);','gte_SetGeomOffset(160,156);gte_SetGeomScreen(278);',1)
src=src.replace('t.vx=-cam_follow_x;t.vy=-30;t.vz=126-(cam_follow_z-1120)/22;',
                't.vx=-cam_follow_x;t.vy=-24;t.vz=142-(cam_follow_z-1120)/22;',1)

src+='\n/* REV304 TOMBI-BENCHMARKED RUNTIME PASS: READABLE MOKO / SAFE FOREGROUND / FULLER FRAME */\n'
pathlib.Path(sys.argv[2]).write_text(src)
