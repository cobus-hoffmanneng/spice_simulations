# Known-good test — RC low-pass, AC corner frequency

The repo's **"does my toolchain still work?"** smoke test. A first-order RC low-pass filter run
through an LTspice `.ac` sweep via `spicelib`, checking the −3 dB corner against the analytical
`fc = 1/(2πRC)`. Built and verified by Nikola; opened and confirmed functional in LTspice by Cobus.

## Circuit
- R1 = **1.5915 kΩ**, C1 = **100 nF** → `fc = 1/(2π·1591.5·100n)` = **1000.031 Hz** (target 1 kHz).
- `.ac dec 100 1 1Meg`, source `V1 in 0 AC 1`, output node `out`.
- Two source forms, both tracked: **`rc_lowpass.asc`** (drawn schematic — cosmetically rough
  layout is a known limitation of programmatic `.asc`; it is functionally correct, don't "fix" it)
  and **`rc_lowpass.cir`** (equivalent hand-written netlist fallback).

## Expected result (known-good)
- Simulated corner ≈ **1000.03 Hz** (matches analytic 1000.031 Hz to ~5 sig figs, error < 0.001 %).
- Passband gain ≈ **0 dB**; high-frequency roll-off ≈ **−20 dB/decade**.

## Reproduce it
```powershell
& "C:\Tools\spicelib-venv\Scripts\python.exe" C:\Simulations\tests\rc-lowpass\run_ac.py
```
`run_ac.py` resolves its paths relative to this folder, so it works from any clone. It runs the
`.asc` (proving programmatic schematic → netlist → sim), parses the `.raw`, interpolates the −3 dB
corner, and reads the `.meas Fc` value back from the `.log`. Generated outputs land in `simout/`
and are git-ignored.

> This is a **toolchain-verification example** (hence `tests/`), not client work — that lives in
> `projects/`. If a new machine's toolchain is healthy, this reproduces the numbers above.
