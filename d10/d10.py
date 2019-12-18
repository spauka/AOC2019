from math import atan2, pi

class Point(tuple):
    def __add__(self, o):
        return Point((x+y for x, y in zip(self, o)))

    def __sub__(self, o):
        return Point((x-y) for x, y in zip(self, o))
    
    def __abs__(self):
        return Point(abs(x) for x in self)

class Fraction(tuple):
    @staticmethod
    def gcd(x, y):
        if y == 0:
            return x
        return Fraction.gcd(y, x%y)

    def __new__(cls, point):
        x, y = point
        gcd = abs(Fraction.gcd(x, y))
        return super().__new__(tuple, (x//gcd, y//gcd))

asteroids = set()

with open('input', 'r') as f:
    x, y = 0, 0
    for y, line in enumerate(f):
        for x, c in enumerate(line.strip()):
            if c == '#':
                asteroids.add(Point((x, y)))
    grid_size = Point((x, y))

# Part 1
num_los = []
for asteroid in asteroids:
    los = set()
    for other in asteroids:
        if asteroid is other:
            continue
        frac = Fraction(asteroid - other)
        los.add(frac)
    num_los.append((len(los), asteroid))
num_los, asteroid = max(num_los)
print(num_los, asteroid)

# Part 2
num_hit = 0
while asteroids:
    los = {}
    for other in asteroids:
        if asteroid is other:
            continue
        frac = Fraction(asteroid - other)
        if frac not in los:
            los[frac] = other
        elif sum(abs(asteroid - other)) < sum(abs(asteroid - los[frac])):
            los[frac] = other

    if num_hit + len(los) >= 200:
        hits = sorted(los.items(), key=lambda x: abs(atan2(*x[0])) if atan2(*x[0]) <= 0 else 2*pi - atan2(*x[0]))
        print(len(hits))
        print(hits[:10])
        ths = hits[200-1]
        print(ths, ths[1][0]*100 + ths[1][1])
        break
    asteroids.difference_update(los)
    num_hit += len(los)