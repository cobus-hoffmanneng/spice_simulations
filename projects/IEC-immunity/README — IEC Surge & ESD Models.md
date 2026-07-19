# IEC Surge & ESD LTspice Models — usage note

Reusable LTspice generators for **IEC 61000-4-5 (surge / combination wave)** and
**IEC 61000-4-2 (ESD, contact discharge)**, plus runnable demo decks. Drop a
generator onto (or `.include` into) your own design and check the design survives.

> **These are idealised sources, not a compliance test.** They verify clamp
> behaviour and relative robustness / energy. Real results are dominated by DUT
> layout parasitics and TVS model fidelity — see **Caveats**.

---

## Files

| File | What it is |
|---|---|
| `models/IEC61000-4-5_Surge_CWG.sub` | Surge combination-wave generator `.subckt` (RLC). Ports `out gnd`. Params `VPEAK`, `TSTART`. |
| `models/IEC61000-4-5_Surge_CWG.asy` | LTspice symbol for the surge generator. |
| `models/IEC61000-4-2_ESD.sub` | ESD contact-discharge generator `.subckt` (two-Heidler current source). Ports `tip gnd`. Params `KV`, `TSTART`. |
| `models/IEC61000-4-2_ESD.asy` | LTspice symbol for the ESD generator. |
| `projects/IEC-immunity/IEC61000-4-5_Surge_demo.cir` | Runnable deck: OCV(open), SCC(short), + example TVS-clamp DUT. |
| `projects/IEC-immunity/IEC61000-4-2_ESD_demo.cir` | Runnable deck: current into 2 Ω target, + example TVS-clamp DUT. |

The demos are **`.cir` netlists** (not `.asc`) on purpose: LTspice opens and runs
them directly and it is far less error-prone than hand-authored schematic
geometry. The `.asy` symbols are provided so you can also place the generators as
blocks in your own `.asc` schematics.

### Repo placement
These are staged to mirror `C:\Simulations\`: **generators live in `models/`**,
**demos in `projects/IEC-immunity/`**, all tracked as source (`.cir/.sub/.asy`).
Run a demo with the repo's `scripts/run_sim.py <deck>.cir`. `*.raw/*.log/simout/`
are generated and git-ignored — don't commit them. **Waveform
validation-by-running must be done on a machine with LTspice + the spicelib venv
(the personal laptop)** — it was not run here.

---

## How to use in your own design

1. **Include the generator** (netlist): `.include ../../models/IEC61000-4-5_Surge_CWG.sub`
   — or place the `.asy` symbol on a schematic (LTspice auto-includes the `.sub`
   via the symbol's `ModelFile` attribute; if it can't find it, add an explicit
   `.include`/`.lib` directive or put the `.sub` next to the schematic).
2. **Instance it** and set the level:
   - Surge: `XG1 out 0 IEC61000_4_5_CWG VPEAK=2000 TSTART=1u` (peak **open-circuit** volts).
   - ESD:   `XE1 tip 0 IEC61000_4_2_ESD KV=8 TSTART=1n` (contact-discharge **kV**).
3. **Connect the output** (`out`/`tip`) to your protected node — usually through
   the real coupling/series path (line inductance & resistance for surge; a few
   cm of trace/lead inductance for ESD).
4. **Run `.tran`.**
   - Surge decks **must use `uic`** (`.tran 0 100u 0 20n uic`) — the generator
     pre-charges its storage capacitor with `ic=`. Use a small max-timestep
     (≤20 ns) so the 1.2 µs front is resolved.
   - ESD decks need a very small max-timestep (≤20 ps) to resolve the 0.8 ns rise;
     run to ~100 ns.
5. **Look at:**
   - **V(protected node)** — the voltage your sensitive part actually sees. Compare
     against that part's absolute-max rating.
   - **Current / energy in the TVS** — `I(Dtvs)` and `∫V·I` over the pulse; check
     against the TVS peak-pulse-current and (for surge) the 8/20 µs power rating.
   - **Any device seeing over-voltage** during the fast edge (before the clamp
     snaps, or across series inductance).

---

## Generator topologies (what's inside, and the reference)

**Surge — IEC 61000-4-5 CWG.** Standard combination-wave RLC network: a charged
storage capacitor discharged through a pulse-forming network (`Rs1` shunt,
`Rm`+`Lr` series, `Rs2` shunt) so that the **same** generator produces a 1.2/50 µs
wave into an open and an 8/20 µs wave into a short, with an effective 2 Ω source
impedance. A single double-exponential can't do both; this network can. Ideal
component values (`Cc=5.93 µF, Lr=10.9 µH, Rs1=20.2 Ω, Rs2=26.1 Ω, Rm=0.814 Ω`)
are the peer-reviewed "elementary and ideal" set from **Carobbi & Bonci, IEEE EMC
Magazine 2013** (as tabulated on the IEC 61000-4-5 Wikipedia page). Peak OCV is
0.943× the charge voltage, so the model charges to `VPEAK/0.943` to hit your set
`VPEAK`.

**ESD — IEC 61000-4-2 contact discharge.** The physical gun is 150 pF / 330 Ω, but
the RC network alone misses the fast first peak. This model injects the calibrated
**current** directly with a **two-Heidler behavioural source** (`i1=16.6 A,
τ1=1.1 ns, τ2=2 ns; i2=9.3 A, τ3=12 ns, τ4=37 ns; n=1.8`, scaled linearly by kV),
which reproduces the standard double-hump and the verification points. This is the
widely-used two-Heidler set (Heidler-function fits of the IEC 61000-4-2 waveform,
e.g. Katsivelis / Fotis / Gonos, NTUA HV Lab). The `SCALE=kV/4` factor scales the
4 kV reference to any level.

---

## Validation targets (confirm on first run — I could not run LTspice)

The demo decks emit these via `.meas` (see the `.log` after running). Values are
idealised; each must sit inside the standard tolerance.

### Surge — OCV 1.2/50 µs & SCC 8/20 µs (demo at VPEAK = 1 kV)

| Quantity | Target | Tolerance | `.meas` name |
|---|---|---|---|
| OCV peak | 1000 V | (set by VPEAK) | `Vocv_peak` |
| OCV front time T1 | 1.2 µs | ±30% (0.84–1.56 µs) | `Tfront_us` |
| OCV time to half T2 | 50 µs | ±20% (40–60 µs) | from `t30`,`t50tail` |
| SCC peak | 500 A | = OCV/2 Ω | `Iscc_peak` |
| SCC front T1 | 8 µs | ±20% (6.4–9.6 µs) | inspect I(Rscc) |
| SCC time to half T2 | 20 µs | ±20% (16–24 µs) | inspect I(Rscc) |
| **Effective Z = OCVpk / SCCpk** | **2 Ω** | key check | 1000 V / 500 A |

Scaling: at **VPEAK = 2 kV**, OCV peak 2000 V and SCC peak ≈ 1000 A; times unchanged.
Front-time defn used: T1 = 1.67·(t90−t30) for the 1.2/50 voltage; for the 8/20
current T1 = 1.25·(t90−t10). T2 is time to 50% on the tail from the virtual origin.

### ESD — contact discharge current (into 2 Ω target)

Per-kV: first peak **3.75 A/kV**, I@30 ns **2 A/kV**, I@60 ns **1 A/kV**, rise **0.8 ns**.

| Quantity | @ 4 kV | @ 8 kV | Tolerance | `.meas` name |
|---|---|---|---|---|
| First peak | ~15 A (model ~14.9) | ~30 A | ±15% | `Ipk_target` |
| Rise time (10–90%) | ~0.8 ns | ~0.8 ns | ±25% | inspect I(Rtgt) edge |
| I @ 30 ns | ~8 A (model ~8.0) | ~16 A | ±30% | `I30ns` |
| I @ 60 ns | ~4 A (model ~4.0) | ~8 A | ±30% | `I60ns` |

(Hand-computed from the two-Heidler parameters, 4 kV: peak 14.9 A, I@30ns 8.0 A,
I@60ns 4.0 A — all inside tolerance. `TSTART=1n`, so the 30/60 ns points are read
at 31 ns / 61 ns.)

---

## Standard test levels (reference)

### IEC 61000-4-5 surge — installation levels (open-circuit voltage)

| Level | Voltage |
|---|---|
| 1 | 0.5 kV |
| 2 | 1 kV |
| 3 | 2 kV |
| 4 | 4 kV |

- **Line-to-line** coupling: 2 Ω source impedance (the model here).
- **Line-to-ground** coupling: the standard adds an external **+10 Ω (→ 12 Ω total)**
  and a different coupling/decoupling network. **Not modelled here** — for L-G,
  add a 10 Ω series resistor at the output and the appropriate coupling cap.

### IEC 61000-4-2 ESD — test levels

| Level | Contact | Air |
|---|---|---|
| 1 | 2 kV | 2 kV |
| 2 | 4 kV | 4 kV |
| 3 | 6 kV | 8 kV |
| 4 | 8 kV | 15 kV |

**Default here is contact discharge** (repeatable, current directly specified &
verifiable). **Air discharge** is applied by approach/arcing: the actual current
depends on approach speed, humidity, tip geometry and arc formation, so it is far
more variable and is specified by *test voltage*, not a fixed current waveform —
it is not modelled as a current source here.

---

## Caveats (read before trusting a result)

1. **Design aid, not compliance.** These idealised sources verify clamp behaviour,
   relative robustness and energy — they are **not a substitute for accredited
   compliance testing** on real hardware.
2. **Layout parasitics dominate reality.** The voltage a part actually sees is set
   by trace/lead **inductance** (V = L·di/dt on the fast edge — huge for the 0.8 ns
   ESD edge and the 8/20 µs surge), return-path and coupling geometry. Put realistic
   series L in the path; the idealised generator won't warn you about board layout.
3. **TVS model fidelity.** The demo clamps (`TVSCLAMP`, `ESDTVS`) are **illustrative
   `.model D` placeholders** — swap in the **manufacturer's SPICE model** of your
   actual TVS (dynamic resistance, capacitance and turn-on set the real clamp
   voltage). An ideal diode will flatter your design.
4. **Idealised source impedance / current forcing.** Surge is an ideal RLC (real
   generators drift with switch non-idealities and tolerances — Carobbi values are
   a simulation starting point). ESD is an **ideal current source** (forces the
   waveform regardless of DUT); conservative for clamp checks, but the source-node
   voltage across any series inductance is a modelling artifact — trust the
   **clamped node**, not the raw generator node.
5. **Line-to-ground surge not modelled.** Only the 2 Ω line-to-line case is built.
   Add the +10 Ω and CWG back-filter / coupling-decoupling network yourself for L-G.
6. **`uic` requirement (surge).** The surge deck relies on `.tran … uic` for the
   pre-charged cap. Without `uic`, the cap starts at 0 V and you get no surge.

---

### Sources
- IEC 61000-4-5 CWG ideal values & topology — Carobbi & Bonci, *"Elementary and
  ideal equivalent circuit model of the 1,2/50-8/20 µs combination wave generator"*,
  IEEE EMC Magazine 2013; values via en.wikipedia.org/wiki/IEC_61000-4-5.
- IEC 61000-4-2 two-Heidler current parameters — Heidler-function fits of the
  standard ESD current (Katsivelis/Fotis/Gonos, NTUA HV Lab) and IEC 61000-4-2
  contact-discharge verification table (3.75 A/kV, 0.8 ns, 2 A/kV @30 ns,
  1 A/kV @60 ns).
