PATTERN = (0, 1, 0, -1)

signal = []
with open("input_s", "r") as f:
    for c in f.read().strip():
        signal.append(int(c))
output = signal[:]

for phase in range(100):
    oc = 1
    while (3*oc - 1) < len(signal):
        s = 0
        step = 4*oc
        start1, start2 = oc - 1, 3*oc - 1
        for start in range(oc):
            s += sum(signal[start+start1::step]) - sum(signal[start+start2::step])
        output[oc-1] = abs(s)%10
        oc += 1
    for oc in range(oc, len(signal)+1):
        output[oc-1]  = abs(sum(signal[oc-1:oc-1 + oc]))%10
    signal, output = output, signal
print("".join(str(s) for s in signal[:8]))