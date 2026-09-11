import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V3 REV 291' not in src: raise SystemExit('Village v3 marker missing')
src=src.replace('VILLAGE 3D V3 REV 291','VILLAGE 3D V4 REV 292 / VILLAGE 3D V3 REV 291',1)
src=src.replace('VECTOR t={0,-70,110,0}','VECTOR t={0,-70,110}',1)

# Per-vertex colour is the cheapest PS1-era way to remove the flat tech-demo look
# without introducing borrowed textures/assets. Geometry remains true XYZ/GTE.
anchor='static void box3('
if anchor not in src: raise SystemExit('box3 anchor missing')
gouraud=r'''static void quad3g(uint32_t*ot,char**pk,int d,V3 a,V3 b,V3 c,V3 e,int r0,int g0,int b0,int r1,int g1,int b1){
    POLY_G4*p=(POLY_G4*)*pk;SVECTOR va={a.x,a.y,a.z,0},vb={b.x,b.y,b.z,0},vc={c.x,c.y,c.z,0},ve={e.x,e.y,e.z,0};int32_t s0,s1,s2,s3,flag;
    setPolyG4(p);setRGB0(p,r0,g0,b0);setRGB1(p,r0,g0,b0);setRGB2(p,r1,g1,b1);setRGB3(p,r1,g1,b1);
    gte_ldv3(&va,&vb,&vc);gte_rtpt();gte_stsxy0(&s0);gte_stsxy1(&s1);gte_stsxy2(&s2);gte_ldv0(&ve);gte_rtps();gte_stsxy(&s3);gte_stflg(&flag);
    if(!(flag&0x80000000)){setXY4(p,(short)s0,(short)(s0>>16),(short)s1,(short)(s1>>16),(short)s2,(short)(s2>>16),(short)s3,(short)(s3>>16));addPrim(ot+d,p);*pk+=sizeof(POLY_G4);}
}
static int absi(int v){return v<0?-v:v;}static int clampi(int v,int lo,int hi){return v<lo?lo:(v>hi?hi:v);}
static int moko_prev_x=0,moko_prev_z=0,moko_motion_seeded=0,moko_prev_jump=0,moko_land_squash=0;
static int cam_pitch_v4=188,cam_yaw_v4=0;
'''
src=src.replace(anchor,gouraud+anchor,1)

# Replace Moko animation so idle is actually idle, movement drives gait/lean, and landing
# has a tiny squash. This is runtime motion inferred from real world-space displacement.
pat=re.compile(r'static void moko\(uint32_t\*ot,char\*\*pk,int x,int gy,int z,int facing,int tick,int jump\)\{.*?\}\nstatic void camera_follow',re.S)
rep=r'''static void moko(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){
    int dx=0,dz=0,moving,phase,step,bob,ear,tail,y,lean,squash,dir=facing?1:-1;
    if(!moko_motion_seeded){moko_prev_x=x;moko_prev_z=z;moko_motion_seeded=1;}
    dx=x-moko_prev_x;dz=z-moko_prev_z;moving=(absi(dx)+absi(dz))>2;
    if(moko_prev_jump>0&&jump==0)moko_land_squash=5;if(moko_land_squash>0)moko_land_squash--;
    phase=moving?((tick/4)&3):0;step=moving?(phase==1?11:(phase==3?-11:0)):0;
    bob=moving?((phase&1)*3):((tick/28)&1);ear=moving?((tick/15)&1)*3:0;tail=((tick/(moving?5:11))&3)-1;
    lean=clampi(dx/2,-8,8);squash=moko_land_squash?5:0;y=gy-jump+squash;
    shadow(ot,pk,x,z,37,jump);
    /* compact pear-shaped feline body; retained as the v3 regression contract */
    prism(ot,pk,x+lean,y+72-bob,z+4,68+squash,76-squash,58,98,49,149);
    box3(ot,pk,x-29+lean,y+91-bob,z-1,58,48-squash,54,112,58,164);
    prism(ot,pk,x+lean/2,y+27-bob,z-2,84,63,58,143,77,187);
    box3(ot,pk,x-25+lean/2,y+49-bob,z-17,50,19,22,211,180,199);
    prism(ot,pk,x-25+lean/2,y-11-bob-ear,z+5,39,52,28,109,44,151);prism(ot,pk,x+25+lean/2,y-11-bob+ear,z+5,39,52,28,109,44,151);
    box3(ot,pk,x-23+lean/2,y+34-bob,z-25,12,8,9,231,224,235);box3(ot,pk,x+11+lean/2,y+34-bob,z-25,12,8,9,231,224,235);
    box3(ot,pk,x-19+lean/2,y+36-bob,z-30,5,6,6,36,29,45);box3(ot,pk,x+14+lean/2,y+36-bob,z-30,5,6,6,36,29,45);prism(ot,pk,x+lean/2,y+52-bob,z-31,11,10,7,232,105,142);
    prism(ot,pk,x+lean,y+105-bob,z-18,36,38,16,207,166,74);prism(ot,pk,x+lean,y+112-bob,z-23,21,22,10,242,224,157);
    box3(ot,pk,x-2+lean,y+114-bob,z-27,4,14,5,34,28,39);box3(ot,pk,x+lean,y+122-bob,z-27,12,4,5,34,28,39);
    box3(ot,pk,x-23-step,y+137-bob,z+1,18,35,34,69,34,109);box3(ot,pk,x+5+step,y+137-bob,z+1,18,35,34,69,34,109);
    prism(ot,pk,x-15-step,y+169-bob,z-7,31,19,40,52,28,82);prism(ot,pk,x+15+step,y+169-bob,z-7,31,19,40,52,28,82);
    if(dir>0){box3(ot,pk,x+27,y+111-bob,z+18,38+tail*4,8,10,207,59,135);prism(ot,pk,x+67+tail*4,y+72-bob-tail*4,z+18,15,53+tail*3,12,225,157,78);}
    else{box3(ot,pk,x-65-tail*4,y+111-bob,z+18,38+tail*4,8,10,207,59,135);prism(ot,pk,x-70-tail*4,y+72-bob-tail*4,z+18,15,53+tail*3,12,225,157,78);}
    moko_prev_x=x;moko_prev_z=z;moko_prev_jump=jump;
}
static void camera_follow'''
src,n=pat.subn(rep,src,count=1)
if n!=1: raise SystemExit('v4 Moko replacement failed')

# Add gentle authored pitch/yaw changes to the existing camera zones. No cuts.
old='cam_follow_x+=(tx-cam_follow_x)/9;cam_follow_z+=(tz-cam_follow_z)/11;\n}'
new='''cam_follow_x+=(tx-cam_follow_x)/9;cam_follow_z+=(tz-cam_follow_z)/11;
    {int target_pitch=188,target_yaw=0;if(px<82)target_pitch=176;else if(px>176&&px<226){target_pitch=194;target_yaw=facing?10:-10;}else if(px>=226&&px<286)target_pitch=202;else if(px>=286){target_pitch=181;target_yaw=-8;}cam_pitch_v4+=(target_pitch-cam_pitch_v4)/12;cam_yaw_v4+=(target_yaw-cam_yaw_v4)/14;}
}'''
if old not in src: raise SystemExit('v4 camera anchor missing')
src=src.replace(old,new,1)

# Camera rotation and dawn/ground colour gradients are applied in the actual village draw.
old='if(!ready)world3d_init();camera_follow(px,py,facing);\n    t.vx=-cam_follow_x;t.vy=-82;t.vz=132-(cam_follow_z-1120)/19;TransMatrix(&cam,&t);gte_SetRotMatrix(&cam);gte_SetTransMatrix(&cam);\n    road(ot,pk);'
new='''if(!ready)world3d_init();camera_follow(px,py,facing);
    {SVECTOR vr={cam_pitch_v4,cam_yaw_v4,0,0};RotMatrix(&vr,&cam);}
    t.vx=-cam_follow_x;t.vy=-82;t.vz=132-(cam_follow_z-1120)/19;TransMatrix(&cam,&t);gte_SetRotMatrix(&cam);gte_SetTransMatrix(&cam);
    road(ot,pk);
    quad3g(ot,pk,6,(V3){-420,180,760},(V3){420,180,760},(V3){350,180,1120},(V3){-350,180,1120},118,101,77,151,119,77);
    quad3g(ot,pk,6,(V3){-350,180,1122},(V3){350,180,1122},(V3){430,180,1510},(V3){-430,180,1510},151,119,77,102,91,79);'''
if old not in src: raise SystemExit('v4 draw camera anchor missing')
src=src.replace(old,new,1)
old_h='quad3(ot,pk,7,(V3){-1450,-460,1870},(V3){1450,-460,1870},(V3){1450,188,1870},(V3){-1450,188,1870},64,78,98);'
new_h='quad3g(ot,pk,7,(V3){-1450,-460,1870},(V3){1450,-460,1870},(V3){1450,188,1870},(V3){-1450,188,1870},47,60,91,154,103,91);'
if old_h not in src: raise SystemExit('v4 horizon anchor missing')
src=src.replace(old_h,new_h,1)
pathlib.Path(sys.argv[2]).write_text(src)
