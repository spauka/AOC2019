import re

def qp(line):
    m = re.findall(r"([-+\d]+)", line)
    return tuple(int(x) for x in m)

d = []
with open("input", "r") as inp:
    for line in inp:
        init = list(qp(line))
d = init[:]

d[1] = 12
d[2] = 2

s = 0
while d[s] != 99:
    if d[s] == 1:
        d[d[s+3]] = d[d[s+1]] + d[d[s+2]]
    elif d[s] == 2:
        d[d[s+3]] = d[d[s+1]] * d[d[s+2]]
    s += 4

print(d[0])

for noun in range(0, 99):
    for verb in range(0, 99):
        d = init[:]
        d[1] = noun
        d[2] = verb
        s = 0
        while d[s] != 99:
            if d[s] == 1:
                d[d[s+3]] = d[d[s+1]] + d[d[s+2]]
            elif d[s] == 2:
                d[d[s+3]] = d[d[s+1]] * d[d[s+2]]
            s += 4

        if d[0] == 19690720:
            print(f"noun: {noun}, verb: {verb}, ans: {100*noun + verb}")
            break