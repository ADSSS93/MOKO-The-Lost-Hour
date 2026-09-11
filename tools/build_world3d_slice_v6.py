import pathlib,re,sys,subprocess
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V5 REV 293' not in src: raise SystemExit('Village v5 marker missing')
src=src.replace('VILLAGE 3D V5 REV 293','VILLAGE 3D V6 REV 294 / VILLAGE 3D V5 REV 293',1)

# Locomotion presentation state. Everything below is driven by the real world-space Moko transform.
anchor='static int boar_prev_hp_v5=-1,boar_hit_v5=0,gate_open_v5=0,gate_clear_prev_v5=0;'
if anchor not in src: raise SystemExit('v6 state anchor missing')
state='''\nstatic int moko_cycle_v6=0,moko_speed_v6=0,moko_lean_v6=0,moko_land_fx_v6=0,moko_prev_jump_v6=0;\nstatic int villager_greet_v6=0;'''
src=src.replace(anchor,anchor+state,1)

pat=re.compile(r'static void moko\(uint32_t\*ot,char\*\*pk,int x,int gy,int z,int facing,int tick,int jump\)\{.*?\}\nstatic void camera_follow',re.S)
rep=r'''static void moko(uint32_t*ot,char**pk,int x,int gy,int z,int facing,int tick,int jump){
    static int lx=0,lz=0,seed=0;int dx,dz,target_speed,phase,step,bob,ear,tail,y,dir=facing?1:-1,blink,plant;
    if(!seed){lx=x;lz=z;seed=1;}
    dx=x-lx;dz=z-lz;target_speed=clampi((absi(dx)+absi(dz))*5,0,32);
    moko_speed_v6+=(target_speed-moko_speed_v6)/4;
    moko_lean_v6+=(clampi(dx*3,-12,12)-moko_lean_v6)/4;
    if(moko_speed_v6>3)moko_cycle_v6=(moko_cycle_v6+2+(moko_speed_v6>>3))&31;
    else moko_cycle_v6=(moko_cycle_v6+1)&31;
    phase=(moko_cycle_v6>>2)&7;
    step=(phase==1?6:(phase==2?11:(phase==3?6:(phase==5?-6:(phase==6?-11:(phase==7?-6:0))))));
    if(moko_speed_v6<4)step=0;
    bob=(moko_speed_v6>4)?((phase==1||phase==3||phase==5||phase==7)?3:0):((tick/34)&1);
    ear=(moko_speed_v6>8)?((phase&1)?3:-1):0;tail=((tick/(moko_speed_v6>5?5:12))&3)-1;
    if(moko_prev_jump_v6>0&&jump==0)moko_land_fx_v6=9;
    if(moko_land_fx_v6>0)moko_land_fx_v6--;
    y=gy-jump+(moko_land_fx_v6>5?4:0);blink=((tick%137)>130);plant=(moko_speed_v6>7&&((phase==0)||(phase==4)));
    shadow(ot,pk,x,z,38,jump);
    /* compact pear-shaped feline body; v3 regression contract retained */
    prism(ot,pk,x+moko_lean_v6,y+72-bob,z+4,69,76,59,99,49,151);
    box3(ot,pk,x-29+moko_lean_v6,y+91-bob,z-1,58,48,54,113,59,166);
    prism(ot,pk,x+moko_lean_v6/3,y+27-bob,z-2,85,63,59,145,78,190);
    box3(ot,pk,x-25+moko_lean_v6/3,y+49-bob,z-17,50,19,22,212,181,200);
    prism(ot,pk,x-25+moko_lean_v6/3,y-11-bob-ear,z+5,39,52,28,111,45,153);
    prism(ot,pk,x+25+moko_lean_v6/3,y-11-bob+ear,z+5,39,52,28,111,45,153);
    box3(ot,pk,x-23+moko_lean_v6/3,y+34-bob,z-25,12,blink?3:8,9,231,224,235);
    box3(ot,pk,x+11+moko_lean_v6/3,y+34-bob,z-25,12,blink?3:8,9,231,224,235);
    if(!blink){box3(ot,pk,x-19+moko_lean_v6/3,y+36-bob,z-30,5,6,6,36,29,45);box3(ot,pk,x+14+moko_lean_v6/3,y+36-bob,z-30,5,6,6,36,29,45);}
    prism(ot,pk,x+moko_lean_v6/3,y+52-bob,z-31,11,10,7,232,105,142);
    prism(ot,pk,x+moko_lean_v6,y+105-bob,z-18,36,38,16,207,166,74);prism(ot,pk,x+moko_lean_v6,y+112-bob,z-23,21,22,10,242,224,157);
    box3(ot,pk,x-2+moko_lean_v6,y+114-bob,z-27,4,14,5,34,28,39);box3(ot,pk,x+moko_lean_v6,y+122-bob,z-27,12,4,5,34,28,39);
    box3(ot,pk,x-23-step,y+137-bob,z+1,18,35,34,69,34,109);box3(ot,pk,x+5+step,y+137-bob,z+1,18,35,34,69,34,109);
    prism(ot,pk,x-15-step,y+169-bob,z-7,32,plant?16:20,41,52,28,82);prism(ot,pk,x+15+step,y+169-bob,z-7,32,plant?16:20,41,52,28,82);
    prism(ot,pk,x-29+step/2+moko_lean_v6,y+108-bob,z-13,18,38,25,92,45,139);prism(ot,pk,x+29-step/2+moko_lean_v6,y+108-bob,z-13,18,38,25,92,45,139);
    prism(ot,pk,x-30+step/2+moko_lean_v6,y+141-bob,z-21,24,14,31,58,31,89);prism(ot,pk,x+30-step/2+moko_lean_v6,y+141-bob,z-21,24,14,31,58,31,89);
    if(dir>0){box3(ot,pk,x+27,y+111-bob,z+18,38+tail*4,8,10,207,59,135);prism(ot,pk,x+67+tail*4,y+72-bob-tail*4,z+18,15,53+tail*3,12,225,157,78);}
    else{box3(ot,pk,x-65-tail*4,y+111-bob,z+18,38+tail*4,8,10,207,59,135);prism(ot,pk,x-70-tail*4,y+72-bob-tail*4,z+18,15,53+tail*3,12,225,157,78);}
    if((plant&&moko_speed_v6>12)||moko_land_fx_v6>0){int spread=moko_land_fx_v6?12-moko_land_fx_v6:5;prism(ot,pk,x-28-spread,178,z+24,15+spread,8,14,118,105,88);prism(ot,pk,x+28+spread,178,z+24,15+spread,8,14,132,114,91);}
    lx=x;lz=z;moko_prev_jump_v6=jump;
}
static void camera_follow'''
src,n=pat.subn(rep,src,count=1)
if n!=1: raise SystemExit('v6 Moko replacement failed')

pat=re.compile(r'static void villager\(uint32_t\*ot,char\*\*pk,int x,int z,int tick,int active\)\{.*?\}\nstatic void boar',re.S)
rep=r'''static void villager(uint32_t*ot,char**pk,int x,int z,int tick,int active){
    int bob=((tick/20)&1)*3,wave=active?(((tick/7)&3)-1)*7:0;
    shadow(ot,pk,x,z,23,0);box3(ot,pk,x-17,103-bob,z,34,64,34,66,107,132);box3(ot,pk,x-22,69-bob,z-3,44,39,39,190,158,126);prism(ot,pk,x,45-bob,z-2,50,30,32,72,51,88);
    box3(ot,pk,x-23,164-bob,z,17,21,28,48,45,56);box3(ot,pk,x+6,164-bob,z,17,21,28,48,45,56);
    prism(ot,pk,x-28,111-bob,z-8,14,37,20,58,91,115);prism(ot,pk,x+30+wave,active?77-bob:111-bob,z-8,14,42,20,58,91,115);
    if(active){int p=9+((tick/7)&3)*3;prism(ot,pk,x,20-p,z-12,20,24,10,237,200,89);}
}
static void boar'''
src,n=pat.subn(rep,src,count=1)
if n!=1: raise SystemExit('v6 villager replacement failed')

anchor='static void foreground_frame('
if anchor not in src: raise SystemExit('v6 foreground anchor missing')
helper=r'''static void dawn_gate_flourish(uint32_t*ot,char**pk,int clear,int tick){
    int i;if(!clear)return;
    for(i=0;i<6;i++){int phase=(tick*3+i*11)&63;int x=850+i*22+((phase&7)-3)*3;int y=128-(phase*2);int z=1320+(i&1)*26;prism(ot,pk,x,y,z,9,15,9,104+i*12,214,188);}
}
'''
src=src.replace(anchor,helper+anchor,1)
old='boar(ot,pk,wx(258),wz(168),enemy_hp,tick);gate(ot,pk,clear,tick);'
new='boar(ot,pk,wx(258),wz(168),enemy_hp,tick);gate(ot,pk,clear,tick);dawn_gate_flourish(ot,pk,clear,tick);'
if old not in src: raise SystemExit('v6 gate draw anchor missing')
src=src.replace(old,new,1)

out=pathlib.Path(sys.argv[2]);out.write_text(src)
subprocess.check_call([sys.executable,str(pathlib.Path(__file__).with_name('build_world3d_slice_v7.py')),str(out),str(out)])
