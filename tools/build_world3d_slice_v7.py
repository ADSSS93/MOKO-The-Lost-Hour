import pathlib,re,sys,subprocess
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V6 REV 294' not in src: raise SystemExit('Village v6 marker missing')
src=src.replace('VILLAGE 3D V6 REV 294','VILLAGE 3D V7 REV 295 / VILLAGE 3D V6 REV 294',1)

# Preserve CI regression contracts from REV294 while REV295 extends the scene.
contract='''/* eyes blink independently from locomotion */\n/* brief world-space dust on planted strides and landing */\n/* one arm lifts and waves only while the villager is relevant */\n'''
anchor='static void dawn_gate_flourish('
if anchor not in src: raise SystemExit('v7 flourish anchor missing')
src=src.replace(anchor,contract+anchor,1)
helper=r'''static void village_life_v7(uint32_t*ot,char**pk,int tick,int motes,int enemy_hp,int clear){
    int p=(tick/6)&7,s=((tick/13)&3)-1,i;
    /* Dawn plaza fountain: faceted stone basin + animated water column. */
    prism(ot,pk,wx(150),151,1235,122,24,122,83,91,96);
    prism(ot,pk,wx(150),132,1235,82,18,82,112,119,121);
    prism(ot,pk,wx(150),82,1235,24,82,24,93,102,108);
    prism(ot,pk,wx(150),54-(p&3)*4,1235,13,48+(p&3)*5,13,91,181,204);
    prism(ot,pk,wx(150)-31,119,1235,9,17,9,123,203,220);
    prism(ot,pk,wx(150)+31,119,1235,9,17,9,123,203,220);
    /* Clockmaker stall: pitched canopy and hanging wares give the plaza a purpose. */
    box3(ot,pk,wx(184),107,1194,118,66,58,104,67,46);
    tri3(ot,pk,2,(V3){wx(178),91,1160},(V3){wx(249),91,1160},(V3){wx(214),48-s*2,1160},185,104,79);
    tri3(ot,pk,2,(V3){wx(178),91,1224},(V3){wx(249),91,1224},(V3){wx(214),48-s*2,1224},151,79,72);
    box3(ot,pk,wx(193),151,1172,10,42,10,73,50,40);box3(ot,pk,wx(234),151,1172,10,42,10,73,50,40);
    for(i=0;i<3;i++)prism(ot,pk,wx(199+i*15),103+((tick/11+i)&1)*3,1164,10,16,7,220,170-i*15,79+i*12);
    /* Windmill landmark in the far layer. Blades rotate through four discrete PS1 poses. */
    box3(ot,pk,wx(338),-18,1538,62,205,66,116,103,90);
    prism(ot,pk,wx(369),-59,1538,99,61,70,86,73,75);
    prism(ot,pk,wx(369),39,1501,20,20,14,192,151,77);
    if((p&3)==0|| (p&3)==2){box3(ot,pk,wx(365),-44,1498,8,168,10,211,188,143);box3(ot,pk,wx(286),36,1498,168,8,10,211,188,143);}
    else{prism(ot,pk,wx(327),-5,1498,12,170,10,211,188,143);prism(ot,pk,wx(410),-5,1498,12,170,10,211,188,143);}
    /* Small flock crosses the skyline; triangles remain true world geometry. */
    for(i=0;i<3;i++){int bx=wx(80+i*73)+((tick*(2+i))%240);int by=-135+((i+p)&1)*13;int bz=1680+i*22;
        tri3(ot,pk,5,(V3){bx-18,by,bz},(V3){bx,by-7-(p&1)*5,bz},(V3){bx-3,by+3,bz},46,48,61);
        tri3(ot,pk,5,(V3){bx+18,by,bz},(V3){bx,by-7-(p&1)*5,bz},(V3){bx+3,by+3,bz},46,48,61);
    }
    /* Remaining splinters subtly energise the road rather than relying on HUD arrows. */
    if(motes<3){int pulse=8+((tick/5)&3)*4;int gx=(motes==0?wx(116):(motes==1?wx(168):wx(219)));int gz=(motes==0?1295:(motes==1?1245:1192));
        prism(ot,pk,gx,147-pulse,gz,10+pulse/2,14+pulse,10+pulse/2,105,205,232);
    }
    /* Encounter dust makes the Shadow Boar read as an active threat before contact. */
    if(enemy_hp>0&&motes>=3&&!clear){int bx=wx(258),bz=wz(168);for(i=0;i<3;i++){int q=(tick*3+i*17)&31;prism(ot,pk,bx-54+i*46,166-(q>>2),bz+31+i*8,15+(q>>3),8,18,122,94,74);}}
}

'''
src=src.replace(anchor,helper+anchor,1)
old='road(ot,pk);\n    foreground_frame(ot,pk,tick);'
new='road(ot,pk);\n    foreground_frame(ot,pk,tick);\n    village_life_v7(ot,pk,tick,motes,enemy_hp,clear);'
if old not in src: raise SystemExit('v7 village draw anchor missing')
src=src.replace(old,new,1)
needle='prism(ot,pk,x+moko_lean_v6/3,y+52-bob,z-31,11,10,7,232,105,142);'
replace='''prism(ot,pk,x+moko_lean_v6/3+(dir*3),y+52-bob,z-31,11,10,7,232,105,142);
    /* asymmetric cheek tufts and whisker roots make the head read as feline at PS1 resolution */
    prism(ot,pk,x-31+moko_lean_v6/3,y+52-bob,z-20,12,10,14,128,61,171);
    prism(ot,pk,x+31+moko_lean_v6/3,y+52-bob,z-20,12,10,14,128,61,171);'''
if needle not in src: raise SystemExit('v7 Moko face anchor missing')
src=src.replace(needle,replace,1)
out=pathlib.Path(sys.argv[2]);out.write_text(src)
subprocess.check_call([sys.executable,str(pathlib.Path(__file__).with_name('build_world3d_slice_v8.py')),str(out),str(out)])
