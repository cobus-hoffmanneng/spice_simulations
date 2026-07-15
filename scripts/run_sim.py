"""
Portable spicelib runner for the PKA Simulation repo.

The minimal loop Nikola uses: netlist (.cir) -> run LTspice headless -> parse .raw -> get numbers.

Paths are resolved portably (no hard-coded username):
  * LTspice exe   -> spicelib auto-detects it from %LOCALAPPDATA%\\Programs\\ADI\\LTspice\\.
  * Netlist/out   -> relative to this repo, so it works from any clone location / machine.

Run it with the dedicated venv's python (see README.md / integration note):
    & "C:\\Tools\\spicelib-venv\\Scripts\\python.exe" scripts\\run_sim.py <path-to-deck.cir>

If no deck is given it runs scripts/_selftest.cir (an RC low-pass) as a smoke test.
"""
import os
import sys
import numpy as np
from spicelib import SimRunner, RawRead

# spicelib auto-detects the installed LTspice exe from %LOCALAPPDATA% - no hard-coded path.
from spicelib.simulators.ltspice_simulator import LTspice

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(netlist_path, out_dir=None):
    """Run a self-contained .cir headless and return the parsed RawRead object."""
    netlist_path = os.path.abspath(netlist_path)
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(netlist_path), "simout")
    os.makedirs(out_dir, exist_ok=True)

    print("LTspice exe:", LTspice.spice_exe)
    runner = SimRunner(simulator=LTspice, output_folder=out_dir)
    raw_path, log_path = runner.run_now(netlist_path)  # launches LTspice -b, blocks till done
    print("RAW:", raw_path)
    print("LOG:", log_path)
    return RawRead(raw_path), log_path


def main():
    deck = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "scripts", "_selftest.cir")
    raw, _log = run(deck)

    print("Traces:", raw.get_trace_names())
    # Example extraction: if this is the RC self-test, check V(out) reaches ~63% at t=tau=1ms.
    if "V(out)" in raw.get_trace_names() and "time" in raw.get_trace_names():
        t = np.abs(raw.get_trace("time").get_wave())        # time can be negatively signed - abs it
        vout = np.real(raw.get_trace("V(out)").get_wave())
        idx = int(np.argmin(np.abs(t - 1e-3)))
        print(f"V(out) @ t=1ms = {vout[idx]:.4f} V  (RC self-test expects ~0.6321 V)")
        print(f"V(out) final   = {vout[-1]:.4f} V")


if __name__ == "__main__":
    main()
