# MOKO: The Lost Hour

An original PlayStation 1 homebrew adventure built in C with PSn00bSDK.

## Current milestone
MOKO now has a complete five-area playable route: Silent Station, Backward Street, House Without Morning, Clockworks and the Clock Chamber finale. The runtime includes native PS1 controller input, double-buffered GPU rendering, an animated TIM player sprite, room-specific hazards and puzzles, four Memory Shards, four Memory Echoes, checkpoints, score/combo/Focus systems, Memory Dash, dialogue, ending/credits, SPU ambience and sound effects, memory-card save infrastructure, and a 48-event quest/secret-event catalogue.

The Clock Chamber is now skill-based: restoring all four shard sockets begins a stabilization phase and the timer alone is not enough to win. The player must use Memory Dash to raise clock stability while avoiding crossing temporal sweeps; dropping stability extends the encounter and breaks the perfect-chain bonus.

## Controls
- D-pad: move Moko
- CROSS: interact / collect / advance dialogue
- R1: Memory Dash
- START: pause

## Build
GitHub Actions builds the project with PSn00bSDK and mkpsxiso and publishes `MOKO.bin` and `MOKO.cue` as the `MOKO-PS1` artifact.

## Development status
The project compiles to a PS1 disc image in CI. Hardware/emulator gameplay QA, final audio tuning, full quest-world integration, save UI and presentation polish are still active development tasks; a green build should not be treated as proof that every audiovisual or gameplay path has been runtime-tested.
