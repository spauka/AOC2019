signal = []
with open("input", "r") as f:
    for c in f.read().strip()*10000:
        signal.append(int(c))
output = signal[:]
offs = int("".join(str(c) for c in signal[:7]))

assert offs > len(signal)//2

for phase in range(100):
    print(phase)
    # oc = 1
    # while (3*oc - 1) < len(signal):
    #     csum = 0
    #     start = oc - 1
    #     factor = 1
    #     while start < len(signal):
    #         csum += factor*signal[start:start+oc].sum()
    #         factor *= -1
    #         start += 2*oc
    #     output[oc-1] = abs(csum)%10
    #     oc += 1
    #     if oc%1000 == 0: print(oc)
    # oc = (len(signal)+1)//3
    # csum = sum(signal[oc-1:2*oc-1])
    # for oc in range(oc, len(signal)//2):
    #     csum -= signal[oc-1]
    #     csum += signal[2*oc-1] + signal[2*oc]
    #     output[oc]  = abs(csum)%10
    csum = 0
    for oc in range(len(signal) - 1, len(signal)//2 - 1, -1):
        csum += signal[oc]
        output[oc] = csum%10
    signal, output = output, signal

print("".join(str(s) for s in signal[offs:offs+8]))