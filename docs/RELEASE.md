# MOKO: The Lost Hour — Release Candidate Gate

A build is a release candidate only when all of the following are true.

## Automated gate
- PSn00bSDK build succeeds.
- `MOKO.bin` and `MOKO.cue` are produced by GitHub Actions.
- The disc artifact is retained for emulator testing.

## Runtime gate
- Disc boots to the title screen in a PS1 emulator.
- D-pad movement, CROSS interaction, START pause and R1 Memory Dash work.
- Moko renders facing left/right and walk animation is stable.
- Silent Station, Backward Street, House Without Morning, Clockworks and Clock Chamber are reachable.
- Four Memory Shards can be collected and the Clock Chamber can be completed.
- Memory Echoes and physical world events can be collected without softlocks.
- Locked secret events do not render an interaction prompt before their prerequisite is complete.
- Event completion/AP/progress UI remains readable.
- Game Over/retry, ending and credits are reachable.
- Audio does not hang or crash gameplay.

## Completion policy
A green compile is not runtime proof. The project must not be labelled final until the runtime gate has been executed against the generated BIN/CUE and blocking defects have been fixed.

## Current known release blocker
The memory-card module compiles but has not been runtime-verified on an emulator or real card. Persistent saving must not be advertised as working until that test passes.
