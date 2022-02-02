import itertools
import random
from itertools import product
size = 8
cell=set()
cell.add(1)
cell.add(2)

for c in product(*(range(n - 1, n + 2) for n in cell)):
    print(c)

# print(list(product((0,1)))
