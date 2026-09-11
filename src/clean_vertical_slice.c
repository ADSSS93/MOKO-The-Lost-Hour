#include <stdint.h>
#include <stdio.h>
#include <psxgpu.h>
#include <psxgte.h>
#include <psxpad.h>
#include <psxapi.h>
#include <psxetc.h>
#include <inline_c.h>

#include "moko_model.h"
#include "village_model.h"
#include "clockmaker_model.h"
#include "boar_model.h"

#define OT_LEN 9
#define OT_SIZE (1 << OT_LEN)
#define PACKET_LEN 65536

typedef struct {
    DISPENV disp;
    DRAWENV draw;
    uint32_t ot[OT_SIZE];
    char packets[PACKET_LEN];
} Frame;

static Frame fb[2];
static int active=0;
static char *packet;
static char pad_buffer[2][34];
static uint16_t old_btn=0xffff;
static int font_id;
static int tick=0;

static int player_x=0;
static int player_z=900;
static int facing=1;
static int jump_h=0;
static int jump_v=0;
static int attack_timer=0;
static int cam_x=0;
static int cam_z=120;

static int talked_clockmaker=0;
static int splinters=0;
static uint8_t splinter_taken[3]={0,0,0};
static int boar_hp=3;
static int area_clear=0;

static const int splinter_x[3]={-150,130,-60};
static const int splinter_z[3]={1320,1460,1585};

static int clampi(int v,int lo,int hi){return v<lo?lo:(v>hi?hi:v);}
static int absi(int v){return v<0?-v:v;}

static uint16_t buttons(void){
    PADTYPE *p=(PADTYPE*)pad_buffer[0];
    return p->stat==0?p->btn:0xffff;
}
static int pressed(uint16_t now,uint16_t mask){return !(now&mask)&&(old_btn&mask);}

static void video_init(void){
    ResetGraph(0);
    InitGeom();
    EnterCriticalSection();
    InitPAD(pad_buffer[0],34,pad_buffer[1],34);
    StartPAD();
    ChangeClearPAD(0);
    ExitCriticalSection();

    SetDefDispEnv(&fb[0].disp,0,0,320,240);
    SetDefDrawEnv(&fb[0].draw,0,240,320,240);
    SetDefDispEnv(&fb[1].disp,0,240,320,240);
    SetDefDrawEnv(&fb[1].draw,0,0,320,240);
    fb[0].draw.isbg=fb[1].draw.isbg=1;
    setRGB0(&fb[0].draw,44,38,63);
    setRGB0(&fb[1].draw,44,38,63);
    PutDispEnv(&fb[0].disp);
    PutDrawEnv(&fb[0].draw);
    SetDispMask(1);

    gte_SetGeomOffset(160,103);
    gte_SetGeomScreen(225);
    FntLoad(960,0);
    font_id=FntOpen(10,8,300,34,0,256);
    ClearOTagR(fb[0].ot,OT_SIZE);
    ClearOTagR(fb[1].ot,OT_SIZE);
    packet=fb[0].packets;
}

static void frame_begin(void){
    MATRIX view;
    SVECTOR rot={0,0,0,0};
    VECTOR trans;
    RotMatrix(&rot,&view);
    trans.vx=-cam_x;
    trans.vy=0;
    trans.vz=-cam_z;
    TransMatrix(&view,&trans);
    gte_SetRotMatrix(&view);
    gte_SetTransMatrix(&view);
}

static void frame_end(void){
    int rendered=active;
    FntFlush(font_id);
    DrawSync(0);
    VSync(0);
    DrawOTag(fb[rendered].ot+OT_SIZE-1);
    DrawSync(0);
    PutDispEnv(&fb[rendered^1].disp);
    active=rendered^1;
    PutDrawEnv(&fb[active].draw);
    ClearOTagR(fb[active].ot,OT_SIZE);
    packet=fb[active].packets;
    tick++;
}

static void face_color(int kind,int face,int *r,int *g,int *b){
    if(kind==0){
        if(face<6){*r=150+(face&1)*10;*g=116+(face&1)*6;*b=76;return;}
        if((face>=14&&face<18)||(face>=26&&face<30)||(face>=36&&face<40)||(face>=46&&face<50)||face>=64){
            *r=105+(face&1)*15;*g=51;*b=82+(face&2)*8;return;
        }
        if(face>=56&&face<64){*r=91;*g=79+(face&1)*10;*b=82;return;}
        *r=126+(face%3)*9;*g=94+(face%2)*8;*b=76+(face%4)*4;return;
    }
    if(kind==1){
        if(face<10){*r=106;*g=54;*b=156;}
        else if(face<21){*r=151;*g=81;*b=197;}
        else if(face<23){*r=92;*g=39;*b=137;}
        else if(face<31){*r=74;*g=40;*b=112;}
        else if(face<35){*r=218;*g=184;*b=205;}
        else if(face<37){*r=211;*g=171;*b=71;}
        else {*r=205;*g=65;*b=139;}
        return;
    }
    if(kind==2){
        if(face<8){*r=62;*g=101;*b=126;}
        else if(face<15){*r=188;*g=153;*b=119;}
        else if(face<20){*r=57;*g=52;*b=69;}
        else {*r=107;*g=63;*b=91;}
        return;
    }
    if(face<10){*r=68;*g=33;*b=94;}
    else if(face<17){*r=121;*g=52;*b=130;}
    else if(face<19){*r=224;*g=190;*b=116;}
    else {*r=45;*g=28;*b=60;}
}

static void emit_triangle(short ax,short ay,short az,short bx,short by,short bz,short cx,short cy,short cz,int r,int g,int b){
    POLY_F3 *p=(POLY_F3*)packet;
    SVECTOR a={ax,ay,az,0},bb={bx,by,bz,0},c={cx,cy,cz,0};
    int32_t s0,s1,s2,flag;
    int zavg=((int)az+(int)bz+(int)cz)/3-cam_z;
    int depth=clampi(zavg/4,1,OT_SIZE-2);
    setPolyF3(p);
    setRGB0(p,r,g,b);
    gte_ldv3(&a,&bb,&c);
    gte_rtpt();
    gte_stsxy0(&s0); gte_stsxy1(&s1); gte_stsxy2(&s2); gte_stflg(&flag);
    if(!(flag&0x80000000)){
        setXY3(p,(short)s0,(short)(s0>>16),(short)s1,(short)(s1>>16),(short)s2,(short)(s2>>16));
        addPrim(fb[active].ot+depth,p);
        packet+=sizeof(POLY_F3);
    }
}

static void draw_mesh(const MokoMeshV *v,const MokoMeshF *f,int face_count,int ox,int oy,int oz,int mirror,int kind,int anim){
    int i;
    for(i=0;i<face_count;i++){
        MokoMeshV aa=v[f[i].a],bb=v[f[i].b],cc=v[f[i].c];
        int r,g,b;
        int step=(anim==1)?(((tick/5)&3)==1?5:(((tick/5)&3)==3?-5:0)):0;
        int bob=(anim==1)?((tick/6)&1)*2:0;
        if(kind==1){
            if(f[i].a>=22&&f[i].a<=29) aa.x+=(aa.x<0?-step:step);
            if(f[i].b>=22&&f[i].b<=29) bb.x+=(bb.x<0?-step:step);
            if(f[i].c>=22&&f[i].c<=29) cc.x+=(cc.x<0?-step:step);
            if(f[i].a>=46) aa.y+=((tick/5)&3)-1;
            if(f[i].b>=46) bb.y+=((tick/5)&3)-1;
            if(f[i].c>=46) cc.y+=((tick/5)&3)-1;
        }
        face_color(kind,i,&r,&g,&b);
        emit_triangle(
            ox+(mirror?-aa.x:aa.x),oy+aa.y-bob,oz+aa.z,
            ox+(mirror?-bb.x:bb.x),oy+bb.y-bob,oz+bb.z,
            ox+(mirror?-cc.x:cc.x),oy+cc.y-bob,oz+cc.z,
            r,g,b);
    }
}

static void draw_crystal(int x,int y,int z,int pulse){
    int h=26+(pulse&3)*2;
    emit_triangle(x,y-h,z-8,x-12,y,z,x,y+20,z-7,91,218,238);
    emit_triangle(x,y-h,z-8,x,y+20,z-7,x+12,y,z,126,238,248);
    emit_triangle(x-12,y,z,x+12,y,z,x,y+20,z+9,222,157,78);
    emit_triangle(x-12,y,z,x,y+20,z+9,x,y-h,z-8,69,166,205);
}

static void draw_gate_glow(void){
    if(!area_clear)return;
    emit_triangle(-38,30,1660,38,30,1660,0,92,1655,101,237,213);
    emit_triangle(-28,40,1658,28,40,1658,0,84,1653,219,186,90);
}

static void update_game(void){
    uint16_t now=buttons();
    int speed=7;
    if(!(now&PAD_LEFT)){player_x-=speed;facing=0;}
    if(!(now&PAD_RIGHT)){player_x+=speed;facing=1;}
    if(!(now&PAD_UP)) player_z+=speed;
    if(!(now&PAD_DOWN)) player_z-=speed;
    player_x=clampi(player_x,-245,245);
    player_z=clampi(player_z,865,1775);

    if(pressed(now,PAD_CROSS)&&jump_h==0) jump_v=18;
    if(jump_v||jump_h){
        jump_h+=jump_v;
        jump_v-=2;
        if(jump_h<=0){jump_h=0;jump_v=0;}
    }
    if(pressed(now,PAD_SQUARE))attack_timer=12;
    if(attack_timer>0)attack_timer--;

    if(!talked_clockmaker && absi(player_x+105)<75 && absi(player_z-1210)<90 && pressed(now,PAD_CIRCLE)) talked_clockmaker=1;
    if(talked_clockmaker){
        int i;
        for(i=0;i<3;i++) if(!splinter_taken[i] && absi(player_x-splinter_x[i])<34 && absi(player_z-splinter_z[i])<38){
            splinter_taken[i]=1;
            splinters++;
        }
    }
    if(splinters==3 && boar_hp>0 && attack_timer>5 && absi(player_x-95)<82 && absi(player_z-1700)<92){
        boar_hp--;
        player_z-=25;
    }
    if(boar_hp<=0 && splinters==3 && player_z>1740) area_clear=1;

    cam_x+=(player_x-cam_x)/10;
    {
        int target_z=player_z-760;
        cam_z+=(target_z-cam_z)/12;
    }
    old_btn=now;
}

static void draw_scene(void){
    int i;
    draw_mesh(village_v,village_f,VILLAGE_FACES,0,0,0,0,0,0);
    draw_mesh(moko_v,moko_f,MOKO_FACES,player_x,8-jump_h,player_z,!facing,1,1);
    draw_mesh(clockmaker_v,clockmaker_f,CLOCKMAKER_FACES,-105,3,1210,0,2,0);
    if(talked_clockmaker){
        for(i=0;i<3;i++) if(!splinter_taken[i]) draw_crystal(splinter_x[i],126,splinter_z[i],tick/6+i);
    }
    if(splinters==3 && boar_hp>0){
        int bob=((tick/6)&1)*3;
        draw_mesh(boar_v,boar_f,BOAR_FACES,95,5-bob,1700,(tick/40)&1,3,0);
    }
    draw_gate_glow();
    if(attack_timer>0){
        int tx=player_x+(facing?65:-65);
        int tz=player_z+10;
        emit_triangle(player_x+(facing?30:-30),95-jump_h,player_z-8,tx,82-jump_h,tz,tx,122-jump_h,tz+8,233,92,163);
    }
}

static void draw_ui(void){
    if(area_clear) FntPrint(font_id,"VILLAGE OF DAWN   AREA CLEAR\nDawn Gate restored");
    else if(!talked_clockmaker) FntPrint(font_id,"VILLAGE OF DAWN   HP 3\nFind the Clockmaker - O interact");
    else if(splinters<3) FntPrint(font_id,"TIME SPLINTERS %d/3\nRecover the blue fragments",splinters);
    else if(boar_hp>0) FntPrint(font_id,"SHADOW BOAR  HP %d\nSquare: tail strike",boar_hp);
    else FntPrint(font_id,"DAWN GATE OPEN\nWalk through the arch");
}

int main(void){
    video_init();
    while(1){
        update_game();
        frame_begin();
        draw_scene();
        draw_ui();
        frame_end();
    }
    return 0;
}
