import re

minp, maxp = 372037, 905157
print(len([i for i in range(372037, 905157+1) if re.findall(r"(.)\1", str(i)) and "".join(sorted(str(i))) == str(i)]))
print(len([i for i in range(372037, 905157+1) if 2 in (str(i).count(d) for d in str(i)) and "".join(sorted(str(i))) == str(i)]))