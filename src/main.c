#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <psxgpu.h>
#include <psxgte.h>
#include <psxpad.h>
#include <psxapi.h>
#include <psxetc.h>

#define OT_LEN 8
#define OT_SIZE (1 << OT_LEN)
#define PACKET_LEN 32768
#define SCREEN_W 320
#define SCREEN_H 240

typedef struct {
    DISPENV disp;
    DRAWENV draw;
    uint32_t ot[OT_SIZE];
    char packets[PACKET_LEN];
} DB;

static DB db[2];
static int active = 0;
static char *next_packet;
static char pad_buffer[2][34];
static int font_id;
static int player_x = 150;
static int player_y = 180;

static void init(void) {
    ResetGraph(0);
    InitGeom();

    EnterCriticalSection();
    InitPAD(pad_buffer[0], 34, pad_buffer[1], 34);
    StartPAD();
    ChangeClearPAD(0);
    ExitCriticalSection();

    SetDefDispEnv(&db[0].disp, 0, 0, SCREEN_W, SCREEN_H);
    SetDefDrawEnv(&db[0].draw, 0, SCREEN_H, SCREEN_W, SCREEN_H);
    SetDefDispEnv(&db[1].disp, 0, SCREEN_H, SCREEN_W, SCREEN_H);
    SetDefDrawEnv(&db[1].draw, 0, 0, SCREEN_W, SCREEN_H);

    db[0].draw.isbg = 1;
    db[1].draw.isbg = 1;
    setRGB0(&db[0].draw, 8, 8, 18);
    setRGB0(&db[1].draw, 8, 8, 18);

    PutDispEnv(&db[0].disp);
    PutDrawEnv(&db[0].draw);
    SetDispMask(1);

    FntLoad(960, 0);
    font_id = FntOpen(8, 8, 304, 64, 0, 256);
}

static void rect(int x, int y, int w, int h, int r, int g, int b) {
    TILE *p = (TILE *)next_packet;
    setTile(p);
    setXY0(p, x, y);
    setWH(p, w, h);
    setRGB0(p, r, g, b);
    addPrim(db[active].ot, p);
    next_packet += sizeof(TILE);
}

static void frame(void) {
    DrawSync(0);
    VSync(0);
    PutDispEnv(&db[active].disp);
    PutDrawEnv(&db[active].draw);
    DrawOTag(db[active].ot + OT_SIZE - 1);

    active ^= 1;
    ClearOTagR(db[active].ot, OT_SIZE);
    next_packet = db[active].packets;
}

static void update_player(void) {
    PADTYPE *pad = (PADTYPE *)pad_buffer[0];
    if (pad->stat != 0)
        return;

    if (!(pad->btn & PAD_LEFT))  player_x -= 2;
    if (!(pad->btn & PAD_RIGHT)) player_x += 2;
    if (!(pad->btn & PAD_UP))    player_y -= 2;
    if (!(pad->btn & PAD_DOWN))  player_y += 2;

    if (player_x < 8) player_x = 8;
    if (player_x > 300) player_x = 300;
    if (player_y < 70) player_y = 70;
    if (player_y > 220) player_y = 220;
}

int main(void) {
    int clock = 60 * 60;
    int crystals = 0;

    init();
    ClearOTagR(db[active].ot, OT_SIZE);
    next_packet = db[active].packets;

    while (1) {
        update_player();
        if (clock > 0) clock--;

        rect(0, 64, 320, 176, 12, 14, 28);
        rect(40, 120, 70, 8, 55, 45, 70);
        rect(190, 150, 90, 8, 55, 45, 70);
        rect(player_x, player_y, 12, 18, 220, 190, 120);

        FntPrint(font_id,
            "MOKO: THE LOST HOUR\nTIME %02d:%02d   MEMORY SHARDS %d/4\nD-PAD MOVE\nFind the four memory shards before the hour is lost.",
            clock / 3600, (clock / 60) % 60, crystals);
        FntFlush(font_id);
        frame();
    }

    return 0;
}
