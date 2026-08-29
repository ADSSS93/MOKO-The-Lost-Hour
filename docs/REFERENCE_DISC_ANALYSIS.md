# Commercial PS1 disc architecture reference

This document records high-level technical observations from a user-supplied, legally owned PS1 disc image. No copyrighted game assets, code, dialogue, level data, or proprietary binary content are copied into MOKO.

## Disc-level observations

- Raw image size: 410,518,080 bytes (~391.5 MiB).
- Raw sector count: 174,540 sectors.
- Sector size: 2352 bytes.
- ISO9660/PlayStation volume signature is present.
- The disc contains a normal PS1 executable/configuration layer plus large data containers and streamed media.

## High-level file organization observed

The filesystem exposes a small set of top-level files while most content is packed into containers. Examples of file roles observed:

- executable / boot configuration
- large DAT/IMG/IDX content containers
- SND and XA audio data
- STR streamed video
- multiple BIN data banks

The important architectural lesson for MOKO is not the exact file names or formats. It is that a commercial-scale PS1 title separates engine code from a much larger content layer and streams/loads content rather than representing nearly the whole game as procedural rectangles and a tiny embedded sprite.

## Implications for MOKO

MOKO should evolve toward this architecture:

1. Keep the executable/engine relatively small.
2. Add a real asset pipeline rather than hard-coding most scenery in `main.c`.
3. Store area backgrounds, sprite sheets, UI art and animation data as generated PS1-ready resources.
4. Separate level definitions from rendering code.
5. Add proper sound/music banks and later streamed media only where useful.
6. Keep original MOKO art, characters, levels, music and mission content. The reference disc is used only to understand platform-scale organization.

## Development target

The goal is not to make the BIN artificially large. The goal is to make the game content-rich enough that disc size grows naturally from original graphics, animation, music, levels and presentation while remaining efficient for original PlayStation hardware.
