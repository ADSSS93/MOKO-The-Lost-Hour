import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V10 REV 299' not in src:
    raise SystemExit('Village v10 marker missing')
src=src.replace('VILLAGE 3D V10 REV 299','VILLAGE 3D V13 REV 303 / VILLAGE 3D V12 REV 301 / VILLAGE 3D V11 REV 300 / VILLAGE 3D V10 REV 299',1)

anchor='static int wz(int sy){return 1010+(190-sy)*7;}'
if anchor not in src: raise SystemExit('rev303 projection helper anchor missing')
helper='''\nstatic int projected_xy_sane(int32_t s){short x=(short)s,y=(short)(s>>16);return x>-320&&x<640&&y>-240&&y<480;}'''
src=src.replace(anchor,anchor+helper,1)
tri_old='if(!(flag&0x80000000)){setXY3(p,'
tri_new='if(!(flag&0x80000000)&&projected_xy_sane(s0)&&projected_xy_sane(s1)&&projected_xy_sane(s2)){setXY3(p,'
if tri_old not in src: raise SystemExit('rev303 triangle guard anchor missing')
src=src.replace(tri_old,tri_new)
quad_old='if(!(flag&0x80000000)){setXY4(p,'
quad_new='if(!(flag&0x80000000)&&projected_xy_sane(s0)&&projected_xy_sane(s1)&&projected_xy_sane(s2)&&projected_xy_sane(s3)){setXY4(p,'
if quad_old not in src: raise SystemExit('rev303 quad guard anchor missing')
src=src.replace(quad_old,quad_new)

src=src.replace('(V3){-1700,188,180},(V3){1700,188,180}','(V3){-1700,188,430},(V3){1700,188,430}',1)
src=src.replace('(V3){-1700,187,190},(V3){-470,187,190}','(V3){-1700,187,445},(V3){-470,187,445}',1)
src=src.replace('(V3){470,187,190},(V3){1700,187,190}','(V3){470,187,445},(V3){1700,187,445}',1)
src=src.replace('foreground_frame(ot,pk,tick);','/* REV303: failed silhouette foreground removed after runtime QA. */',1)

insert_anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if insert_anchor not in src: raise SystemExit('rev303 playable-area helper anchor missing')
foreground=r'''static void commercial_foreground_v13(uint32_t*ot,char**pk,int tick){
    int pulse=(tick/12)&1;
    quad3g(ot,pk,7,(V3){-1050,188,360},(V3){1050,188,360},(V3){930,188,540},(V3){-930,188,540},70,61,55,91,77,62);
    quad3g(ot,pk,7,(V3){-930,188,545},(V3){930,188,545},(V3){800,188,735},(V3){-800,188,735},91,77,62,112,91,66);
    quad3g(ot,pk,6,(V3){-360,184,365},(V3){360,184,365},(V3){300,184,760},(V3){-300,184,760},126,104,72,154,124,77);
    box3(ot,pk,-420,178,440,30,10,285,133,105,71);box3(ot,pk,390,178,440,30,10,285,133,105,71);
    box3(ot,pk,-475,150,555,18,36,20,77,65,58);box3(ot,pk,457,150,555,18,36,20,77,65,58);
    prism(ot,pk,-466,136-pulse*2,550,24,22,18,218,158,77);prism(ot,pk,466,136-pulse*2,550,24,22,18,218,158,77);
}
'''
src=src.replace(insert_anchor,foreground+insert_anchor,1)
road_call='road(ot,pk);'
if road_call not in src: raise SystemExit('rev303 road anchor missing')
src=src.replace(road_call,road_call+'\n    commercial_foreground_v13(ot,pk,tick);',1)

mesh_code=r'''typedef struct { signed char x,y,z; } MokoMeshV;
typedef struct { unsigned char a,b,c,shade; } MokoMeshF;
static const MokoMeshV moko_mesh_v[]={
 {0,-74,0},{-30,-46,-12},{30,-46,-12},{-34,-14,-15},{34,-14,-15},{-28,18,-10},{28,18,-10},{0,30,6},
 {-26,-82,2},{-44,-112,8},{-10,-91,4},{26,-82,2},{44,-112,8},{10,-91,4},
 {-24,24,-8},{-25,65,-5},{-8,68,3},{24,24,-8},{25,65,-5},{8,68,3},
 {0,-40,-24},{-11,-34,-29},{11,-34,-29},{0,-20,-31},
 {31,5,5},{54,2,12},{65,-9,16},{72,-25,18}
};
static const MokoMeshF moko_mesh_f[]={
 {0,1,2,2},{1,3,20,1},{1,20,0,2},{2,0,20,3},{2,20,4,2},{3,5,20,1},{4,20,6,2},{5,7,20,1},{6,20,7,2},
 {5,14,7,1},{6,7,17,2},{14,17,7,2},{14,15,16,1},{14,16,7,2},{17,7,19,2},{17,19,18,1},
 {0,8,10,2},{8,9,10,1},{0,10,1,2},{0,2,13,3},{11,0,13,2},{11,13,12,1},
 {20,21,22,3},{20,22,23,2},{21,23,22,1},
 {6,24,7,2},{24,25,7,2},{25,26,7,1},{26,27,7,2}
};
static V3 moko_mesh_world(MokoMeshV v,int x,int y,int z,int facing,int step,int bob,int jump,int tick){
    int vx=v.x,vy=v.y,vz=v.z;
    if(vy>20&&vx<0)vy+=step;if(vy>20&&vx>0)vy-=step;
    if(vx>45)vy+=((tick/5)&3)-1;
    if(!facing)vx=-vx;
    return (V3){x+vx,y+112+vy-bob-jump,z+vz};
}
static void moko_mesh_draw(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){
    int i,phase=(tick/4)&3,step=(phase==1?7:(phase==3?-7:0)),bob=(phase&1)*2;
    static const unsigned char col[4][3]={{77,35,124},{104,50,158},{137,72,184},{176,105,204}};
    shadow(ot,pk,x,z,34,jump);
    for(i=0;i<(int)(sizeof(moko_mesh_f)/sizeof(moko_mesh_f[0]));i++){
        MokoMeshF f=moko_mesh_f[i];int s=f.shade;
        V3 a=moko_mesh_world(moko_mesh_v[f.a],x,gy,z,facing,step,bob,jump,tick);
        V3 b=moko_mesh_world(moko_mesh_v[f.b],x,gy,z,facing,step,bob,jump,tick);
        V3 c=moko_mesh_world(moko_mesh_v[f.c],x,gy,z,facing,step,bob,jump,tick);
        tri3(ot,pk,2,a,b,c,col[s][0],col[s][1],col[s][2]);
    }
    tri3(ot,pk,1,(V3){x-13,gy+76-bob-jump,z-29},(V3){x-5,gy+76-bob-jump,z-30},(V3){x-9,gy+82-bob-jump,z-31},225,215,235);
    tri3(ot,pk,1,(V3){x+5,gy+76-bob-jump,z-30},(V3){x+13,gy+76-bob-jump,z-29},(V3){x+9,gy+82-bob-jump,z-31},225,215,235);
}
static void moko(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){moko_mesh_draw(ot,pk,x,gy,z,facing,tick,jump);}
'''
moko_pat=re.compile(r'static void moko\(uint32_t\*ot,char\*\*pk,int x,int gy,int z,int facing,int tick,int jump\)\{.*?\}\nstatic void camera_follow',re.S)
if not moko_pat.search(src): raise SystemExit('rev303 Moko renderer anchor missing')
src=moko_pat.sub(mesh_code+'\nstatic void camera_follow',src,count=1)
src=src.replace('moko(ot,pk,mx,-18,mz,facing,tick,player_jump);','moko_mesh_draw(ot,pk,mx,2,mz,facing,tick,player_jump);',1)
src=src.replace('moko(ot,pk,mx,0,mz,facing,tick,player_jump);','moko_mesh_draw(ot,pk,mx,2,mz,facing,tick,player_jump);',1)

src=src.replace('gte_SetGeomOffset(160,154);gte_SetGeomScreen(292);','gte_SetGeomOffset(160,148);gte_SetGeomScreen(260);',1)
src=src.replace('gte_SetGeomOffset(160,142);gte_SetGeomScreen(268);','gte_SetGeomOffset(160,148);gte_SetGeomScreen(260);',1)
src=src.replace('t.vx=-cam_follow_x;t.vy=-48;t.vz=78-(cam_follow_z-1120)/22;','t.vx=-cam_follow_x;t.vy=-30;t.vz=126-(cam_follow_z-1120)/22;',1)
src=src.replace('t.vx=-cam_follow_x;t.vy=-42;t.vz=108-(cam_follow_z-1120)/22;','t.vx=-cam_follow_x;t.vy=-30;t.vz=126-(cam_follow_z-1120)/22;',1)

src+='\n/* REV303 STRUCTURAL PRESENTATION PASS: ANIMATED LOW-POLY MOKO MESH */\n'
pathlib.Path(sys.argv[2]).write_text(src)
