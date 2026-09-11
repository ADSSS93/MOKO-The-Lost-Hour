import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V13 REV 303' not in src:
    raise SystemExit('Village v13 marker missing')
src=src.replace('VILLAGE 3D V13 REV 303','VILLAGE 3D V19 REV 309 / VILLAGE 3D V18 REV 308 / VILLAGE 3D V17 REV 307 / VILLAGE 3D V16 REV 306 / VILLAGE 3D V15 REV 305 / VILLAGE 3D V14 REV 304 / VILLAGE 3D V13 REV 303',1)

road_pat=re.compile(r'static void road\(uint32_t\*ot,char\*\*pk\)\{.*?\}\nstatic void awning',re.S)
road_rep=r'''static void road(uint32_t*ot,char**pk){
    int i;
    quad3g(ot,pk,7,(V3){-1500,188,760},(V3){1500,188,760},(V3){1320,188,1040},(V3){-1320,188,1040},55,53,55,80,67,58);
    quad3g(ot,pk,7,(V3){-1320,188,1044},(V3){1320,188,1044},(V3){1040,188,1510},(V3){-1040,188,1510},80,67,58,109,87,64);
    quad3g(ot,pk,7,(V3){-1040,188,1514},(V3){1040,188,1514},(V3){900,188,1890},(V3){-900,188,1890},109,87,64,125,99,70);
    for(i=0;i<6;i++){
        int z0=850+i*155,z1=z0+118,shift=(i-2)*15;
        quad3g(ot,pk,6,(V3){-390+shift,183,z0},(V3){390+shift,183,z0},(V3){350+shift,183,z1},(V3){-350+shift,183,z1},115+(i&1)*10,92+(i&1)*8,67,147+(i&1)*8,116+(i&1)*6,75);
    }
}
static void awning'''
src,n=road_pat.subn(road_rep,src,count=1)
if n!=1: raise SystemExit('rev309 safe road replacement failed')

# Match whole function through the next known function declaration; do not parse
# braces because V3 compound literals contain many braces themselves.
pat=re.compile(r'static void commercial_foreground_v13\(uint32_t\*ot,char\*\*pk,int tick\)\{.*?\nstatic void playable_area_frame_v10',re.S)
replacement=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){
    (void)tick;
    quad3g(ot,pk,7,(V3){-1480,188,770},(V3){1480,188,770},(V3){1220,188,960},(V3){-1220,188,960},57,54,55,82,68,59);
    quad3g(ot,pk,6,(V3){-440,184,775},(V3){440,184,775},(V3){355,184,1115},(V3){-355,184,1115},119,98,70,162,129,79);
}
static void playable_area_frame_v10'''
src,n=pat.subn(replacement,src,count=1)
if n!=1: raise SystemExit('rev309 foreground replacement failed')
src=src.replace('foreground_frame(ot,pk,tick);','/* REV309 old foreground disabled */')
src=src.replace('tree(ot,pk,-1120,900);','/* REV309 near-left tree removed */')
src=src.replace('tree(ot,pk,1120,945);','/* REV309 near-right tree removed */')

anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if anchor not in src: raise SystemExit('rev309 playable-area anchor missing')
helper=r'''static void commercial_village_v19(uint32_t*ot,char**pk,int tick){
    int i,p=(tick/10)&3;
    for(i=0;i<4;i++){
        int z=1160+i*120;
        box3(ot,pk,-492,158,z,18,30,22,89,68,55);
        box3(ot,pk,474,158,z,18,30,22,89,68,55);
        prism(ot,pk,-483,136-(i&1)*3,z,25,20,18,226,165,78);
        prism(ot,pk,483,136-((i+1)&1)*3,z,25,20,18,226,165,78);
    }
    awning(ot,pk,-760,1260,215,126,77,65);
    awning(ot,pk,545,1255,215,73,96,118);
    house(ot,pk,-1050,1430,285,245,117,92,77);
    house(ot,pk,735,1440,300,252,126,98,82);
    quad3g(ot,pk,6,(V3){-510,181,1210},(V3){510,181,1210},(V3){440,181,1515},(V3){-440,181,1515},112,92,72,145,117,82);
    for(i=0;i<4;i++){int x=-330+i*220;box3(ot,pk,x,175,1335+(i&1)*30,138,8,60,160,132,91);}
    arch(ot,pk,-155,1545,310);tower(ot,pk,74,1710);
    foliage(ot,pk,-650,1360,tick+9);foliage(ot,pk,640,1375,tick+17);
    foliage(ot,pk,-390,1535,tick+23);foliage(ot,pk,395,1553,tick+31);
    for(i=0;i<3;i++){
        int x=-250+i*250;
        box3(ot,pk,x-3,71,1545,6,94,8,82,57,48);
        prism(ot,pk,x,82+p,1537,42,31,10,126+i*28,72,151-i*18);
        prism(ot,pk,x,123,1531,26,28,10,218,174,84);
    }
}'''
src=src.replace(anchor,helper+'\n'+anchor,1)
road_call='commercial_foreground_v13(ot,pk,tick);'
if road_call not in src: raise SystemExit('rev309 foreground call missing')
src=src.replace(road_call,road_call+'\n    commercial_village_v19(ot,pk,tick);',1)

src=src.replace('{-27,-72,2},{-43,-99,8},{-11,-83,4},{27,-72,2},{43,-99,8},{11,-83,4},',
                '{-24,-67,2},{-32,-86,6},{-10,-75,4},{24,-67,2},{32,-86,6},{10,-75,4},',1)
src=src.replace('{-29,24,-8},{-34,67,-5},{-7,72,3},{29,24,-8},{34,67,-5},{7,72,3},',
                '{-28,24,-8},{-31,63,-5},{-7,69,3},{28,24,-8},{31,63,-5},{7,69,3},',1)
scale_anchor='int vx=v.x,vy=v.y,vz=v.z;'
if scale_anchor not in src: raise SystemExit('rev309 mesh scale anchor missing')
src=src.replace(scale_anchor,scale_anchor+'vx=(vx*5)/4;vy=(vy*5)/4;vz=(vz*5)/4;',1)

old='''tri3(ot,pk,1,(V3){x-13,gy+76-bob-jump,z-29},(V3){x-5,gy+76-bob-jump,z-30},(V3){x-9,gy+82-bob-jump,z-31},225,215,235);\n    tri3(ot,pk,1,(V3){x+5,gy+76-bob-jump,z-30},(V3){x+13,gy+76-bob-jump,z-29},(V3){x+9,gy+82-bob-jump,z-31},225,215,235);'''
new='''tri3(ot,pk,1,(V3){x-16,gy+69-bob-jump,z-38},(V3){x-5,gy+69-bob-jump,z-39},(V3){x-11,gy+78-bob-jump,z-40},244,238,248);\n    tri3(ot,pk,1,(V3){x+5,gy+69-bob-jump,z-39},(V3){x+16,gy+69-bob-jump,z-38},(V3){x+11,gy+78-bob-jump,z-40},244,238,248);\n    tri3(ot,pk,1,(V3){x-5,gy+81-bob-jump,z-42},(V3){x+5,gy+81-bob-jump,z-42},(V3){x,gy+88-bob-jump,z-44},232,105,145);'''
if old not in src: raise SystemExit('rev309 face anchor missing')
src=src.replace(old,new,1)

src=src.replace('gte_SetGeomOffset(160,148);gte_SetGeomScreen(260);','gte_SetGeomOffset(160,162);gte_SetGeomScreen(282);',1)
src=src.replace('t.vx=-cam_follow_x;t.vy=-30;t.vz=126-(cam_follow_z-1120)/22;',
                't.vx=-cam_follow_x;t.vy=-16;t.vz=150-(cam_follow_z-1120)/23;',1)

src+='\n/* REV309 RUNTIME FIX: SAFE FLAT ROAD / COMPACT CAT SILHOUETTE / MODERATE CAMERA */\n'
pathlib.Path(sys.argv[2]).write_text(src)
