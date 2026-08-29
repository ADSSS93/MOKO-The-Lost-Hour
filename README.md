# MOKO: The Lost Hour

An original PlayStation 1 homebrew adventure built in C with PSn00bSDK.

## Current milestone
The repository now contains the native PS1 runtime foundation: double-buffered GPU rendering, controller input, player movement, HUD, countdown mechanic and a first playable room. The project is being expanded into the complete game through successive tested milestones.

## Build
The GitHub Actions workflow builds the project and is intended to publish `MOKO.bin` and `MOKO.cue` as the `MOKO-PS1` artifact.

Toolchain: PSn00bSDK + mkpsxiso (open source).
