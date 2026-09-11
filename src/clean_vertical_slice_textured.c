#include <stdint.h>
#include <stdio.h>
#include <psxgpu.h>
#include <psxgte.h>
#include <psxpad.h>
#include <psxapi.h>
#include <psxetc.h>
#include <inline_c.h>

#include "moko_generated.h"
#include "village_model.h"
#include "clockmaker_model.h"
#include "boar_model.h"

#define OT_LEN 9
#define OT_SIZE (1 << OT_LEN)
#define PACKET_LEN 65536
#define TEX_X 640
#define TEX_Y 0
#define TEX_W 64
#define TEX_H 64

typedef struct { DISPENV disp; DRAWENV draw; uint32_t ot[OT_SIZE]; char packets[PACKET_LEN]; } Frame;
typedef enum { MOKO_IDLE=0,MOKO_RUN=1,MOKO_JUMP=2,MOKO_ATTACK=3 } MokoAnim;

static Frame fb[2];
static int active=0,font_id=0,tick=0;
static char *packet;
static char pad_buffer[2][34];
static uint16_t old_btn=0xffff;
static uint16_t material_tex[TEX_W*TEX_H];
static uint16_t material_tpage=0;

static int player_x=0,player_z=900,facing=1,jump_h=0,jump_v=0;
static int attack_timer=0,attack_connected=0,player_moving=0;
static int cam_x=0,cam_z=120;
static int talked_clockmaker=0,splinters=0,boar_hp=3,area_clear=0;
static uint8_t splinter_taken[3]={0,0,0};
static const int splinter_x[3]={-150,130,-60};
static const int splinter_z[3]={1320,1460,1585};

static int clampi(int v,int lo,int hi){return v<lo?lo:(v>hi?hi:v);}
static int absi(int v){return v<0?-v:v;}
static uint16_t rgb15(int r,int g,int b){return (uint16_t)(((r>>3)&31)|(((g>>3)&31)<<5)|(((b>>3)&31)<<10)|0x8000);}
static uint16_t buttons(void){PADTYPE*p=(PADTYPE*)pad_buffer[0];return p->stat==0?p->btn:0xffff;}
static int pressed(uint16_t n,uint16_t m){return !(n&m)&&(old_btn&m);}

static void make_material_texture(void){
    int x,y;
    RECT r={TEX_X,TEX_Y,TEX_W,TEX_H};
    for(y=0;y<TEX_H;y++) for(x=0;x<TEX_W;x++){
        int checker=((x>>3)^(y>>3))&1;
        int grain=((x*13+y*7+x*y)&7)-3;
        int rr,gg,bb;
        if(y<32&&x<32){ /* Village sandstone/plaster */
            rr=checker?194:164; gg=checker?143:116; bb=checker?91:72;
            if((x%16)==0||((y+5)%19)==0){rr=110;gg=82;bb=68;}
        }else if(y<32){ /* Moko purple cloth/fur */
            rr=checker?154:112; gg=checker?72:48; bb=checker?196:155;
            if((x+y)%23<2){rr=210;gg=98;bb=190;}
        }else if(x<32){ /* Clockmaker brass/blue */
            rr=checker?87:57; gg=checker?129:92; bb=checker?146:119;
            if((x%13)<2){rr=199;gg=160;bb=92;}
        }else{ /* Shadow Boar */
            rr=checker?101:61; gg=checker?47:28; bb=checker?119:80;
            if(((x+y)%17)<2){rr=161;gg=66;bb=155;}
        }
        rr=clampi(rr+grain,0,255); gg=clampi(gg+grain,0,255); bb=clampi(bb+grain,0,255);
        material_tex[y*TEX_W+x]=rgb15(rr,gg,bb);
    }
    LoadImage(&r,(uint32_t*)material_tex);
    DrawSync(0);
    material_tpage=getTPage(2,0,TEX_X,TEX_Y);
}

static void video_init(void){
    ResetGraph(0); InitGeom();
    EnterCriticalSection(); InitPAD(pad_buffer[0],34,pad_buffer[1],34); StartPAD(); ChangeClearPAD(0); ExitCriticalSection();
    SetDefDispEnv(&fb[0].disp,0,0,320,240); SetDefDrawEnv(&fb[0].draw,0,240,320,240);
    SetDefDispEnv(&fb[1].disp,0,240,320,240); SetDefDrawEnv(&fb[1].draw,0,0,320,240);
    fb[0].draw.isbg=fb[1].draw.isbg=1; setRGB0(&fb[0].draw,38,34,58); setRGB0(&fb[1].draw,38,34,58);
    PutDispEnv(&fb[0].disp); PutDrawEnv(&fb[0].draw); SetDispMask(1);
    gte_SetGeomOffset(160,103); gte_SetGeomScreen(215);
    FntLoad(960,0); font_id=FntOpen(10,8,300,34,0,256);
    ClearOTagR(fb[0].ot,OT_SIZE); ClearOTagR(fb[1].ot,OT_SIZE); packet=fb[0].packets;
    make_material_texture();
}

static void frame_begin(void){
    MATRIX view; SVECTOR rot={0,0,0,0}; VECTOR trans;
    RotMatrix(&rot,&view); trans.vx=-cam_x; trans.vy=0; trans.vz=-cam_z; TransMatrix(&view,&trans);
    gte_SetRotMatrix(&view); gte_SetTransMatrix(&view);
}
static void frame_end(void){
    int rendered=active; FntFlush(font_id); DrawSync(0); VSync(0); DrawOTag(fb[rendered].ot+OT_SIZE-1); DrawSync(0);
    PutDispEnv(&fb[rendered^1].disp); active=rendered^1; PutDrawEnv(&fb[active].draw);
    ClearOTagR(fb[active].ot,OT_SIZE); packet=fb[active].packets; tick++;
}

static int project3(short ax,short ay,short az,short bx,short by,short bz,short cx,short cy,short cz,int32_t*s0,int32_t*s1,int32_t*s2,int*depth){
    SVECTOR a={ax,ay,az,0},b={bx,by,bz,0},c={cx,cy,cz,0}; int32_t flag; int zavg;
    if((int)az-cam_z<72||(int)bz-cam_z<72||(int)cz-cam_z<72)return 0;
    zavg=((int)az+(int)bz+(int)cz)/3-cam_z; *depth=clampi(zavg/4,1,OT_SIZE-2);
    gte_ldv3(&a,&b,&c); gte_rtpt(); gte_stsxy0(s0); gte_stsxy1(s1); gte_stsxy2(s2); gte_stflg(&flag);
    return !(flag&0x80000000);
}

static void emit_flat(short ax,short ay,short az,short bx,short by,short bz,short cx,short cy,short cz,int r,int g,int b){
    int32_t s0,s1,s2; int depth; POLY_F3*p;
    if(!project3(ax,ay,az,bx,by,bz,cx,cy,cz,&s0,&s1,&s2,&depth))return;
    p=(POLY_F3*)packet; setPolyF3(p); setRGB0(p,r,g,b);
    setXY3(p,(short)s0,(short)(s0>>16),(short)s1,(short)(s1>>16),(short)s2,(short)(s2>>16));
    addPrim(fb[active].ot+depth,p); packet+=sizeof(POLY_F3);
}

static void emit_tex(short ax,short ay,short az,short bx,short by,short bz,short cx,short cy,short cz,MokoMeshUV ua,MokoMeshUV ub,MokoMeshUV uc,int kind,int shade){
    int32_t s0,s1,s2; int depth; POLY_FT3*p; int u0=0,v0=0;
    if(!project3(ax,ay,az,bx,by,bz,cx,cy,cz,&s0,&s1,&s2,&depth))return;
    if(kind==1)u0=32; else if(kind==2)v0=32; else if(kind==3){u0=32;v0=32;}
    p=(POLY_FT3*)packet; setPolyFT3(p);
    setXY3(p,(short)s0,(short)(s0>>16),(short)s1,(short)(s1>>16),(short)s2,(short)(s2>>16));
    setUV3(p,u0+(ua.u>>1),v0+(ua.v>>1),u0+(ub.u>>1),v0+(ub.v>>1),u0+(uc.u>>1),v0+(uc.v>>1));
    setTPage(p,material_tpage); setRGB0(p,shade,shade,shade); SetShadeTex(p,0);
    addPrim(fb[active].ot+depth,p); packet+=sizeof(POLY_FT3);
}

static void animate_moko(MokoMeshV*p,int anim){
    int phase=(tick/4)&3,gait=phase==1?6:(phase==3?-6:0);
    if(anim==MOKO_IDLE){if(p->y<35&&(p->x<-15||p->x>15))p->y-=((tick/16)&1)*3;if(p->x>45)p->z+=((tick/10)&3)-1;}
    else if(anim==MOKO_RUN){if(p->y>=140&&p->x<0)p->x-=gait;if(p->y>=140&&p->x>0)p->x+=gait;if(p->x>45)p->y+=phase-1;}
    else if(anim==MOKO_JUMP){if(p->y>=140)p->y-=10;if(p->y<35&&(p->x<-15||p->x>15))p->x+=(p->x<0?-4:4);if(p->x>45)p->y-=7;}
    else if(anim==MOKO_ATTACK){if(p->x>45){p->x+=22;p->y-=10;p->z+=10;}if(p->y>=140)p->y-=4;}
}
static void scale_moko(MokoMeshV*p){const int fy=176;p->x=(p->x*2)/3;p->z=(p->z*2)/3;p->y=fy+((p->y-fy)*2)/3;}

static void draw_mesh(const MokoMeshV*v,const MokoMeshUV*uv,const MokoMeshF*f,int n,int ox,int oy,int oz,int mirror,int kind,int anim){
    int i;
    for(i=0;i<n;i++){
        MokoMeshV a=v[f[i].a],b=v[f[i].b],c=v[f[i].c]; int bob=0,shade=kind==1?180:155;
        if(kind==1){animate_moko(&a,anim);animate_moko(&b,anim);animate_moko(&c,anim);scale_moko(&a);scale_moko(&b);scale_moko(&c);if(anim==MOKO_RUN)bob=((tick/4)&1)*2;}
        if((i&3)==1)shade+=14; else if((i&3)==2)shade-=18;
        emit_tex(ox+(mirror?-a.x:a.x),oy+a.y-bob,oz+a.z,ox+(mirror?-b.x:b.x),oy+b.y-bob,oz+b.z,ox+(mirror?-c.x:c.x),oy+c.y-bob,oz+c.z,uv[f[i].ta],uv[f[i].tb],uv[f[i].tc],kind,shade);
    }
}

static void crystal(int x,int y,int z,int p){int h=26+(p&3)*2;emit_flat(x,y-h,z-8,x-12,y,z,x,y+20,z-7,91,218,238);emit_flat(x,y-h,z-8,x,y+20,z-7,x+12,y,z,126,238,248);emit_flat(x-12,y,z,x+12,y,z,x,y+20,z+9,222,157,78);}
static void gate_glow(void){if(area_clear){emit_flat(-38,30,1768,38,30,1768,0,92,1763,101,237,213);emit_flat(-28,40,1766,28,40,1766,0,84,1761,219,186,90);}}

static void update_game(void){
    uint16_t n=buttons(); int sp=7,dx=0,dz=0;
    if(!(n&PAD_LEFT)){player_x-=sp;facing=0;dx=-sp;} if(!(n&PAD_RIGHT)){player_x+=sp;facing=1;dx=sp;}
    if(!(n&PAD_UP)){player_z+=sp;dz=sp;} if(!(n&PAD_DOWN)){player_z-=sp;dz=-sp;} player_moving=dx||dz;
    player_x=clampi(player_x,-245,245); player_z=clampi(player_z,865,1775);
    if(pressed(n,PAD_CROSS)&&jump_h==0)jump_v=18; if(jump_v||jump_h){jump_h+=jump_v;jump_v-=2;if(jump_h<=0){jump_h=0;jump_v=0;}}
    if(pressed(n,PAD_SQUARE)){attack_timer=12;attack_connected=0;} if(attack_timer>0)attack_timer--;
    if(!splinter_taken[0]&&absi(player_x-splinter_x[0])<38&&absi(player_z-splinter_z[0])<44){splinter_taken[0]=1;splinters=1;}
    if(splinter_taken[0]&&!talked_clockmaker&&absi(player_x+105)<82&&absi(player_z-1210)<98)talked_clockmaker=1;
    if(talked_clockmaker){int i;for(i=1;i<3;i++)if(!splinter_taken[i]&&absi(player_x-splinter_x[i])<38&&absi(player_z-splinter_z[i])<44){splinter_taken[i]=1;splinters++;}}
    if(splinters==3&&boar_hp>0&&attack_timer>5&&!attack_connected&&absi(player_x-95)<82&&absi(player_z-1700)<92){boar_hp--;attack_connected=1;player_z-=25;}
    if(boar_hp<=0&&splinters==3&&player_z>1740)area_clear=1;
    {int d=player_x-cam_x;if(absi(d)>24)cam_x+=(d-(d<0?-24:24))/7;}
    {int target=player_z-760,d=target-cam_z;if(absi(d)>18)cam_z+=(d-(d<0?-18:18))/9;}
    old_btn=n;
}

static void draw_scene(void){
    int i,anim=MOKO_IDLE; if(attack_timer>0)anim=MOKO_ATTACK;else if(jump_h>0)anim=MOKO_JUMP;else if(player_moving)anim=MOKO_RUN;
    draw_mesh(village_v,village_uv,village_f,VILLAGE_FACES,0,0,0,0,0,0);
    draw_mesh(moko_v,moko_uv,moko_f,MOKO_FACES,player_x,8-jump_h,player_z,!facing,1,anim);
    draw_mesh(clockmaker_v,clockmaker_uv,clockmaker_f,CLOCKMAKER_FACES,-105,3,1210,0,2,0);
    if(!splinter_taken[0])crystal(splinter_x[0],126,splinter_z[0],tick/6);
    if(talked_clockmaker)for(i=1;i<3;i++)if(!splinter_taken[i])crystal(splinter_x[i],126,splinter_z[i],tick/6+i);
    if(splinters==3&&boar_hp>0)draw_mesh(boar_v,boar_uv,boar_f,BOAR_FACES,95,5-(((tick/6)&1)*3),1700,(tick/40)&1,3,0);
    gate_glow();
    if(attack_timer>0){int tx=player_x+(facing?52:-52),tz=player_z+10;emit_flat(player_x+(facing?28:-28),116-jump_h,player_z-8,tx,104-jump_h,tz,tx,132-jump_h,tz+8,233,92,163);}
}
static void draw_ui(void){
    if(area_clear)FntPrint(font_id,"VILLAGE OF DAWN   AREA CLEAR\nDawn Gate restored");
    else if(!splinter_taken[0])FntPrint(font_id,"VILLAGE OF DAWN   HP 3\nFind the first Time Splinter");
    else if(!talked_clockmaker)FntPrint(font_id,"TIME SPLINTERS 1/3\nBring it to the Clockmaker");
    else if(splinters<3)FntPrint(font_id,"TIME SPLINTERS %d/3\nRecover the remaining fragments",splinters);
    else if(boar_hp>0)FntPrint(font_id,"SHADOW BOAR  HP %d\nSquare: tail strike",boar_hp);
    else FntPrint(font_id,"DAWN GATE OPEN\nWalk through the arch");
}
int main(void){video_init();while(1){update_game();frame_begin();draw_scene();draw_ui();frame_end();}return 0;}
