import pathlib,re,sys,subprocess
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V8 REV 296' not in src:
    raise SystemExit('Village v8 marker missing')
src=src.replace('VILLAGE 3D V8 REV 296','VILLAGE 3D V9 REV 297 / VILLAGE 3D V8 REV 296',1)

# REV297 is driven by the first real emulator screenshot. REV295/296 projected the
# entire authored scene into the upper portion of the 320x240 display, leaving a
# large black dead zone. Reframe the actual GTE viewport before adding any more art.
src=src.replace('gte_SetGeomOffset(160,108);gte_SetGeomScreen(236);','gte_SetGeomOffset(160,154);gte_SetGeomScreen(292);',1)

old='t.vx=-cam_follow_x;t.vy=-82;t.vz=132-(cam_follow_z-1120)/19;'
new='t.vx=-cam_follow_x;t.vy=-48;t.vz=78-(cam_follow_z-1120)/22;'
if old not in src: raise SystemExit('rev297 village camera translation anchor missing')
src=src.replace(old,new,1)

road_old='quad3(ot,pk,7,(V3){-1450,188,500},(V3){1450,188,500},(V3){1450,188,1900},(V3){-1450,188,1900},71,67,59);'
road_new='quad3g(ot,pk,7,(V3){-1700,188,180},(V3){1700,188,180},(V3){1500,188,2050},(V3){-1500,188,2050},67,61,55,88,78,65);'
if road_old not in src: raise SystemExit('rev297 road floor anchor missing')
src=src.replace(road_old,road_new,1)

needle='road(ot,pk);\n    foreground_frame(ot,pk,tick);'
replacement='''road(ot,pk);\n    quad3g(ot,pk,7,(V3){-1700,187,190},(V3){-470,187,190},(V3){-520,187,1250},(V3){-1550,187,1510},44,70,57,70,91,67);\n    quad3g(ot,pk,7,(V3){470,187,190},(V3){1700,187,190},(V3){1550,187,1510},(V3){520,187,1250},45,72,58,72,94,69);\n    foreground_frame(ot,pk,tick);'''
if needle not in src: raise SystemExit('rev297 world fill anchor missing')
src=src.replace(needle,replacement,1)

src=src.replace('if(px<90)target_pitch=178;','if(px<90)target_pitch=154;',1)
src=src.replace('else if(px>176&&px<226){target_pitch=193;','else if(px>176&&px<226){target_pitch=164;',1)
src=src.replace('else if(px>=226&&px<330)target_pitch=199;','else if(px>=226&&px<330)target_pitch=170;',1)
src=src.replace('else if(px>=330){target_pitch=182;','else if(px>=330){target_pitch=158;',1)

pat=re.compile(r'moko\(ot,pk,mx,7,mz,facing,tick,player_jump\);')
if not pat.search(src): raise SystemExit('rev297 Moko draw anchor missing')
src=pat.sub('moko(ot,pk,mx,-18,mz,facing,tick,player_jump);',src,count=1)

src+='\n/* REV297 EMULATOR FRAMING FIX: full-frame XYZ ground / GTE offset 160,154 / screen 292 */\n'
out=pathlib.Path(sys.argv[2]);out.write_text(src)
subprocess.check_call([sys.executable,str(pathlib.Path(__file__).with_name('build_world3d_slice_v10.py')),str(out),str(out)])
