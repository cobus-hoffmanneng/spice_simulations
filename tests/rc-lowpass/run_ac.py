"""
Known-good toolchain verification: RC low-pass, .ac sweep, corner-frequency check.

Self-contained AC example (distinct from scripts/run_sim.py, which is the generic
tran runner). Paths resolve relative to THIS file, so it runs from any clone location.

    & "C:\\Tools\\spicelib-venv\\Scripts\\python.exe" tests\\rc-lowpass\\run_ac.py

Expected: simulated corner ~= 1000.03 Hz vs analytic 1/(2*pi*R*C) = 1000.031 Hz,
passband 0 dB, roll-off -20 dB/decade.
"""
import os
import math
import numpy as np
from spicelib import SimRunner, RawRead
from spicelib.log.ltsteps import LTSpiceLogReader
from spicelib.simulators.ltspice_simulator import LTspice   # auto-detects LTspice exe

HERE   = os.path.dirname(os.path.abspath(__file__))
DECK   = os.path.join(HERE, "rc_lowpass.asc")   # run the actual schematic (proves .asc netlists & runs)
OUTDIR = os.path.join(HERE, "simout")           # generated outputs (git-ignored)

R = 1591.5
C = 100e-9
fc_analytic = 1.0 / (2 * math.pi * R * C)

runner = SimRunner(simulator=LTspice, output_folder=OUTDIR)
raw_path, log_path = runner.run_now(DECK)
print("RAW:", raw_path)
print("LOG:", log_path)

raw = RawRead(raw_path)
print("Traces:", raw.get_trace_names())

freq = np.abs(raw.get_trace('frequency').get_wave())      # sweep axis (abs per LTspice sign quirk)
vout = raw.get_trace('V(out)').get_wave()                 # complex phasor
mag  = np.abs(vout)

# sort by frequency just in case
order = np.argsort(freq)
freq = freq[order]
mag  = mag[order]

passband = mag[0]                         # magnitude at 1 Hz (DC-ish passband)
gain_db  = 20.0 * np.log10(mag / passband)
target   = -3.0102999566                  # -3.01 dB

# interpolate corner in log-frequency space where gain crosses -3.01 dB
logf = np.log10(freq)
idx = np.where(gain_db <= target)[0][0]   # first sample past the corner
x0, x1 = logf[idx-1], logf[idx]
y0, y1 = gain_db[idx-1], gain_db[idx]
logfc = x0 + (target - y0) * (x1 - x0) / (y1 - y0)
fc_sim = 10.0 ** logfc

# passband gain (dB) and high-freq roll-off slope (dB/decade) as sanity checks
passband_db = 20.0 * np.log10(passband)
# slope between two points a decade apart well into stopband
f_hi1, f_hi2 = 1e5, 1e6
g1 = np.interp(np.log10(f_hi1), logf, gain_db)
g2 = np.interp(np.log10(f_hi2), logf, gain_db)
slope = (g2 - g1) / (np.log10(f_hi2) - np.log10(f_hi1))

err_pct = 100.0 * (fc_sim - fc_analytic) / fc_analytic

print("\n===== RESULTS =====")
print(f"Analytic fc      : {fc_analytic:.3f} Hz")
print(f"Simulated fc     : {fc_sim:.3f} Hz  (interp of |V(out)| = -3.01 dB, log-f linear)")
print(f"Error            : {err_pct:+.3f} %")
print(f"Passband gain    : {passband_db:+.4f} dB (|Vout|@1Hz = {passband:.6f})")
print(f"Roll-off slope   : {slope:.2f} dB/decade (100k->1MHz)")

try:
    lr = LTSpiceLogReader(log_path)
    names = lr.get_measure_names()
    print("\n.meas from log:")
    for n in names:
        print(f"  {n} = {lr.get_measure_value(n)}")
except Exception as e:
    print("log read note:", e)
