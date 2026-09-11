import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V23 REV 313 / VILLAGE 3D V22 REV 312 / VILLAGE 3D V20 REV 310 / VILLAGE 3D V13 REV 303',1)

# REV313 keeps the stable REV312 staging but makes the protagonist a real
# authored triangle mesh instead of a stack of runtime boxes.  This follows the
# model-first pipeline demonstrated by the open PS1 graphics demo referenced by
# the user while keeping all MOKO geometry original.
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
    quad3g(ot,pk,6,(V3){-620,185,820},(V3){-345,185,820},(V3){-275,185,1810},(V3){-820,185,1810},65,73,60,82,88,66);
    quad3g(ot,pk,6,(V3){345,185,820},(V3){620,185,820},(V3){820,185,1810},(V3){275,185,1810},65,73,60,82,88,66);
}
static void awning'''
src,n=road_pat.subn(road_rep,src,count=1)
if n!=1: raise SystemExit('rev313 road replacement failed')

pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\nstatic void playable_area_frame_v10',re.S)
replacement=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){(void)ot;(void)pk;(void)tick;}
static void playable_area_frame_v10'''
src,n=pat.subn(replacement,src,count=1)
if n!=1: raise SystemExit('rev313 foreground replacement failed')
src=src.replace('foreground_frame(ot,pk,tick);','/* REV313 old silhouette foreground disabled */')

anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if anchor not in src: raise SystemExit('rev313 playable-area anchor missing')
helper=r'''static void commercial_village_v23(uint32_t*ot,char**pk,int tick){
    int i,p=(tick/12)&3;
    house(ot,pk,-1180,1280,300,245,121,91,76);
    awning(ot,pk,-865,1260,210,138,82,62);
    house(ot,pk,-1120,1540,330,275,111,88,80);
    foliage(ot,pk,-720,1405,tick+7);
    lamp(ot,pk,-520,1320,tick);
    house(ot,pk,880,1295,305,250,126,96,80);
    awning(ot,pk,620,1268,210,78,105,125);
    house(ot,pk,820,1550,335,278,119,91,83);
    foliage(ot,pk,690,1430,tick+17);
    lamp(ot,pk,510,1340,tick+5);
    arch(ot,pk,-145,1635,330);
    tower(ot,pk,88,1775);
    for(i=0;i<3;i++){
        int z=1190+i*170;
        box3(ot,pk,-505,164,z,42,22,34,102,78,58);
        box3(ot,pk,463,164,z+35,42,22,34,104,79,59);
        prism(ot,pk,-484,145-p,z-4,26,19,20,220,158,75);
        prism(ot,pk,484,145-((p+1)&3),z+31,26,19,20,220,158,75);
    }
}'''
src=re.sub(r'static void commercial_village_v\d+\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\n\}', '', src, flags=re.S)
src=src.replace(anchor,helper+'\n'+anchor,1)
src=re.sub(r'\n\s*commercial_village_v\d+\(ot,pk,tick\);','',src)
fg='commercial_foreground_v13(ot,pk,tick);'
if fg not in src: raise SystemExit('rev313 foreground call missing')
src=src.replace(fg,fg+'\n    commercial_village_v23(ot,pk,tick);',1)

src=re.sub(r'gte_SetGeomOffset\(160,\d+\);gte_SetGeomScreen\(\d+\);','gte_SetGeomOffset(160,142);gte_SetGeomScreen(238);',src,count=1)
src=re.sub(r't\.vx=-cam_follow_x;t\.vy=-?\d+;t\.vz=\d+-\(cam_follow_z-1120\)/\d+;',
           't.vx=-cam_follow_x;t.vy=-58;t.vz=102-(cam_follow_z-1120)/20;',src,count=1)

moko_pat=re.compile(r'static void moko\(uint32_t\*ot,char\*\*pk,int x,int gy,int z,int facing,int tick,int jump\)\{.*?\n\}\nstatic void camera_follow',re.S)
moko_rep=r'''static void moko(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){
    static const V3 mv[]={
      {-28,72,18},{28,72,18},{-38,118,14},{38,118,14},{-28,151,18},{28,151,18},{0,92,-24},{0,139,-20},
      {-39,27,12},{39,27,12},{-43,64,9},{43,64,9},{-25,80,7},{25,80,7},{0,25,-25},{0,70,-33},
      {-34,28,9},{-18,-8,13},{-5,29,7},{5,29,7},{18,-8,13},{34,28,9},
      {-30,150,12},{-42,178,-5},{-4,176,-9},{30,150,12},{42,178,-5},{4,176,-9},
      {-17,58,-31},{17,58,-31},{0,76,-39},{-19,95,-25},{19,95,-25},{18,124,-24},{-18,124,-24},
      {30,112,18},{55,104,16},{72,86,13},{82,62,10}
    };
    static const unsigned char mf[][6]={
      {0,1,6,107,55,154},{0,6,2,98,47,146},{1,3,6,122,63,169},{2,6,7,92,43,137},{3,7,6,108,51,153},{2,7,4,78,37,121},{3,5,7,91,42,133},{4,7,5,70,33,108},
      {8,14,10,151,83,194},{10,14,15,137,70,182},{10,15,12,129,63,175},{9,11,14,159,89,201},{11,15,14,144,76,188},{11,13,15,136,69,180},{8,9,14,171,98,211},{9,15,14,162,91,204},{12,15,13,119,57,164},
      {16,17,18,113,45,153},{19,20,21,113,45,153},{22,23,24,62,31,94},{22,24,4,70,35,105},{25,26,27,62,31,94},{25,5,27,70,35,105},
      {28,29,30,233,225,241},{31,32,33,209,170,76},{31,33,34,198,155,65},{35,36,37,212,61,139},{35,37,38,221,75,145}
    };
    int i,phase=(tick/5)&3,step=(phase==1?6:(phase==3?-6:0)),bob=(phase&1)*2,sy=gy-jump,sx=facing?1:-1;
    shadow(ot,pk,x,z,31,jump);
    for(i=0;i<(int)(sizeof(mf)/sizeof(mf[0]));i++){
      V3 a=mv[mf[i][0]],b=mv[mf[i][1]],c=mv[mf[i][2]];
      if(a.y>138)a.x+=(a.x<0?-step:step);if(b.y>138)b.x+=(b.x<0?-step:step);if(c.y>138)c.x+=(c.x<0?-step:step);
      a.x=x+sx*a.x;a.y=sy+a.y-bob;a.z=z+a.z;b.x=x+sx*b.x;b.y=sy+b.y-bob;b.z=z+b.z;c.x=x+sx*c.x;c.y=sy+c.y-bob;c.z=z+c.z;
      tri3(ot,pk,2,a,b,c,mf[i][3],mf[i][4],mf[i][5]);
    }
    tri3(ot,pk,1,(V3){x-11*sx,sy+49-bob,z-36},(V3){x-4*sx,sy+49-bob,z-37},(V3){x-8*sx,sy+55-bob,z-38},248,244,250);
    tri3(ot,pk,1,(V3){x+4*sx,sy+49-bob,z-37},(V3){x+11*sx,sy+49-bob,z-36},(V3){x+8*sx,sy+55-bob,z-38},248,244,250);
    tri3(ot,pk,1,(V3){x-4*sx,sy+63-bob,z-41},(V3){x+4*sx,sy+63-bob,z-41},(V3){x,sy+69-bob,z-43},232,103,147);
}
static void camera_follow'''
src,n=moko_pat.subn(moko_rep,src,count=1)
if n!=1: raise SystemExit('rev313 triangulated Moko replacement failed')

src+='\n/* REV313 MODEL-FIRST PASS: TRIANGULATED MOKO / STABLE VILLAGE FRAMING */\n'
pathlib.Path(sys.argv[2]).write_text(src)
