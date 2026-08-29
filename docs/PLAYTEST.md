# MOKO: The Lost Hour — Emulator Playtest Checklist

Use the `MOKO-PS1` GitHub Actions artifact (`MOKO.bin` + `MOKO.cue`) in a PlayStation emulator. Load the CUE file, not the BIN directly.

## Boot
- [ ] BIOS/boot reaches the MOKO title screen.
- [ ] START begins a new game.
- [ ] No black screen, GPU corruption, or crash during the first 60 seconds.

## Moko
- [ ] Moko sprite is visible.
- [ ] Left/right movement uses the correct facing animation.
- [ ] Walking animation changes frames cleanly.
- [ ] R1 Memory Dash moves Moko and consumes Focus.
- [ ] Dash cooldown/focus recovery behave correctly.

## Core route
- [ ] Silent Station can be completed.
- [ ] Backward Street can be reached and completed.
- [ ] House Without Morning can be reached and completed.
- [ ] Clockworks can be reached and completed.
- [ ] Clock Chamber can be reached after four shards.
- [ ] Finale requires active stabilization and can be completed.
- [ ] Ending and credits are reachable.

## Adventure events
- [ ] World event markers appear in their intended rooms.
- [ ] CROSS prompt appears only when an event is available.
- [ ] Locked secret events do not show an interaction prompt.
- [ ] 00:00 Ticket unlocks Platform 13.
- [ ] Platform 13 unlocks Clockwork Cat.
- [ ] Soaked Letter unlocks Walking Lamp.
- [ ] Portrait + Tea chain unlocks Under the Bed.
- [ ] Lunchbox chain unlocks Hidden Bell.
- [ ] EVENT CLEAR notification appears after successful interactions.
- [ ] AP/event completion percentage increases correctly.

## Quest regression
- [ ] The Hidden Minute does not auto-complete.
- [ ] Untouchable Minute does not auto-complete merely from entering an area at full health.
- [ ] Forty Events unlocks at 40 completed events.
- [ ] Nothing Left Behind unlocks at 46 completed events.
- [ ] The Sixtieth Second is only awarded after every other event.

## Audio / stability
- [ ] Room ambience changes without hanging the game.
- [ ] Event/finale sounds do not produce severe clipping or lockups.
- [ ] Pause/resume works repeatedly.
- [ ] Game Over -> retry works.
- [ ] No crash after changing rooms repeatedly for five minutes.

## Save system
Physical Memory Card saving is not considered verified yet. Do not mark it working until a real BIOS/emulator card image can create, reload, and validate the save across a full restart.

## Reporting a failure
Record: emulator + version, BIOS/region if applicable, exact room, exact action, visible result, and whether the issue reproduces after restarting the game.
