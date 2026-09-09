#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: generate_moko_tim.py OUTPUT")

out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
FRAME_W, FRAME_H, FRAMES = 16, 24, 6
width, height = FRAME_W * FRAMES, FRAME_H
pixels = [0] * (width * height)

# PS1 BGR555 colors
PURPLE = 0x4C5B
PURPLE_DARK = 0x2D35
PURPLE_LIGHT = 0x6D7D
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
    # ears + head silhouette
    put(frame, 3, 1-bob, PURPLE_DARK); put(frame, 4, 0-bob, PURPLE_DARK); put(frame, 5, 2-bob, PURPLE)
    put(frame, 10, 2-bob, PURPLE); put(frame, 11, 0-bob, PURPLE_DARK); put(frame, 12, 1-bob, PURPLE_DARK)
    box(frame, 3, 3-bob, 12, 9-bob, PURPLE)
    box(frame, 4, 4-bob, 11, 8-bob, PURPLE_LIGHT)
    # face
    if facing_right:
        put(frame, 9, 5-bob, WHITE); put(frame, 10, 5-bob, BLACK)
        put(frame, 11, 7-bob, PINK)
    else:
        put(frame, 6, 5-bob, WHITE); put(frame, 5, 5-bob, BLACK)
        put(frame, 4, 7-bob, PINK)
    # body
    box(frame, 3, 9-bob, 12, 18-bob, PURPLE)
    box(frame, 4, 10-bob, 11, 17-bob, PURPLE_DARK)
    # clock on chest
    box(frame, 6, 11-bob, 9, 14-bob, GOLD)
    box(frame, 7, 12-bob, 8, 13-bob, CREAM)
    put(frame, 8, 12-bob, BLACK); put(frame, 8, 13-bob, CYAN)
    # arms + legs
    if step == 1:
        box(frame, 1, 10-bob, 3, 16-bob, PURPLE); box(frame, 12, 11-bob, 14, 17-bob, PURPLE)
        box(frame, 3, 18-bob, 6, 22-bob, PURPLE_DARK); box(frame, 10, 17-bob, 13, 21-bob, PURPLE_DARK)
    elif step == 2:
        box(frame, 1, 11-bob, 3, 17-bob, PURPLE); box(frame, 12, 9-bob, 14, 15-bob, PURPLE)
        box(frame, 2, 17-bob, 5, 21-bob, PURPLE_DARK); box(frame, 9, 18-bob, 12, 22-bob, PURPLE_DARK)
    else:
        box(frame, 1, 10-bob, 3, 16-bob, PURPLE); box(frame, 12, 10-bob, 14, 16-bob, PURPLE)
        box(frame, 3, 18-bob, 6, 22-bob, PURPLE_DARK); box(frame, 9, 18-bob, 12, 22-bob, PURPLE_DARK)
    # clock-hand tail, strongly asymmetric to preserve Moko identity
    if facing_right:
        for k in range(5): put(frame, 13+k//2, 14+k-bob, PINK)
        put(frame, 15, 19-bob, GOLD); put(frame, 14, 18-bob, GOLD)
    else:
        for k in range(5): put(frame, 2-k//2, 14+k-bob, PINK)
        put(frame, 0, 19-bob, GOLD); put(frame, 1, 18-bob, GOLD)

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
