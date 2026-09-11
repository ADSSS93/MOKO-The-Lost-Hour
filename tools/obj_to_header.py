#!/usr/bin/env python3
"""Build-time OBJ -> compact C mesh tables for MOKO's PS1 renderer.

Supports positions (v), UVs (vt) and polygon faces. When an authored OBJ has no
UV map yet, deterministic planar fallback UVs are generated from its X/Y bounds.
That means every asset can enter the textured PS1 renderer immediately, while a
Blender-authored unwrap can transparently replace the fallback later.
"""
from pathlib import Path
import re, sys

if len(sys.argv) != 4:
    raise SystemExit("usage: obj_to_header.py input.obj output.h symbol")

src, out, sym = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", sym):
    raise SystemExit("invalid C symbol")

verts=[]
uvs=[]
faces=[]

def resolve(idx,count):
    i=int(idx)
    return count+i if i<0 else i-1

for raw in src.read_text().splitlines():
    line=raw.strip()
    if not line or line.startswith('#'):
        continue
    p=line.split()
    if p[0]=='v' and len(p)>=4:
        verts.append(tuple(int(round(float(x))) for x in p[1:4]))
    elif p[0]=='vt' and len(p)>=3:
        u=max(0,min(255,int(round(float(p[1])*255))))
        v=max(0,min(255,int(round((1.0-float(p[2]))*255))))
        uvs.append((u,v))
    elif p[0]=='f' and len(p)>=4:
        corners=[]
        for tok in p[1:]:
            bits=tok.split('/')
            vi=resolve(bits[0],len(verts))
            ti=resolve(bits[1],len(uvs)) if len(bits)>1 and bits[1] else -1
            corners.append((vi,ti))
        for i in range(1,len(corners)-1):
            faces.append((corners[0],corners[i],corners[i+1]))

if not verts or not faces:
    raise SystemExit(f"{src}: no usable mesh")

# Assets created before the Blender-first workflow have geometry but no vt lines.
# Give them a stable 0..63 planar unwrap now; real Blender UVs take precedence.
if not uvs:
    xs=[v[0] for v in verts]; ys=[v[1] for v in verts]
    xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys)
    dx=max(1,xmax-xmin); dy=max(1,ymax-ymin)
    uvs=[(int((x-xmin)*63/dx),int((y-ymin)*63/dy)) for x,y,z in verts]
    faces=[tuple((vi,vi if ti<0 else ti) for vi,ti in tri) for tri in faces]
else:
    # Mixed authored/unwrapped corners fall back to vertex-indexed coordinates.
    # Extend the UV table only when required.
    if any(ti<0 for tri in faces for vi,ti in tri):
        xs=[v[0] for v in verts]; ys=[v[1] for v in verts]
        xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys)
        dx=max(1,xmax-xmin); dy=max(1,ymax-ymin)
        fallback=[]
        for x,y,z in verts:
            fallback.append((int((x-xmin)*63/dx),int((y-ymin)*63/dy)))
        base=len(uvs); uvs.extend(fallback)
        faces=[tuple((vi,base+vi if ti<0 else ti) for vi,ti in tri) for tri in faces]

if len(verts)>65535 or len(uvs)>65535:
    raise SystemExit(f"{src}: mesh table too large")
for tri in faces:
    for vi,ti in tri:
        if vi<0 or vi>=len(verts): raise SystemExit(f"{src}: vertex index out of range")
        if ti<0 or ti>=len(uvs): raise SystemExit(f"{src}: uv index out of range")

out.parent.mkdir(parents=True,exist_ok=True)
guard=f"MOKO_GEN_{sym.upper()}_H"
with out.open('w') as fp:
    fp.write(f"#ifndef {guard}\n#define {guard}\n")
    fp.write("#ifndef MOKO_GENERATED_MESH_TYPES\n#define MOKO_GENERATED_MESH_TYPES\n")
    fp.write("typedef struct { short x,y,z; } MokoMeshV;\n")
    fp.write("typedef struct { unsigned char u,v; } MokoMeshUV;\n")
    fp.write("typedef struct { unsigned short a,b,c; unsigned short ta,tb,tc; } MokoMeshF;\n")
    fp.write("#endif\n")
    fp.write(f"static const MokoMeshV {sym}_v[]={{\n")
    for v in verts: fp.write(f"  {{{v[0]},{v[1]},{v[2]}}},\n")
    fp.write("};\n")
    fp.write(f"static const MokoMeshUV {sym}_uv[]={{\n")
    for uv in uvs: fp.write(f"  {{{uv[0]},{uv[1]}}},\n")
    fp.write("};\n")
    fp.write(f"static const MokoMeshF {sym}_f[]={{\n")
    for tri in faces:
        (a,ta),(b,tb),(c,tc)=tri
        fp.write(f"  {{{a},{b},{c},{ta},{tb},{tc}}},\n")
    fp.write("};\n")
    fp.write(f"#define {sym.upper()}_VERTS {len(verts)}\n")
    fp.write(f"#define {sym.upper()}_UVS {len(uvs)}\n")
    fp.write(f"#define {sym.upper()}_FACES {len(faces)}\n")
    fp.write("#endif\n")
