import itertools
PATTERN = (" ", "▉", " ", "☐")
def repiter(pattern, count):
    for c in pattern:
        for _ in range(count):
            yield(c)

slen = 100
for outc in range(slen):
    line = ""
    for _, c in zip(range(slen), itertools.islice(repiter(itertools.cycle(PATTERN), outc+1), 1, None)):
        line += c
    print(line)