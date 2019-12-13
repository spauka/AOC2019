import re

def qp(line):
    m = re.findall(r"([-+\d]+)", line)
    return tuple(int(x) for x in m)

d = []
with open("input", "r") as inp:
    for line in inp:
        d.extend(qp(line))

# Part 1
fuel = 0
for n in d:
    fuel += n//3 - 2
print(fuel)

def c(f):
    new_fuel = f // 3 - 2
    if new_fuel < 0:
        return 0
    return new_fuel

# Part 2
fuel = 0
for n in d:
    new_fuel = c(n)
    while new_fuel != 0:
        fuel += new_fuel
        new_fuel = c(new_fuel)
print(fuel)
