import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V10 REV 299' not in src:
    raise SystemExit('Village v10 marker missing')
src=src.replace('VILLAGE 3D V10 REV 299','VILLAGE 3D V12 REV 301 / VILLAGE 3D V11 REV 300 / VILLAGE 3D V10 REV 299',1)

# Runtime emulator testing exposed classic PS1 near-plane explosions: a primitive
# with one projected vertex far outside the viewport can become a giant black
# triangle/quad. Keep authored XYZ geometry, but reject wildly projected vertices.
anchor='static int wz(int sy){return 1010+(190-sy)*7;}'
if anchor not in src:
    raise SystemExit('rev301 projection helper anchor missing')
helper='''\nstatic int projected_xy_sane(int32_t s){short x=(short)s,y=(short)(s>>16);return x>-320&&x<640&&y>-240&&y<480;}'''
src=src.replace(anchor,anchor+helper,1)

tri_old='if(!(flag&0x80000000)){setXY3(p,'
tri_new='if(!(flag&0x80000000)&&projected_xy_sane(s0)&&projected_xy_sane(s1)&&projected_xy_sane(s2)){setXY3(p,'
if tri_old not in src:
    raise SystemExit('rev301 triangle projection guard anchor missing')
src=src.replace(tri_old,tri_new)
quad_old='if(!(flag&0x80000000)){setXY4(p,'
quad_new='if(!(flag&0x80000000)&&projected_xy_sane(s0)&&projected_xy_sane(s1)&&projected_xy_sane(s2)&&projected_xy_sane(s3)){setXY4(p,'
if quad_old not in src:
    raise SystemExit('rev301 quad projection guard anchor missing')
src=src.replace(quad_old,quad_new)

# Keep the older broad road safely away from the eye.
src=src.replace('(V3){-1700,188,180},(V3){1700,188,180}',
                '(V3){-1700,188,430},(V3){1700,188,430}',1)
src=src.replace('(V3){-1700,187,190},(V3){-470,187,190}',
                '(V3){-1700,187,445},(V3){-470,187,445}',1)
src=src.replace('(V3){470,187,190},(V3){1700,187,190}',
                '(V3){470,187,445},(V3){1700,187,445}',1)

# REV301: the real #435 emulator frame showed that the decorative foreground
# silhouettes were reading as giant black debug triangles. Remove that whole
# presentation device. Replace it with short, bounded XYZ ground strips that
# approach the camera progressively, so no single polygon crosses the near plane.
src=src.replace('foreground_frame(ot,pk,tick);','/* REV301: broken foreground silhouettes removed after emulator QA. */',1)

insert_anchor='static void playable_area_frame_v10(uint32_t*ot,char**pk,int motes,int enemy_hp,int clear,int tick){'
if insert_anchor not in src:
    raise SystemExit('rev301 playable-area helper anchor missing')
foreground=r'''static void commercial_foreground_v12(uint32_t*ot,char**pk,int tick){
    int pulse=(tick/12)&1;
    /* Segmented warm stone plaza: close geometry is deliberately split into
       multiple shallow quads to avoid PS1 near-plane explosions. */
    quad3g(ot,pk,7,(V3){-980,188,360},(V3){980,188,360},(V3){900,188,520},(V3){-900,188,520},72,63,57,88,75,61);
    quad3g(ot,pk,7,(V3){-900,188,525},(V3){900,188,525},(V3){790,188,700},(V3){-790,188,700},88,75,61,107,88,65);
    /* Centre path pulls the eye toward the clock tower rather than leaving an
       empty lower half of the frame. */
    quad3g(ot,pk,6,(V3){-330,184,365},(V3){330,184,365},(V3){290,184,720},(V3){-290,184,720},125,104,73,151,123,77);
    /* Low curb stones frame the playable lane without screen-space bars. */
    box3(ot,pk,-390,178,430,34,10,250,132,104,70);
    box3(ot,pk,356,178,430,34,10,250,132,104,70);
    /* Two small lantern stones anchor the immediate foreground and make the
       bottom corners feel authored rather than empty. */
    box3(ot,pk,-455,154,520,18,32,20,79,66,58);
    box3(ot,pk,437,154,520,18,32,20,79,66,58);
    prism(ot,pk,-446,140-pulse*2,515,24,22,18,218,158,77);
    prism(ot,pk,446,140-pulse*2,515,24,22,18,218,158,77);
}
'''
src=src.replace(insert_anchor,foreground+insert_anchor,1)

# Draw the new close-range geometry immediately after the road so it contributes
# to the composition before characters and props.
road_call='road(ot,pk);'
if road_call not in src:
    raise SystemExit('rev301 road draw anchor missing')
src=src.replace(road_call,road_call+'\n    commercial_foreground_v12(ot,pk,tick);',1)

# Runtime frame showed Moko reading too large and too high relative to the scene.
# Lower him slightly and reduce the exaggerated GTE zoom, moving toward a late-PS1
# 2.5D framing where the character occupies roughly a quarter to a third of height.
src=src.replace('gte_SetGeomOffset(160,154);gte_SetGeomScreen(292);','gte_SetGeomOffset(160,142);gte_SetGeomScreen(268);',1)
src=src.replace('moko(ot,pk,mx,-18,mz,facing,tick,player_jump);','moko(ot,pk,mx,0,mz,facing,tick,player_jump);',1)

# Push the camera a touch farther back while preserving the authored spring logic.
src=src.replace('t.vx=-cam_follow_x;t.vy=-48;t.vz=78-(cam_follow_z-1120)/22;',
                't.vx=-cam_follow_x;t.vy=-42;t.vz=108-(cam_follow_z-1120)/22;',1)

src+='\n/* REV301 RUNTIME VISUAL RESET: SAFE FOREGROUND / FULL FRAME / TOMBI-BENCHMARKED SCALE */\n'
pathlib.Path(sys.argv[2]).write_text(src)
