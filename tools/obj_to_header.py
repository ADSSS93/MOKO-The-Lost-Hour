#!/usr/bin/env python3
"""Build-time OBJ -> C header converter for MOKO's clean PS1 renderer.

Supports positions (v), texture coordinates (vt) and polygon faces. Polygons are
triangulated as a fan. Face corners retain both vertex and UV indices so the
runtime can emit PS1 textured triangles without hardcoded geometry.
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

def resolve(idx, count):
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
        # OBJ V runs bottom-up; PS1 texture V runs top-down. Store normalized 0..255.
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
if len(verts)>65535 or len(uvs)>65535:
    raise SystemExit(f"{src}: mesh table too large")
for tri in faces:
    for vi,ti in tri:
        if vi<0 or vi>=len(verts): raise SystemExit(f"{src}: vertex index out of range")
        if ti>=len(uvs): raise SystemExit(f"{src}: uv index out of range")

out.parent.mkdir(parents=True, exist_ok=True)
guard=f"MOKO_GEN_{sym.upper()}_H"
with out.open('w') as fp:
    fp.write(f"#ifndef {guard}\n#define {guard}\n")
    fp.write("#ifndef MOKO_GENERATED_MESH_TYPES\n#define MOKO_GENERATED_MESH_TYPES\n")
    fp.write("typedef struct { short x,y,z; } MokoMeshV;\n")
    fp.write("typedef struct { unsigned char u,v; } MokoMeshUV;\n")
    fp.write("typedef struct { unsigned short a,b,c; short ta,tb,tc; } MokoMeshF;\n")
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
