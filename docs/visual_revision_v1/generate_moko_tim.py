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

def put(frame, x, y, color):
    if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
        pixels[y * width + frame * FRAME_W + x] = color

def box(frame, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(frame, x, y, color)

def draw_moko(frame, step=0, facing_right=True):
    """A deliberately readable 24x32 hero: ears, face, coat, pendant and key-tail.
    The silhouette is original and remains readable on a CRT-sized PS1 frame."""
    violet, shadow, cream, dark = 0x5A7D, 0x294A, 0x6B5F, 0x1C63
    cobalt, gold, glow, pink = 0x34B2, 0x4210, 0x7FFF, 0x4D5A
    bob = 1 if step == 2 else 0
    box(frame, 6, 1-bob, 9, 7-bob, violet); box(frame, 14, 1-bob, 17, 7-bob, violet)
    box(frame, 7, 2-bob, 8, 5-bob, pink); box(frame, 15, 2-bob, 16, 5-bob, pink)
    box(frame, 5, 6-bob, 18, 14-bob, violet); box(frame, 6, 5-bob, 17, 15-bob, violet)
    box(frame, 7, 11-bob, 16, 15-bob, cream)
    if facing_right:
        box(frame, 14, 8-bob, 15, 10-bob, dark); put(frame, 15, 8-bob, glow)
        box(frame, 16, 11-bob, 18, 12-bob, dark)
    else:
        box(frame, 8, 8-bob, 9, 10-bob, dark); put(frame, 8, 8-bob, glow)
        box(frame, 5, 11-bob, 7, 12-bob, dark)
    put(frame, 11, 12-bob, dark); put(frame, 12, 12-bob, dark)
    box(frame, 5, 15-bob, 18, 25-bob, cobalt); box(frame, 7, 16-bob, 16, 25-bob, cobalt)
    box(frame, 11, 16-bob, 13, 19-bob, gold); put(frame, 12, 17-bob, glow)
    box(frame, 3, 17-bob, 6, 23-bob, violet); box(frame, 17, 17-bob, 20, 23-bob, violet)
    box(frame, 3, 22-bob, 6, 24-bob, cream); box(frame, 17, 22-bob, 20, 24-bob, cream)
    if facing_right:
        box(frame, 19, 17-bob, 22, 19-bob, violet); box(frame, 21, 14-bob, 23, 19-bob, violet); box(frame, 21, 13-bob, 23, 15-bob, gold)
    else:
        box(frame, 1, 17-bob, 4, 19-bob, violet); box(frame, 0, 14-bob, 2, 19-bob, violet); box(frame, 0, 13-bob, 2, 15-bob, gold)
    if step == 1:
        box(frame, 6, 25-bob, 10, 29-bob, shadow); box(frame, 14, 26-bob, 18, 30-bob, shadow)
    elif step == 2:
        box(frame, 5, 26-bob, 9, 30-bob, shadow); box(frame, 14, 25-bob, 18, 29-bob, shadow)
    else:
        box(frame, 6, 26-bob, 10, 30-bob, shadow); box(frame, 14, 26-bob, 18, 30-bob, shadow)

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
