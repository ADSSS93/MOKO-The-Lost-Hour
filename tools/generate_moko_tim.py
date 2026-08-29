#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: generate_moko_tim.py OUTPUT")

out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
width, height = 16, 24
pixels = []
for y in range(height):
    for x in range(width):
        c = 0x0000
        if 2 <= y <= 9 and 4 <= x <= 11:
            c = 0x5E7F
        if 9 <= y <= 18 and 2 <= x <= 13:
            c = 0x294A
        if 19 <= y <= 22 and ((3 <= x <= 6) or (9 <= x <= 12)):
            c = 0x2529
        if 4 <= y <= 5 and x == 9:
            c = 0xFFFF
        pixels.append(c)

# TIM v0, 16-bit direct color. Place texture at VRAM (448, 0), safely outside
# the two 320x240 framebuffers while remaining on a valid 16-bit texture page.
header = struct.pack('<II', 0x10, 0x02)
image_bytes = b''.join(struct.pack('<H', p) for p in pixels)
block_size = 12 + len(image_bytes)
image = struct.pack('<IHHHH', block_size, 448, 0, width, height) + image_bytes
out.write_bytes(header + image)
print(f"generated {out} ({width}x{height}, {out.stat().st_size} bytes)")
