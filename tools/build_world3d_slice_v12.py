import pathlib,re,sys

src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V24 REV 314 / VILLAGE 3D V13 REV 303',1)

# Model-first pass: parse the authored OBJ asset at build time and embed it into
# the PS1 renderer. This mirrors the asset-driven workflow used by real PS1
# projects without copying any external game assets.
obj_path=pathlib.Path(__file__).resolve().parent.parent/'assets'/'models'/'moko_lowpoly.obj'
verts=[];faces=[]
for raw in obj_path.read_text().splitlines():
    line=raw.strip()
    if not line or line.startswith('#'): continue
    parts=line.split()
    if parts[0]=='v' and len(parts)>=4:
        verts.append(tuple(int(round(float(v))) for v in parts[1:4]))
    elif parts[0]=='f' and len(parts)>=4:
        ids=[int(tok.split('/')[0])-1 for tok in parts[1:]]
        for i in range(1,len(ids)-1): faces.append((ids[0],ids[i],ids[i+1]))
if not verts or not faces or len(verts)>255:
    raise SystemExit('invalid Moko OBJ')

# Remove tall legacy tree() calls which can cross the near plane and create
# catastrophic PS1 wedges.
src=re.sub(r'\s*tree\(ot,pk,-?\d+,\d+\);','',src)
src=src.replace('foreground_frame(ot,pk,tick);','/* REV314 legacy foreground disabled */')

# Safe continuous gameplay ground + six readable lane segments.
road_pat=re.compile(r'static void road\(uint32_t\*ot,char\*\*pk\)\{.*?\}\nstatic void awning',re.S)
road_rep=r'''static void road(uint32_t*ot,char**pk){
    int i;
    quad3g(ot,pk,7,(V3){-1450,188,760},(V3){1450,188,760},(V3){1080,188,1900},(V3){-1080,188,1900},58,67,63,91,91,72);
    for(i=0;i<6;i++){
        int z0=820+i*165,z1=z0+168,c0=(i<2?-34:(i<4?0:30)),c1=(i<2?-22:(i<4?14:42));
        int w0=315-i*10,w1=307-i*10;
        quad3g(ot,pk,6,(V3){c0-w0,182,z0},(V3){c0+w0,182,z0},(V3){c1+w1,182,z1},(V3){c1-w1,182,z1},142+(i&1)*7,114+(i&1)*6,79,172+(i&1)*5,137+(i&1)*4,88);
    }
    quad3g(ot,pk,6,(V3){-640,185,820},(V3){-335,185,820},(V3){-265,185,1810},(V3){-800,185,1810},65,76,61,82,91,66);
    quad3g(ot,pk,6,(V3){335,185,820},(V3){640,185,820},(V3){800,185,1810},(V3){265,185,1810},65,76,61,82,91,66);
}
static void awning'''
src,n=road_pat.subn(road_rep,src,count=1)
if n!=1: raise SystemExit('REV314 road replacement failed')

pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\nstatic void playable_area_frame_v10',re.S)
src,n=pat.subn('static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){(void)ot;(void)pk;(void)tick;}\nstatic void playable_area_frame_v10',src,count=1)
if n!=1: raise SystemExit('REV314 foreground replacement failed')

# Stage architecture as side walls and a far landmark, preserving the centre as
# gameplay space instead of stacking props in front of the camera.
anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if anchor not in src: raise SystemExit('REV314 playable-area anchor missing')
helper=r'''static void commercial_village_v24(uint32_t*ot,char**pk,int tick){
    int p=(tick/12)&3;
    house(ot,pk,-1210,1260,305,245,119,91,76); awning(ot,pk,-880,1270,205,136,82,62);
    house(ot,pk,-1160,1540,340,275,108,86,80); lamp(ot,pk,-520,1340,tick);
    house(ot,pk,905,1280,310,248,124,96,80); awning(ot,pk,645,1280,205,78,105,124);
    house(ot,pk,840,1550,340,278,116,90,82); lamp(ot,pk,515,1360,tick+5);
    foliage(ot,pk,-735,1430,tick+7); foliage(ot,pk,710,1440,tick+17);
    arch(ot,pk,-150,1650,330); tower(ot,pk,92,1790);
    box3(ot,pk,-505,164,1260,42,22,34,102,78,58); prism(ot,pk,-484,145-p,1256,26,19,20,220,158,75);
    box3(ot,pk,463,164,1310,42,22,34,104,79,59); prism(ot,pk,484,145-((p+1)&3),1306,26,19,20,220,158,75);
}'''
src=re.sub(r'static void commercial_village_v\d+\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}', '', src, flags=re.S)
src=src.replace(anchor,helper+'\n'+anchor,1)
src=re.sub(r'\n\s*commercial_village_v\d+\(ot,pk,tick\);','',src)
fg='commercial_foreground_v13(ot,pk,tick);'
if fg not in src: raise SystemExit('REV314 foreground call missing')
src=src.replace(fg,fg+'\n    commercial_village_v24(ot,pk,tick);',1)

# Wider, calmer 2.5D camera: Moko should read as a character in a world, not fill
# the frame like a debug model.
src=re.sub(r'gte_SetGeomOffset\(160,\d+\);gte_SetGeomScreen\(\d+\);','gte_SetGeomOffset(160,140);gte_SetGeomScreen(228);',src,count=1)
src=re.sub(r't\.vx=-cam_follow_x;t\.vy=-?\d+;t\.vz=\d+-\(cam_follow_z-1120\)/\d+;', 't.vx=-cam_follow_x;t.vy=-62;t.vz=94-(cam_follow_z-1120)/20;',src,count=1)

# Generate compact C mesh tables from OBJ. Face colour bands provide readable
# PS1 facets while preserving one authored mesh source of truth.
vtxt=',\n      '.join('{%d,%d,%d}'%v for v in verts)
ftxt=',\n      '.join('{%d,%d,%d}'%f for f in faces)
moko_pat=re.compile(r'static void moko_mesh_draw\(uint32_t\*ot,char\*\*pk,int x,int gy,int z,int facing,int tick,int jump\)\{.*?\}\nstatic void moko',re.S)
moko_rep='''static void moko_mesh_draw(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){\n    static const V3 mv[]={\n      %s\n    };\n    static const unsigned char mf[][3]={\n      %s\n    };\n    int i,phase=(tick/5)&3,step=(phase==1?5:(phase==3?-5:0)),bob=(phase&1)*2,sy=gy-jump,sx=facing?1:-1;\n    shadow(ot,pk,x,z,29,jump);\n    for(i=0;i<(int)(sizeof(mf)/sizeof(mf[0]));i++){\n      V3 a=mv[mf[i][0]],b=mv[mf[i][1]],c=mv[mf[i][2]]; int r=107,g=55,bl=154;\n      if(i>=8&&i<17){r=151;g=82;bl=194;} else if(i>=17&&i<19){r=111;g=45;bl=153;} else if(i>=19&&i<23){r=65;g=32;bl=98;} else if(i>=23&&i<26){r=220;g=182;bl=205;} else if(i>=26){r=211;g=72;bl=139;}\n      if(a.y>138)a.x+=(a.x<0?-step:step);if(b.y>138)b.x+=(b.x<0?-step:step);if(c.y>138)c.x+=(c.x<0?-step:step);\n      a.x=x+sx*a.x;a.y=sy+a.y-bob;a.z=z+a.z;b.x=x+sx*b.x;b.y=sy+b.y-bob;b.z=z+b.z;c.x=x+sx*c.x;c.y=sy+c.y-bob;c.z=z+c.z;\n      tri3(ot,pk,2,a,b,c,r,g,bl);\n    }\n    /* face details + brass clock hands remain gameplay-readable at 320x240 */\n    tri3(ot,pk,1,(V3){x-10*sx,sy+49-bob,z-36},(V3){x-4*sx,sy+49-bob,z-37},(V3){x-7*sx,sy+55-bob,z-38},248,244,250);\n    tri3(ot,pk,1,(V3){x+4*sx,sy+49-bob,z-37},(V3){x+10*sx,sy+49-bob,z-36},(V3){x+7*sx,sy+55-bob,z-38},248,244,250);\n    tri3(ot,pk,1,(V3){x-4*sx,sy+63-bob,z-41},(V3){x+4*sx,sy+63-bob,z-41},(V3){x,sy+69-bob,z-43},232,103,147);\n    prism(ot,pk,x,sy+111-bob,z-25,26,27,10,217,172,76);\n    box3(ot,pk,x-2,sy+108-bob,z-31,4,18,5,43,34,39);\n    box3(ot,pk,x,sy+119-bob,z-31,13,4,5,43,34,39);\n}\nstatic void moko'''%(vtxt,ftxt)
src,n=moko_pat.subn(moko_rep,src,count=1)
if n!=1: raise SystemExit('REV314 mesh renderer anchor missing')

src+='\n/* REV314 ASSET PIPELINE: MOKO OBJ -> PS1 TRIANGLES / SAFE CAMERA / STAGED VILLAGE */\n'
pathlib.Path(sys.argv[2]).write_text(src)
