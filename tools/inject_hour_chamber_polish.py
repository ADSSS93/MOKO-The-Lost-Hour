import pathlib, subprocess, sys

here = pathlib.Path(__file__).resolve().parent
out = pathlib.Path(sys.argv[2])

subprocess.check_call([sys.executable, str(here / 'inject_hour_chamber_core.py'), sys.argv[1], str(out)])
subprocess.check_call([sys.executable, str(here / 'inject_moko_combat_feedback.py'), str(out), str(out)])
# Keep presentation changes late so later gameplay injectors cannot restore the
# prototype-style station or oversized debug HUD.
subprocess.check_call([sys.executable, str(here / 'inject_commercial_visual_pass.py'), str(out), str(out)])
# Final pass: a self-contained playable minute in Silent Station.
subprocess.check_call([sys.executable, str(here / 'inject_vertical_slice.py'), str(out), str(out)])
