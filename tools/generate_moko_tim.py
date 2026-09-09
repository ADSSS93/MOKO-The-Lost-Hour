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

# PS1 BGR555 colors
PURPLE = 0x5C7D
PURPLE_DARK = 0x3518
PURPLE_LIGHT = 0x71BF
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


def draw_moko(frame, step=0, facing_right=True):
    bob = 1 if step == 2 else 0

    # Large unmistakable cat ears and head.
    for i in range(5):
        box(frame, 3+i, 4-i-bob, 5+i, 6-bob, PURPLE_DARK)
        box(frame, 16-i, 6-i-bob, 18-i, 6-bob, PURPLE_DARK)
    box(frame, 4, 5-bob, 19, 14-bob, PURPLE)
    box(frame, 6, 7-bob, 17, 12-bob, PURPLE_LIGHT)

    # Face: bright eyes and pink nose readable on a CRT/emulator.
    if facing_right:
        box(frame, 13, 8-bob, 15, 10-bob, WHITE); put(frame, 15, 9-bob, BLACK)
        put(frame, 17, 11-bob, PINK)
    else:
        box(frame, 8, 8-bob, 10, 10-bob, WHITE); put(frame, 8, 9-bob, BLACK)
        put(frame, 6, 11-bob, PINK)

    # Body and belly.
    box(frame, 5, 14-bob, 18, 25-bob, PURPLE)
    box(frame, 7, 15-bob, 16, 24-bob, PURPLE_DARK)

    # Oversized chest clock: gold rim, cream face, cyan hand.
    box(frame, 9, 16-bob, 14, 21-bob, GOLD)
    box(frame, 10, 17-bob, 13, 20-bob, CREAM)
    put(frame, 12, 18-bob, BLACK); put(frame, 12, 19-bob, CYAN); put(frame, 13, 19-bob, CYAN)

    # Arms/legs animate with a chunky PS1 mascot stance.
    if step == 1:
        box(frame, 2, 15-bob, 5, 23-bob, PURPLE)
        box(frame, 18, 17-bob, 21, 24-bob, PURPLE)
        box(frame, 5, 25-bob, 9, 30-bob, PURPLE_DARK)
        box(frame, 15, 24-bob, 19, 29-bob, PURPLE_DARK)
    elif step == 2:
        box(frame, 2, 17-bob, 5, 24-bob, PURPLE)
        box(frame, 18, 14-bob, 21, 22-bob, PURPLE)
        box(frame, 4, 24-bob, 8, 29-bob, PURPLE_DARK)
        box(frame, 14, 25-bob, 18, 30-bob, PURPLE_DARK)
    else:
        box(frame, 2, 16-bob, 5, 23-bob, PURPLE)
        box(frame, 18, 16-bob, 21, 23-bob, PURPLE)
        box(frame, 5, 25-bob, 9, 30-bob, PURPLE_DARK)
        box(frame, 14, 25-bob, 18, 30-bob, PURPLE_DARK)

    # Signature clock-hand tail, long and bright.
    if facing_right:
        for k in range(8):
            put(frame, 19 + min(4, k//2), 18+k-bob, PINK)
        box(frame, 21, 25-bob, 23, 27-bob, GOLD)
        put(frame, 23, 24-bob, GOLD)
    else:
        for k in range(8):
            put(frame, 4 - min(4, k//2), 18+k-bob, PINK)
        box(frame, 0, 25-bob, 2, 27-bob, GOLD)
        put(frame, 0, 24-bob, GOLD)


for base, right in ((0, True), (3, False)):
    draw_moko(base, 0, right)
    draw_moko(base + 1, 1, right)
    draw_moko(base + 2, 2, right)

header = struct.pack('<II', 0x10, 0x02)
image_bytes = b''.join(struct.pack('<H', p) for p in pixels)
block_size = 12 + len(image_bytes)
image = struct.pack('<IHHHH', block_size, 448, 0, width, height) + image_bytes
out.write_bytes(header + image)
print(f"generated {out} ({width}x{height}, {FRAMES} frames, {out.stat().st_size} bytes)")
