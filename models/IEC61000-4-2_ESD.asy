Version 4
SymbolType BLOCK
RECTANGLE Normal 0 0 128 96
LINE Normal 24 72 56 72
LINE Normal 40 72 40 40
LINE Normal 40 40 72 40
LINE Normal 60 34 60 46
LINE Normal 72 40 72 28
LINE Normal 84 48 104 48
LINE Normal 96 40 104 48
LINE Normal 96 56 104 48
TEXT 64 88 Center 2 ESD 4-2 contact
WINDOW 0 64 -8 Bottom 2
WINDOW 3 64 104 Top 2
SYMATTR Prefix X
SYMATTR Value IEC61000_4_2_ESD
SYMATTR ModelFile IEC61000-4-2_ESD.sub
SYMATTR Description IEC 61000-4-2 ESD generator, contact discharge, two-Heidler current source. Params: KV, TSTART.
SYMATTR SpiceLine KV=4 TSTART=1n
PIN 128 32 LEFT 8
PINATTR PinName tip
PINATTR SpiceOrder 1
PIN 0 32 RIGHT 8
PINATTR PinName gnd
PINATTR SpiceOrder 2
