import pathlib,re,sys,subprocess
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V4 REV 292' not in src: raise SystemExit('Village v4 marker missing')
src=src.replace('VILLAGE 3D V4 REV 292','VILLAGE 3D V5 REV 293 / VILLAGE 3D V4 REV 292',1)

# Runtime presentation state: spring camera, boss hit reaction and authored gate reveal.
anchor='static int cam_pitch_v4=188,cam_yaw_v4=0;'
if anchor not in src: raise SystemExit('v4 camera state anchor missing')
state='''static int cam_vel_x_v5=0,cam_vel_z_v5=0,cam_target_x_v5=0,cam_target_z_v5=0;\nstatic int boar_prev_hp_v5=-1,boar_hit_v5=0,gate_open_v5=0,gate_clear_prev_v5=0;\n'''
src=src.replace(anchor,anchor+'\n'+state,1)

pat=re.compile(r'static void camera_follow\(int px,int py,int facing\)\{.*?\n\}',re.S)
rep=r'''static void camera_follow(int px,int py,int facing){
    int desired_x=wx(px)+(facing?76:-76),desired_z=wz(py),dx,dz;
    if(px<90){desired_x=(desired_x*3+wx(116))/4;desired_z=(desired_z*3+1320)/4;}
    else if(px>176&&px<226){desired_x=(desired_x*3+wx(205))/4;desired_z=(desired_z*3+1260)/4;}
    else if(px>=226&&px<286){desired_z-=34;}
    else if(px>=286){desired_x=(desired_x*3+wx(296))/4;desired_z=(desired_z*3+1215)/4;}
    if(!cam_seeded){cam_follow_x=desired_x;cam_follow_z=desired_z;cam_target_x_v5=desired_x;cam_target_z_v5=desired_z;cam_seeded=1;}
    dx=desired_x-cam_target_x_v5;dz=desired_z-cam_target_z_v5;
    if(absi(dx)>12)cam_target_x_v5+=dx/3;if(absi(dz)>10)cam_target_z_v5+=dz/3;
    cam_vel_x_v5+=(cam_target_x_v5-cam_follow_x)/14;cam_vel_z_v5+=(cam_target_z_v5-cam_follow_z)/16;
    cam_vel_x_v5=(cam_vel_x_v5*11)/14;cam_vel_z_v5=(cam_vel_z_v5*12)/15;
    cam_follow_x+=cam_vel_x_v5;cam_follow_z+=cam_vel_z_v5;
    {int target_pitch=188,target_yaw=0;if(px<90)target_pitch=178;else if(px>176&&px<226){target_pitch=193;target_yaw=facing?7:-7;}else if(px>=226&&px<286)target_pitch=199;else if(px>=286){target_pitch=182;target_yaw=-6;}cam_pitch_v4+=(target_pitch-cam_pitch_v4)/14;cam_yaw_v4+=(target_yaw-cam_yaw_v4)/16;}
}'''
src,n=pat.subn(rep,src,count=1)
if n!=1: raise SystemExit('v5 camera replacement failed')

pat=re.compile(r'static void boar\(uint32_t\*ot,char\*\*pk,int x,int z,int hp,int tick\)\{.*?\}\nstatic void splinter',re.S)
rep=r'''static void boar(uint32_t*ot,char**pk,int x,int z,int hp,int tick){
    int gait=(tick/5)&3,bob=(gait&1)*4,lean=(gait==1?7:(gait==3?-7:0)),recoil=0;
    if(hp<=0)return;
    if(boar_prev_hp_v5<0)boar_prev_hp_v5=hp;
    if(hp<boar_prev_hp_v5){boar_hit_v5=11;boar_prev_hp_v5=hp;}
    if(boar_hit_v5>0){recoil=(boar_hit_v5*3);boar_hit_v5--;bob+=2;}
    shadow(ot,pk,x+recoil,z,45,0);
    prism(ot,pk,x+recoil+lean,104-bob,z+6,96,63,72,80,38,101);
    box3(ot,pk,x-42+recoil+lean,119-bob,z-5,84,42,65,92,43,111);
    prism(ot,pk,x-31+recoil+lean,73-bob,z-9,39,43,32,143,61,143);
    prism(ot,pk,x+31+recoil+lean,73-bob,z-9,39,43,32,143,61,143);
    prism(ot,pk,x+recoil+lean,103-bob,z-35,57,39,34,111,48,121);
    box3(ot,pk,x-25+recoil+lean,113-bob,z-41,11,8,8,239,204,87);box3(ot,pk,x+14+recoil+lean,113-bob,z-41,11,8,8,239,204,87);
    prism(ot,pk,x-38+recoil-lean/2,157-bob,z+3,27,31,42,48,28,66);prism(ot,pk,x+38+recoil+lean/2,157-bob,z+3,27,31,42,48,28,66);
}
static void splinter'''
src,n=pat.subn(rep,src,count=1)
if n!=1: raise SystemExit('v5 boar replacement failed')

pat=re.compile(r'static void gate\(uint32_t\*ot,char\*\*pk,int clear,int tick\)\{.*?\}\nstatic void moko',re.S)
rep=r'''static void gate(uint32_t*ot,char**pk,int clear,int tick){
    int glow=clear?18+((tick/6)&3)*10:0,open=gate_open_v5;
    if(clear&&!gate_clear_prev_v5)gate_open_v5=1;gate_clear_prev_v5=clear;
    if(clear&&gate_open_v5<76)gate_open_v5+=2;open=gate_open_v5;
    box3(ot,pk,770,-10,1360,35,196,45,74,60,67);box3(ot,pk,1000,-10,1360,35,196,45,74,60,67);box3(ot,pk,770,-16,1360,265,35,45,88,70,72);
    prism(ot,pk,902,-72,1366,105,72,30,112+glow,77+glow/2,118+glow);
    box3(ot,pk,806-open,42,1347,93,144,22,76,54,78);box3(ot,pk,906+open,42,1347,93,144,22,76,54,78);
    if(clear){tri3(ot,pk,1,(V3){875,36,1338},(V3){902,-18,1338},(V3){929,36,1338},108,223,205);}
}
static void moko'''
src,n=pat.subn(rep,src,count=1)
if n!=1: raise SystemExit('v5 gate replacement failed')

needle='''box3(ot,pk,x-23-step,y+137-bob,z+1,18,35,34,69,34,109);box3(ot,pk,x+5+step,y+137-bob,z+1,18,35,34,69,34,109);\n    prism(ot,pk,x-15-step,y+169-bob,z-7,31,19,40,52,28,82);prism(ot,pk,x+15+step,y+169-bob,z-7,31,19,40,52,28,82);'''
replace='''box3(ot,pk,x-23-step,y+137-bob,z+1,18,35,34,69,34,109);box3(ot,pk,x+5+step,y+137-bob,z+1,18,35,34,69,34,109);\n    prism(ot,pk,x-15-step,y+169-bob,z-7,31,19,40,52,28,82);prism(ot,pk,x+15+step,y+169-bob,z-7,31,19,40,52,28,82);\n    /* forepaws counter-swing and read clearly during run cycles */\n    prism(ot,pk,x-29+step/2+lean,y+108-bob,z-13,18,38,25,91,44,137);prism(ot,pk,x+29-step/2+lean,y+108-bob,z-13,18,38,25,91,44,137);\n    prism(ot,pk,x-30+step/2+lean,y+141-bob,z-21,24,14,31,58,31,89);prism(ot,pk,x+30-step/2+lean,y+141-bob,z-21,24,14,31,58,31,89);'''
if needle not in src: raise SystemExit('v5 Moko limb anchor missing')
src=src.replace(needle,replace,1)

anchor='static void mission_beacon('
if anchor not in src: raise SystemExit('v5 beacon anchor missing')
helper=r'''static void foreground_frame(uint32_t*ot,char**pk,int tick){
    int sway=((tick/17)&3)-1;
    box3(ot,pk,-1290,38,720,74,148,90,74,55,39);prism(ot,pk,-1250+sway*4,-58,735,230,176,118,44,94,65);
    box3(ot,pk,1210,52,790,82,134,96,81,59,42);prism(ot,pk,1247-sway*4,-46,805,220,164,112,51,104,70);
    prism(ot,pk,-1040,128,930,54,46,56,109,93,72);prism(ot,pk,1050,126,970,58,49,58,116,96,72);
}
'''
src=src.replace(anchor,helper+anchor,1)
old='''road(ot,pk);\n    quad3g(ot,pk,6,'''
new='''road(ot,pk);\n    foreground_frame(ot,pk,tick);\n    quad3g(ot,pk,6,'''
if old not in src: raise SystemExit('v5 village draw anchor missing')
src=src.replace(old,new,1)

out=pathlib.Path(sys.argv[2]);out.write_text(src)
subprocess.check_call([sys.executable,str(pathlib.Path(__file__).with_name('build_world3d_slice_v6.py')),str(out),str(out)])
