# models/ — shared SPICE subcircuits & symbols

Reusable, tracked SPICE sources shared across projects: `.lib`, `.sub`, `.mod`, `.asy`.

Drop a vendor model here (from the manufacturer site / DigiKey product page, per the
DigiKey-first rule) when more than one project needs it; project-specific one-offs can live
next to their deck under `projects/<name>/`. **Review any downloaded model before
`.include`-ing it** — a `.cir` can pull in external files.
