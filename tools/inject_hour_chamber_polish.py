import pathlib, subprocess, sys

here = pathlib.Path(__file__).resolve().parent
out = pathlib.Path(sys.argv[2])

subprocess.check_call([sys.executable, str(here / 'inject_hour_chamber_core.py'), sys.argv[1], str(out)])
subprocess.check_call([sys.executable, str(here / 'inject_moko_combat_feedback.py'), str(out), str(out)])
subprocess.check_call([sys.executable, str(here / 'inject_commercial_visual_pass.py'), str(out), str(out)])
subprocess.check_call([sys.executable, str(here / 'inject_vertical_slice.py'), str(out), str(out)])
# Final presentation path: Village of Dawn is rendered through the PS1 GTE
# renderer with low-poly Moko rather than the legacy sprite/background path.
subprocess.check_call([sys.executable, str(here / 'inject_ps1_3d_mode.py'), str(out), str(out)])
subprocess.check_call([sys.executable, str(here / 'inject_village_runtime_cleanup.py'), str(out), str(out)])
