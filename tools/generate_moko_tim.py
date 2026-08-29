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

def put(frame, x, y, color):
    if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
        pixels[y * width + frame * FRAME_W + x] = color

def box(frame, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(frame, x, y, color)

def draw_moko(frame, step=0, facing_right=True):
    skin, coat, dark, accent = 0x5E7F, 0x294A, 0x2529, 0x4210
    bob = 1 if step == 2 else 0
    box(frame, 4, 2-bob, 11, 9-bob, skin)
    if facing_right:
        box(frame, 3, 3-bob, 5, 7-bob, dark)
        put(frame, 9, 5-bob, 0x7FFF); put(frame, 10, 5-bob, dark)
    else:
        box(frame, 10, 3-bob, 12, 7-bob, dark)
        put(frame, 6, 5-bob, 0x7FFF); put(frame, 5, 5-bob, dark)
    box(frame, 2, 9-bob, 13, 18-bob, coat)
    if facing_right: box(frame, 4, 10-bob, 5, 16-bob, accent)
    else: box(frame, 10, 10-bob, 11, 16-bob, accent)
    put(frame, 8, 12-bob, 0x7FFF)
    if step == 1:
        box(frame, 0, 11-bob, 2, 17-bob, coat); box(frame, 13, 9-bob, 15, 15-bob, coat)
        box(frame, 3, 19-bob, 6, 22-bob, dark); box(frame, 10, 18-bob, 13, 21-bob, dark)
    elif step == 2:
        box(frame, 0, 9-bob, 2, 15-bob, coat); box(frame, 13, 11-bob, 15, 17-bob, coat)
        box(frame, 2, 18-bob, 5, 21-bob, dark); box(frame, 9, 19-bob, 12, 22-bob, dark)
    else:
        box(frame, 1, 10-bob, 2, 16-bob, coat); box(frame, 13, 10-bob, 14, 16-bob, coat)
        box(frame, 3, 19-bob, 6, 22-bob, dark); box(frame, 9, 19-bob, 12, 22-bob, dark)

for base, right in ((0, True), (3, False)):
    draw_moko(base, 0, right)
    draw_moko(base + 1, 1, right)
    draw_moko(base + 2, 2, right)

# TIM v0, 16-bit direct color. 96x24 contains right/left idle + two walk frames.
# VRAM x=448 keeps the sheet on a single 16-bit texture page.
header = struct.pack('<II', 0x10, 0x02)
image_bytes = b''.join(struct.pack('<H', p) for p in pixels)
block_size = 12 + len(image_bytes)
image = struct.pack('<IHHHH', block_size, 448, 0, width, height) + image_bytes
out.write_bytes(header + image)
print(f"generated {out} ({width}x{height}, {FRAMES} frames, {out.stat().st_size} bytes)")
