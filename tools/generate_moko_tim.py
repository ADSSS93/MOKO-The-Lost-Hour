#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: generate_moko_tim.py OUTPUT")

out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
FRAME_W, FRAME_H, FRAMES = 16, 24, 4
width, height = FRAME_W * FRAMES, FRAME_H
pixels = [0] * (width * height)

def put(frame, x, y, color):
    if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
        pixels[y * width + frame * FRAME_W + x] = color

def box(frame, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(frame, x, y, color)

def draw_moko(frame, step=0, echo=False):
    skin = 0x5E7F if not echo else 0x7FFF
    coat = 0x294A if not echo else 0x56B5
    dark = 0x2529
    accent = 0x7C1F if echo else 0x4210
    bob = 1 if step == 2 else 0
    # Hair/head silhouette and face.
    box(frame, 4, 2-bob, 11, 9-bob, skin)
    box(frame, 3, 3-bob, 5, 7-bob, dark)
    put(frame, 9, 5-bob, 0x7FFF)
    put(frame, 10, 5-bob, dark)
    # Coat/body with a brighter memory-hour clasp.
    box(frame, 2, 9-bob, 13, 18-bob, coat)
    box(frame, 4, 10-bob, 5, 16-bob, accent)
    put(frame, 8, 12-bob, 0x7FFF)
    # Arms shift between walk frames.
    if step == 1:
        box(frame, 0, 11-bob, 2, 17-bob, coat); box(frame, 13, 9-bob, 15, 15-bob, coat)
    elif step == 2:
        box(frame, 0, 9-bob, 2, 15-bob, coat); box(frame, 13, 11-bob, 15, 17-bob, coat)
    else:
        box(frame, 1, 10-bob, 2, 16-bob, coat); box(frame, 13, 10-bob, 14, 16-bob, coat)
    # Legs: idle, two alternating walk poses, then echo/interaction stance.
    if step == 1:
        box(frame, 3, 19-bob, 6, 22-bob, dark); box(frame, 10, 18-bob, 13, 21-bob, dark)
    elif step == 2:
        box(frame, 2, 18-bob, 5, 21-bob, dark); box(frame, 9, 19-bob, 12, 22-bob, dark)
    else:
        box(frame, 3, 19-bob, 6, 22-bob, dark); box(frame, 9, 19-bob, 12, 22-bob, dark)
    if echo:
        put(frame, 1, 4, 0x7FFF); put(frame, 14, 7, 0x7FFF); put(frame, 13, 2, 0x7FFF)

draw_moko(0, 0)
draw_moko(1, 1)
draw_moko(2, 2)
draw_moko(3, 0, True)

# TIM v0, 16-bit direct color. 64x24 contains four 16x24 frames.
# VRAM x=448 keeps it away from both framebuffers and on one texture page.
header = struct.pack('<II', 0x10, 0x02)
image_bytes = b''.join(struct.pack('<H', p) for p in pixels)
block_size = 12 + len(image_bytes)
image = struct.pack('<IHHHH', block_size, 448, 0, width, height) + image_bytes
out.write_bytes(header + image)
print(f"generated {out} ({width}x{height}, {FRAMES} frames, {out.stat().st_size} bytes)")
