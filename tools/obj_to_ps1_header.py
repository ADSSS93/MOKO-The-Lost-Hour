import pathlib, sys

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
verts = []
faces = []
for raw in src.read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith('#'):
        continue
    parts = line.split()
    if parts[0] == 'v' and len(parts) >= 4:
        verts.append(tuple(int(round(float(v))) for v in parts[1:4]))
    elif parts[0] == 'f' and len(parts) >= 4:
        ids = []
        for tok in parts[1:]:
            ids.append(int(tok.split('/')[0]) - 1)
        for i in range(1, len(ids)-1):
            faces.append((ids[0], ids[i], ids[i+1]))

if not verts or not faces:
    raise SystemExit('OBJ contains no usable vertices/faces')
if len(verts) > 255:
    raise SystemExit('PS1 Moko mesh currently supports <=255 vertices')

text = []
text.append('#ifndef MOKO_MODEL_GENERATED_H')
text.append('#define MOKO_MODEL_GENERATED_H')
text.append(f'#define MOKO_MODEL_VERTEX_COUNT {len(verts)}')
text.append(f'#define MOKO_MODEL_FACE_COUNT {len(faces)}')
text.append('static const short moko_model_vertices[MOKO_MODEL_VERTEX_COUNT][3] = {')
for x,y,z in verts:
    text.append(f'  {{{x},{y},{z}}},')
text.append('};')
text.append('static const unsigned char moko_model_faces[MOKO_MODEL_FACE_COUNT][3] = {')
for a,b,c in faces:
    text.append(f'  {{{a},{b},{c}}},')
text.append('};')
text.append('#endif')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(text) + '\n')
print(f'generated {out}: {len(verts)} vertices, {len(faces)} triangles')
