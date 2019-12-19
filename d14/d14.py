from collections import namedtuple, defaultdict
from math import ceil

Reaction = namedtuple("Reaction", ("inps", "out"))
Ingredient = namedtuple("Ingredient", ("qty", "name"))

reactions = {}
with open("input", "r") as f:
    for line in f:
        inps, out = line.strip().split("=>")
        inps = tuple(m.strip().split(" ") for m in inps.strip().split(","))
        inps = tuple(Ingredient(int(m[0]), m[1]) for m in inps)
        out = out.strip().split(" ")
        out = Ingredient(int(out[0]), out[1])
        react = Reaction(inps, out)
        reactions[out.name] = react

def run_reaction(n_fuel):
    ore = 0
    spares = defaultdict(int)
    requirements = defaultdict(int)
    requirements["FUEL"] = n_fuel

    while requirements:
        # Remove ingredients in reverse order of creation (i.e. ORE last)
        ingredient, qty = requirements.popitem()
        if ingredient == "ORE":
            ore += qty
        else:
            # If there are spares, remove them first
            nspares = spares[ingredient]
            # If we have enough spares, no need to perform the reaction
            if nspares >= qty:
                spares[ingredient] -= qty
            else:
                # Calculate the number of times the reaction must be run
                qty -= nspares
                spares[ingredient] = 0
                reaction = reactions[ingredient]
                nreact = ceil(qty/reaction.out.qty)
                # Add each requirement to the list of outstanding requirements
                for inp in reaction.inps:
                    requirements[inp.name] += nreact*inp.qty
                # And add any spares created
                spares[ingredient] = reaction.out.qty*nreact - qty
    return ore

# Part 1
print(f"Required Ore: {run_reaction(1)}")
# Part 2
max_ore = 1_000_000_000_000
fuel = 1
n_required = run_reaction(fuel)
while n_required < max_ore:
    fuel <<= 1
    n_required = run_reaction(fuel)
# Do a binary search
lower, upper = fuel >> 1, fuel
while lower < upper:
    fuel = lower + (upper-lower)//2
    n_required = run_reaction(fuel)
    if n_required > max_ore:
        upper = fuel - 1
    else:
        lower = fuel + 1
print(f"Fuel: {upper}")