#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: generate_moko_tim.py OUTPUT")

out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
FRAME_W, FRAME_H, FRAMES = 24, 32, 6
width, height = FRAME_W * FRAMES, FRAME_H
pixels = [0] * (width * height)

# PS1 BGR555 palette. Keep the sprite deliberately limited and high-contrast so
# Moko reads as a mascot on CRT-scale output instead of dissolving into scenery.
PURPLE = 0x5C7D
PURPLE_DARK = 0x3518
PURPLE_SHADOW = 0x28D3
PURPLE_LIGHT = 0x71BF
LILAC = 0x69BE
PINK = 0x5DDF
CREAM = 0x6F7B
WHITE = 0x7FFF
BLACK = 0x0842
GOLD = 0x2B3F
CYAN = 0x7E60


def put(frame, x, y, color):
    if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
        pixels[y * width + frame * FRAME_W + x] = color


def box(frame, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(frame, x, y, color)


def line(frame, x0, y0, x1, y1, color):
    dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        put(frame, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def draw_moko(frame, step=0, facing_right=True):
    bob = 1 if step == 2 else 0
    lean = 1 if step == 1 else 0

    # Huge triangular ears are the first silhouette cue: this must read CAT at
    # thumbnail size before the player notices any costume details.
    line(frame, 4, 7-bob, 7, 1-bob, PURPLE_DARK)
    line(frame, 7, 1-bob, 10, 7-bob, PURPLE_DARK)
    line(frame, 14, 7-bob, 17, 1-bob, PURPLE_DARK)
    line(frame, 17, 1-bob, 20, 7-bob, PURPLE_DARK)
    box(frame, 6, 3-bob, 8, 6-bob, PINK)
    box(frame, 16, 3-bob, 18, 6-bob, PINK)

    # Rounded-ish feline head made from stepped pixel planes, with cheek tufts.
    box(frame, 5, 6-bob, 19, 12-bob, PURPLE)
    box(frame, 4, 8-bob, 20, 11-bob, PURPLE)
    put(frame, 3, 10-bob, PURPLE_LIGHT); put(frame, 21, 10-bob, PURPLE_LIGHT)
    box(frame, 7, 7-bob, 17, 9-bob, PURPLE_LIGHT)
    box(frame, 8, 10-bob, 17, 13-bob, LILAC)

    # Two bright eyes + muzzle/nose. Both eyes remain visible so Moko does not
    # read as a cyclopean robot when moving sideways.
    if facing_right:
        box(frame, 9, 8-bob, 10, 9-bob, WHITE); put(frame, 10, 9-bob, BLACK)
        box(frame, 15, 8-bob, 16, 9-bob, WHITE); put(frame, 16, 9-bob, BLACK)
        put(frame, 17, 11-bob, PINK)
        line(frame, 18, 12-bob, 22, 11-bob, WHITE); line(frame, 18, 13-bob, 22, 14-bob, WHITE)
    else:
        box(frame, 8, 8-bob, 9, 9-bob, WHITE); put(frame, 8, 9-bob, BLACK)
        box(frame, 14, 8-bob, 15, 9-bob, WHITE); put(frame, 14, 9-bob, BLACK)
        put(frame, 6, 11-bob, PINK)
        line(frame, 5, 12-bob, 1, 11-bob, WHITE); line(frame, 5, 13-bob, 1, 14-bob, WHITE)

    # Compact pear-shaped torso. Narrow shoulders + wider haunches remove the
    # old rectangular humanoid/robot silhouette.
    box(frame, 8-lean, 14-bob, 16-lean, 17-bob, PURPLE)
    box(frame, 6-lean, 17-bob, 18-lean, 23-bob, PURPLE)
    box(frame, 8-lean, 18-bob, 16-lean, 23-bob, PURPLE_DARK)
    put(frame, 5-lean, 21-bob, PURPLE_LIGHT); put(frame, 19-lean, 21-bob, PURPLE_LIGHT)

    # Signature chest clock: oversized so the character concept survives 320x240.
    box(frame, 9-lean, 17-bob, 15-lean, 22-bob, GOLD)
    box(frame, 10-lean, 18-bob, 14-lean, 21-bob, CREAM)
    put(frame, 12-lean, 18-bob, BLACK); put(frame, 12-lean, 19-bob, CYAN); put(frame, 13-lean, 20-bob, CYAN)

    # Cat forepaws and digitigrade rear legs. The walk cycle alternates paw reach
    # and haunch compression rather than swinging long human arms.
    if step == 1:
        box(frame, 4, 16-bob, 7, 21-bob, PURPLE); box(frame, 3, 21-bob, 7, 23-bob, PURPLE_LIGHT)
        box(frame, 17, 17-bob, 20, 22-bob, PURPLE); box(frame, 17, 22-bob, 21, 24-bob, PURPLE_LIGHT)
        box(frame, 6, 23-bob, 10, 27-bob, PURPLE_SHADOW); box(frame, 4, 27-bob, 10, 30-bob, PURPLE_DARK)
        box(frame, 14, 23-bob, 18, 26-bob, PURPLE_SHADOW); box(frame, 14, 26-bob, 20, 29-bob, PURPLE_DARK)
    elif step == 2:
        box(frame, 4, 17-bob, 7, 22-bob, PURPLE); box(frame, 3, 22-bob, 7, 24-bob, PURPLE_LIGHT)
        box(frame, 17, 15-bob, 20, 21-bob, PURPLE); box(frame, 17, 21-bob, 21, 23-bob, PURPLE_LIGHT)
        box(frame, 5, 23-bob, 9, 26-bob, PURPLE_SHADOW); box(frame, 4, 26-bob, 10, 29-bob, PURPLE_DARK)
        box(frame, 14, 23-bob, 18, 27-bob, PURPLE_SHADOW); box(frame, 13, 27-bob, 20, 30-bob, PURPLE_DARK)
    else:
        box(frame, 4, 16-bob, 7, 22-bob, PURPLE); box(frame, 3, 22-bob, 7, 24-bob, PURPLE_LIGHT)
        box(frame, 17, 16-bob, 20, 22-bob, PURPLE); box(frame, 17, 22-bob, 21, 24-bob, PURPLE_LIGHT)
        box(frame, 6, 23-bob, 10, 28-bob, PURPLE_SHADOW); box(frame, 4, 28-bob, 10, 30-bob, PURPLE_DARK)
        box(frame, 14, 23-bob, 18, 28-bob, PURPLE_SHADOW); box(frame, 14, 28-bob, 20, 30-bob, PURPLE_DARK)

    # Long segmented clock-hand tail. It exits the body horizontally, curls up,
    # then ends in a gold pointer so it is unmistakable in motion.
    if facing_right:
        line(frame, 18, 20-bob, 22, 22-bob, PINK)
        line(frame, 22, 22-bob, 22, 16-bob-(step==2), PINK)
        line(frame, 22, 16-bob-(step==2), 20, 13-bob, PINK)
        put(frame, 20, 12-bob, GOLD); put(frame, 21, 13-bob, GOLD); put(frame, 19, 13-bob, GOLD)
    else:
        line(frame, 6, 20-bob, 1, 22-bob, PINK)
        line(frame, 1, 22-bob, 1, 16-bob-(step==2), PINK)
        line(frame, 1, 16-bob-(step==2), 3, 13-bob, PINK)
        put(frame, 3, 12-bob, GOLD); put(frame, 2, 13-bob, GOLD); put(frame, 4, 13-bob, GOLD)


for base, right in ((0, True), (3, False)):
    draw_moko(base, 0, right)
    draw_moko(base + 1, 1, right)
    draw_moko(base + 2, 2, right)

header = struct.pack('<II', 0x10, 0x02)
image_bytes = b''.join(struct.pack('<H', p) for p in pixels)
block_size = 12 + len(image_bytes)
image = struct.pack('<IHHHH', block_size, 448, 0, width, height) + image_bytes
out.write_bytes(header + image)
print(f"generated {out} ({width}x{height}, {FRAMES} frames, {out.stat().st_size} bytes) MOKO VISUAL REV 282")
