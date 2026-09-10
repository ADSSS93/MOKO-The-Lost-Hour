#!/usr/bin/env python3
import struct,sys
from pathlib import Path
if len(sys.argv)!=2: raise SystemExit('usage: generate_moko_tim.py OUTPUT')
out=Path(sys.argv[1]);out.parent.mkdir(parents=True,exist_ok=True)
W,H,N=28,34,6;width=W*N;pix=[0]*(width*H)
P=0x5C7D;D=0x3518;S=0x28D3;L=0x71BF;LI=0x69BE;PK=0x5DDF;CR=0x6F7B;WH=0x7FFF;BK=0x0842;GO=0x2B3F;CY=0x7E60

def put(f,x,y,c):
 if 0<=x<W and 0<=y<H: pix[y*width+f*W+x]=c
def box(f,x0,y0,x1,y1,c):
 for y in range(y0,y1+1):
  for x in range(x0,x1+1): put(f,x,y,c)
def line(f,x0,y0,x1,y1,c):
 dx=abs(x1-x0);sx=1 if x0<x1 else -1;dy=-abs(y1-y0);sy=1 if y0<y1 else -1;e=dx+dy
 while 1:
  put(f,x0,y0,c)
  if x0==x1 and y0==y1: break
  e2=2*e
  if e2>=dy:e+=dy;x0+=sx
  if e2<=dx:e+=dx;y0+=sy

def moko(f,step,right):
 b=1 if step==2 else 0; lean=1 if step==1 else 0
 # large pointed ears and rounded stepped skull
 for x,y in [(5,6),(6,4),(7,2),(8,4),(9,6),(19,6),(20,4),(21,2),(22,4),(23,6)]: put(f,x,y-b,D)
 box(f,7,4-b,9,7-b,PK);box(f,19,4-b,21,7-b,PK)
 box(f,5,7-b,23,12-b,P);box(f,4,9-b,24,12-b,P);box(f,6,6-b,22,9-b,L)
 put(f,3,10-b,L);put(f,25,10-b,L);put(f,4,13-b,LI);put(f,24,13-b,LI)
 box(f,7,10-b,21,14-b,LI);box(f,10,12-b,18,15-b,CR)
 # eyes, nose, whiskers
 for ex in (9,18): box(f,ex,9-b,ex+1,10-b,WH);put(f,ex+(1 if right else 0),10-b,BK)
 put(f,14,12-b,PK);put(f,14,13-b,BK)
 line(f,7,12-b,1,11-b,WH);line(f,7,14-b,1,15-b,WH);line(f,21,12-b,27,11-b,WH);line(f,21,14-b,27,15-b,WH)
 # short-neck pear torso / haunches
 box(f,10-lean,15-b,18-lean,18-b,P);box(f,7-lean,18-b,21-lean,25-b,P);box(f,9-lean,20-b,19-lean,27-b,D)
 put(f,6-lean,22-b,L);put(f,22-lean,22-b,L)
 # chest clock, circular-ish stepped bezel
 box(f,11-lean,18-b,17-lean,24-b,GO);box(f,10-lean,20-b,18-lean,22-b,GO);box(f,12-lean,19-b,16-lean,23-b,CR)
 put(f,14-lean,20-b,BK);put(f,14-lean,21-b,CY);put(f,15-lean,22-b,CY)
 # forepaws, bent feline rear legs
 if step==1:
  box(f,5,18-b,8,23-b,P);box(f,3,23-b,8,25-b,L);box(f,20,19-b,23,24-b,P);box(f,20,24-b,25,26-b,L)
  box(f,7,25-b,12,29-b,S);box(f,4,29-b,12,32-b,D);box(f,17,25-b,21,28-b,S);box(f,17,28-b,24,31-b,D)
 elif step==2:
  box(f,5,19-b,8,24-b,P);box(f,3,24-b,8,26-b,L);box(f,20,17-b,23,23-b,P);box(f,20,23-b,25,25-b,L)
  box(f,6,25-b,11,28-b,S);box(f,4,28-b,12,31-b,D);box(f,17,25-b,22,29-b,S);box(f,16,29-b,24,32-b,D)
 else:
  box(f,5,18-b,8,24-b,P);box(f,3,24-b,8,26-b,L);box(f,20,18-b,23,24-b,P);box(f,20,24-b,25,26-b,L)
  box(f,7,25-b,12,30-b,S);box(f,4,30-b,12,32-b,D);box(f,17,25-b,22,30-b,S);box(f,17,30-b,25,32-b,D)
 # long clock-hand tail outside body silhouette
 if right:
  line(f,22,22-b,26,24-b,PK);line(f,26,24-b,26,16-b-(step==2),PK);line(f,26,16-b-(step==2),23,12-b,PK);put(f,23,11-b,GO);put(f,22,12-b,GO);put(f,24,12-b,GO)
 else:
  line(f,7,22-b,2,24-b,PK);line(f,2,24-b,2,16-b-(step==2),PK);line(f,2,16-b-(step==2),5,12-b,PK);put(f,5,11-b,GO);put(f,4,12-b,GO);put(f,6,12-b,GO)
for base,right in ((0,True),(3,False)):
 for s in range(3):moko(base+s,s,right)
header=struct.pack('<II',0x10,0x02);data=b''.join(struct.pack('<H',p) for p in pix);image=struct.pack('<IHHHH',12+len(data),448,0,width,H)+data
out.write_bytes(header+image);print(f'generated {out} ({width}x{H}, {N} frames) MOKO VISUAL REV 284')
