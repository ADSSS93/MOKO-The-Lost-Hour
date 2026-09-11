import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()
if 'VILLAGE 3D V10 REV 299' not in src:
    raise SystemExit('Village v10 marker missing')
src=src.replace('VILLAGE 3D V10 REV 299','VILLAGE 3D V11 REV 300 / VILLAGE 3D V10 REV 299',1)

# Runtime emulator testing exposed classic PS1 near-plane explosions: a primitive
# with one projected vertex far outside the viewport can become a giant black
# triangle/quad. Keep authored XYZ geometry, but reject wildly projected vertices
# before they reach the ordering table. The generous guard still allows normal
# off-screen entry/exit and camera motion.
anchor='static int wz(int sy){return 1010+(190-sy)*7;}'
if anchor not in src:
    raise SystemExit('rev300 projection helper anchor missing')
helper='''\nstatic int projected_xy_sane(int32_t s){short x=(short)s,y=(short)(s>>16);return x>-320&&x<640&&y>-240&&y<480;}'''
src=src.replace(anchor,anchor+helper,1)

tri_old='if(!(flag&0x80000000)){setXY3(p,'
tri_new='if(!(flag&0x80000000)&&projected_xy_sane(s0)&&projected_xy_sane(s1)&&projected_xy_sane(s2)){setXY3(p,'
if tri_old not in src:
    raise SystemExit('rev300 triangle projection guard anchor missing')
src=src.replace(tri_old,tri_new)

quad_old='if(!(flag&0x80000000)){setXY4(p,'
quad_new='if(!(flag&0x80000000)&&projected_xy_sane(s0)&&projected_xy_sane(s1)&&projected_xy_sane(s2)&&projected_xy_sane(s3)){setXY4(p,'
if quad_old not in src:
    raise SystemExit('rev300 quad projection guard anchor missing')
src=src.replace(quad_old,quad_new)

# REV297 deliberately brought ground geometry close to the eye to fill the frame,
# but the emulator showed the front edge crossing the useful near-plane during
# spring-camera motion. Retain the full-frame ground, just stage its front edge
# farther away so it cannot invert across the camera.
src=src.replace('(V3){-1700,188,180},(V3){1700,188,180}',
                '(V3){-1700,188,430},(V3){1700,188,430}',1)
src=src.replace('(V3){-1700,187,190},(V3){-470,187,190}',
                '(V3){-1700,187,445},(V3){-470,187,445}',1)
src=src.replace('(V3){470,187,190},(V3){1700,187,190}',
                '(V3){470,187,445},(V3){1700,187,445}',1)

src+='\n/* REV300 RUNTIME PROJECTION SAFETY: NO GIANT NEAR-PLANE PRIMITIVES */\n'
pathlib.Path(sys.argv[2]).write_text(src)
