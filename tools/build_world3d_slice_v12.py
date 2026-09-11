import pathlib,re,sys

src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V25 REV 315 / VILLAGE 3D V24 REV 314 / VILLAGE 3D V13 REV 303',1)

root=pathlib.Path(__file__).resolve().parent.parent

def parse_obj(path):
    verts=[];faces=[]
    for raw in path.read_text().splitlines():
        line=raw.strip()
        if not line or line.startswith('#'): continue
        parts=line.split()
        if parts[0]=='v' and len(parts)>=4:
            verts.append(tuple(int(round(float(v))) for v in parts[1:4]))
        elif parts[0]=='f' and len(parts)>=4:
            ids=[int(tok.split('/')[0])-1 for tok in parts[1:]]
            for i in range(1,len(ids)-1): faces.append((ids[0],ids[i],ids[i+1]))
    if not verts or not faces or len(verts)>255:
        raise SystemExit('invalid OBJ: '+str(path))
    return verts,faces

verts,faces=parse_obj(root/'assets'/'models'/'moko_lowpoly.obj')
world_verts,world_faces=parse_obj(root/'assets'/'models'/'village_dawn_slice.obj')

# Remove legacy near-camera silhouettes that produced catastrophic PS1 wedges.
src=re.sub(r'\s*tree\(ot,pk,-?\d+,\d+\);','',src)
src=src.replace('foreground_frame(ot,pk,tick);','/* REV315 legacy foreground disabled */')

# The authored Village OBJ owns the visible lane now; keep the old road hook as a no-op.
road_pat=re.compile(r'static void road\(uint32_t\*ot,char\*\*pk\)\{.*?\}\nstatic void awning',re.S)
src,n=road_pat.subn('static void road(uint32_t*ot,char**pk){(void)ot;(void)pk;}\nstatic void awning',src,count=1)
if n!=1: raise SystemExit('REV315 road replacement failed')

pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\nstatic void playable_area_frame_v10',re.S)
src,n=pat.subn('static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){(void)ot;(void)pk;(void)tick;}\nstatic void playable_area_frame_v10',src,count=1)
if n!=1: raise SystemExit('REV315 foreground replacement failed')

# Build Village renderer directly from the authored environment OBJ.
wvtxt=',\n      '.join('{%d,%d,%d}'%v for v in world_verts)
wftxt=',\n      '.join('{%d,%d,%d}'%f for f in world_faces)
anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if anchor not in src: raise SystemExit('REV315 playable-area anchor missing')
helper='''static void commercial_village_v25(uint32_t*ot,char**pk,int tick){\n    static const V3 vv[]={\n      %s\n    };\n    static const unsigned char vf[][3]={\n      %s\n    };\n    int i;(void)tick;\n    for(i=0;i<(int)(sizeof(vf)/sizeof(vf[0]));i++){\n      V3 a=vv[vf[i][0]],b=vv[vf[i][1]],c=vv[vf[i][2]]; int r=126,g=93,bl=77,otz=6;\n      if(i<6){r=158;g=126;bl=82;otz=7;}\n      else if(i<18){r=132;g=96;bl=79;}\n      else if(i<22){r=110;g=65;bl=91;}\n      else if(i<34){r=125;g=96;bl=82;}\n      else if(i<38){r=76;g=102;bl=123;}\n      else if(i<48){r=116;g=88;bl=80;}\n      else if(i<58){r=121;g=91;bl=81;}\n      else if(i<64){r=150;g=119;bl=82;}\n      else if(i<72){r=112;g=87;bl=78;}\n      else {r=95;g=61;bl=88;}\n      tri3(ot,pk,otz,a,b,c,r,g,bl);\n    }\n}\n'''%(wvtxt,wftxt)
src=re.sub(r'static void commercial_village_v\d+\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}', '', src, flags=re.S)
src=src.replace(anchor,helper+anchor,1)
src=re.sub(r'\n\s*commercial_village_v\d+\(ot,pk,tick\);','',src)
fg='commercial_foreground_v13(ot,pk,tick);'
if fg not in src: raise SystemExit('REV315 foreground call missing')
src=src.replace(fg,fg+'\n    commercial_village_v25(ot,pk,tick);',1)

# Tombi-style benchmark target: player occupies a small fraction of frame and the
# lane converges toward a strong landmark instead of filling the viewport.
src=re.sub(r'gte_SetGeomOffset\(160,\d+\);gte_SetGeomScreen\(\d+\);','gte_SetGeomOffset(160,138);gte_SetGeomScreen(214);',src,count=1)
src=re.sub(r't\.vx=-cam_follow_x;t\.vy=-?\d+;t\.vz=\d+-\(cam_follow_z-1120\)/\d+;', 't.vx=-cam_follow_x;t.vy=-72;t.vz=76-(cam_follow_z-1120)/20;',src,count=1)

# Build Moko directly from the authored OBJ.
vtxt=',\n      '.join('{%d,%d,%d}'%v for v in verts)
ftxt=',\n      '.join('{%d,%d,%d}'%f for f in faces)
moko_pat=re.compile(r'static void moko_mesh_draw\(uint32_t\*ot,char\*\*pk,int x,int gy,int z,int facing,int tick,int jump\)\{.*?\}\nstatic void moko',re.S)
moko_rep='''static void moko_mesh_draw(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){\n    static const V3 mv[]={\n      %s\n    };\n    static const unsigned char mf[][3]={\n      %s\n    };\n    int i,phase=(tick/5)&3,step=(phase==1?5:(phase==3?-5:0)),bob=(phase&1)*2,sy=gy-jump,sx=facing?1:-1;\n    shadow(ot,pk,x,z,27,jump);\n    for(i=0;i<(int)(sizeof(mf)/sizeof(mf[0]));i++){\n      V3 a=mv[mf[i][0]],b=mv[mf[i][1]],c=mv[mf[i][2]]; int r=111,g=57,bl=159;\n      if(i>=10&&i<21){r=149;g=82;bl=194;}\n      else if(i>=21&&i<23){r=100;g=47;bl=145;}\n      else if(i>=23&&i<31){r=76;g=38;bl=111;}\n      else if(i>=31&&i<35){r=209;g=174;bl=75;}\n      else if(i>=35&&i<39){r=127;g=61;bl=173;}\n      else if(i>=39){r=171;g=76;bl=181;}\n      if(a.y>138)a.x+=(a.x<0?-step:step);if(b.y>138)b.x+=(b.x<0?-step:step);if(c.y>138)c.x+=(c.x<0?-step:step);\n      a.x=x+sx*a.x;a.y=sy+a.y-bob;a.z=z+a.z;b.x=x+sx*b.x;b.y=sy+b.y-bob;b.z=z+b.z;c.x=x+sx*c.x;c.y=sy+c.y-bob;c.z=z+c.z;\n      tri3(ot,pk,2,a,b,c,r,g,bl);\n    }\n    tri3(ot,pk,1,(V3){x-10*sx,sy+49-bob,z-42},(V3){x-4*sx,sy+49-bob,z-43},(V3){x-7*sx,sy+55-bob,z-44},248,244,250);\n    tri3(ot,pk,1,(V3){x+4*sx,sy+49-bob,z-43},(V3){x+10*sx,sy+49-bob,z-42},(V3){x+7*sx,sy+55-bob,z-44},248,244,250);\n    tri3(ot,pk,1,(V3){x-4*sx,sy+64-bob,z-46},(V3){x+4*sx,sy+64-bob,z-46},(V3){x,sy+70-bob,z-48},232,103,147);\n    prism(ot,pk,x,sy+108-bob,z-34,25,27,8,217,172,76);\n}\nstatic void moko'''%(vtxt,ftxt)
src,n=moko_pat.subn(moko_rep,src,count=1)
if n!=1: raise SystemExit('REV315 Moko mesh renderer anchor missing')

src+='\n/* REV315 WORLD-ASSET PASS: MOKO OBJ + VILLAGE OBJ -> PS1 TRIANGLES */\n'
pathlib.Path(sys.argv[2]).write_text(src)
