#!/usr/bin/env python3
"""Tiny build-time OBJ -> C header converter for the clean PS1 vertical slice.

This deliberately keeps authoring data outside the renderer: artists edit OBJ,
CMake converts it to compact fixed-point vertex/triangle tables, and the PS1
runtime only sees static arrays. Only v/f records are required for now.
"""
from pathlib import Path
import re, sys

if len(sys.argv) != 4:
    raise SystemExit("usage: obj_to_header.py input.obj output.h symbol")

src, out, sym = map(Path, sys.argv[:3]) if False else (Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", sym):
    raise SystemExit("invalid C symbol")

verts=[]
faces=[]
for raw in src.read_text().splitlines():
    line=raw.strip()
    if not line or line.startswith('#'):
        continue
    p=line.split()
    if p[0]=='v' and len(p)>=4:
        verts.append(tuple(int(round(float(x))) for x in p[1:4]))
    elif p[0]=='f' and len(p)>=4:
        ids=[]
        for tok in p[1:]:
            i=int(tok.split('/')[0])
            if i<0: i=len(verts)+i
            else: i-=1
            ids.append(i)
        for i in range(1,len(ids)-1):
            faces.append((ids[0],ids[i],ids[i+1]))

if not verts or not faces:
    raise SystemExit(f"{src}: no usable mesh")
if len(verts)>65535:
    raise SystemExit(f"{src}: too many vertices")
for f in faces:
    if min(f)<0 or max(f)>=len(verts):
        raise SystemExit(f"{src}: face index out of range")

out.parent.mkdir(parents=True, exist_ok=True)
guard=f"MOKO_GEN_{sym.upper()}_H"
with out.open('w') as fp:
    fp.write(f"#ifndef {guard}\n#define {guard}\n")
    fp.write("typedef struct { short x,y,z; } MokoMeshV;\n")
    fp.write("typedef struct { unsigned short a,b,c; } MokoMeshF;\n")
    fp.write(f"static const MokoMeshV {sym}_v[]={{\n")
    for v in verts: fp.write(f"  {{{v[0]},{v[1]},{v[2]}}},\n")
    fp.write("};\n")
    fp.write(f"static const MokoMeshF {sym}_f[]={{\n")
    for f in faces: fp.write(f"  {{{f[0]},{f[1]},{f[2]}}},\n")
    fp.write("};\n")
    fp.write(f"#define {sym.upper()}_VERTS {len(verts)}\n")
    fp.write(f"#define {sym.upper()}_FACES {len(faces)}\n")
    fp.write(f"#endif\n")
