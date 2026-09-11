#include <stdint.h>
#include <psxgpu.h>
#include <psxgte.h>
#include <inline_c.h>
#include "moko_model.h"

typedef struct { short x,y,z; } MV;
typedef struct { unsigned char a,b,c,r,g,bcol; } MF;

/* Original MOKO mesh authored for the project.  It is deliberately a real
   triangulated silhouette rather than a pile of runtime boxes.  The current
   palette is untextured while the asset pipeline is being moved toward the
   OBJ/UV workflow used by the reference PS1 demo. */
static const MV vtx[]={
 /* torso */ {-28,72, 18},{ 28,72,18},{-38,118,14},{38,118,14},{-28,151,18},{28,151,18},{0,92,-24},{0,139,-20},
 /* head */ {-39,27,12},{39,27,12},{-43,64,9},{43,64,9},{-25,80,7},{25,80,7},{0,25,-25},{0,70,-33},
 /* ears */ {-34,28,9},{-18,-8,13},{-5,29,7},{5,29,7},{18,-8,13},{34,28,9},
 /* feet */ {-30,150,12},{-42,178,-5},{-4,176,-9},{30,150,12},{42,178,-5},{4,176,-9},
 /* muzzle */ {-17,58,-31},{17,58,-31},{0,76,-39},
 /* chest clock */ {-19,95,-25},{19,95,-25},{18,124,-24},{-18,124,-24},
 /* tail base/segments */ {30,112,18},{55,104,16},{72,86,13},{82,62,10}
};
static const MF face[]={
 {0,1,6,107,55,154},{0,6,2,98,47,146},{1,3,6,122,63,169},{2,6,7,92,43,137},{3,7,6,108,51,153},{2,7,4,78,37,121},{3,5,7,91,42,133},{4,7,5,70,33,108},
 {8,14,10,151,83,194},{10,14,15,137,70,182},{10,15,12,129,63,175},{9,11,14,159,89,201},{11,15,14,144,76,188},{11,13,15,136,69,180},{8,9,14,171,98,211},{9,15,14,162,91,204},{12,15,13,119,57,164},
 {16,17,18,113,45,153},{19,20,21,113,45,153},
 {22,23,24,62,31,94},{22,24,4,70,35,105},{25,26,27,62,31,94},{25,5,27,70,35,105},
 {28,29,30,233,225,241},
 {31,32,33,209,170,76},{31,33,34,198,155,65},
 {35,36,37,212,61,139},{35,37,38,221,75,145}
};

static void tri(uint32_t*ot,char**pk,int d,MV a,MV b,MV c,int r,int g,int bl){
    POLY_F3*p=(POLY_F3*)*pk;SVECTOR va={a.x,a.y,a.z,0},vb={b.x,b.y,b.z,0},vc={c.x,c.y,c.z,0};
    int32_t s0,s1,s2,flag;setPolyF3(p);setRGB0(p,r,g,bl);gte_ldv3(&va,&vb,&vc);gte_rtpt();
    gte_stsxy0(&s0);gte_stsxy1(&s1);gte_stsxy2(&s2);gte_stflg(&flag);
    if(!(flag&0x80000000)){setXY3(p,(short)s0,(short)(s0>>16),(short)s1,(short)(s1>>16),(short)s2,(short)(s2>>16));addPrim(ot+d,p);*pk+=sizeof(POLY_F3);}
}

static MV world(MV v,int x,int y,int z,int facing,int step,int bob){
    int sx=facing?1:-1;
    if(v.y>138){ if(v.x<0)v.x-=step; else v.x+=step; }
    v.x=(short)(x+sx*v.x);v.y=(short)(y+v.y-bob);v.z=(short)(z+v.z);return v;
}

void moko_model_draw(uint32_t *ot,char **pk,int x,int top_y,int z,int facing,int tick,int jump){
    int i,phase=(tick/5)&3,step=(phase==1?6:(phase==3?-6:0)),bob=(phase&1)*2;
    int y=top_y-jump;
    /* compact contact shadow */
    {
        MV a={x-30,184,z-8},b={x+30,184,z-8},c={x+23,184,z+18},d={x-23,184,z+18};
        tri(ot,pk,6,a,b,c,28,24,34);tri(ot,pk,6,a,c,d,28,24,34);
    }
    for(i=0;i<(int)(sizeof(face)/sizeof(face[0]));i++){
        MF f=face[i];MV a=world(vtx[f.a],x,y,z,facing,step,bob),b=world(vtx[f.b],x,y,z,facing,step,bob),c=world(vtx[f.c],x,y,z,facing,step,bob);
        tri(ot,pk,2,a,b,c,f.r,f.g,f.bcol);
    }
    /* clock hands, nose and bright eyes read at 320x240 */
    {
        int sx=facing?1:-1;MV e1={x-11*sx,y+49-bob,z-36},e2={x-4*sx,y+49-bob,z-37},e3={x-8*sx,y+55-bob,z-38};
        MV f1={x+4*sx,y+49-bob,z-37},f2={x+11*sx,y+49-bob,z-36},f3={x+8*sx,y+55-bob,z-38};
        MV n1={x-4*sx,y+63-bob,z-41},n2={x+4*sx,y+63-bob,z-41},n3={x,y+69-bob,z-43};
        tri(ot,pk,1,e1,e2,e3,248,244,250);tri(ot,pk,1,f1,f2,f3,248,244,250);tri(ot,pk,1,n1,n2,n3,232,103,147);
    }
}
