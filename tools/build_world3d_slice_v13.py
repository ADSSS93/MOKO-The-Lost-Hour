import pathlib,re,sys
src=pathlib.Path(sys.argv[1]).read_text()

# REV314 is now the authoritative presentation layer. Older REV310/313 builds
# are still accepted for backwards-compatible local experiments, but this final
# pass must never overwrite the model-first road/camera authored by v12.
if 'VILLAGE 3D V24 REV 314' not in src and 'VILLAGE 3D V20 REV 310' not in src:
    raise SystemExit('REV314/REV310 presentation marker missing')

# Last-resort cleanup only: remove every legacy base tree placement known to
# have produced near-plane wedges. Do not restage road, camera or Moko here.
for call in (
    'tree(ot,pk,-820,1220);','tree(ot,pk,720,1190);','tree(ot,pk,-1100,900);','tree(ot,pk,1110,960);',
    'tree(ot,pk,-835,1190);','tree(ot,pk,745,1170);','tree(ot,pk,-1120,900);','tree(ot,pk,1120,945);',
):
    src=src.replace(call,'/* REV314 legacy tree removed */')

# Catch any remaining literal tree placements while keeping the helper itself
# available for distant authored foliage if needed later.
src=re.sub(r'(?m)^\s*tree\(ot,pk,-?\d+,\d+\);\s*$', '/* REV314 legacy tree placement removed */', src)

src+='\n/* REV314 FINAL WORLD PASS: PRESERVE OBJ MOKO / SAFE CAMERA / NO NEAR TREES */\n'
pathlib.Path(sys.argv[2]).write_text(src)
