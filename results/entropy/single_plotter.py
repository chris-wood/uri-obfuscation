import os
import sys
import matplotlib.pyplot as plt

fname = sys.argv[1]
fhandle = open(fname, "r")
fname = fname[0:fname.index(".")]

width = 1

single_entropy = {}

for line in fhandle:
    data = line.split(",")
    cmin = int(data[0])
    cmax = int(data[1])
    jpmf = float(data[2])
    cpmf = float(data[3])

    if cmax - cmin == 1:
        print single_entropy
        single_entropy[cmax] = jpmf

plt.close('all')
fig, ax = plt.subplots(1)
rects = ax.bar(single_entropy.keys(), single_entropy.values(), width, color='r')
ax.set_xlabel("Name Component Index")
ax.set_ylabel("Entropy")
ax.set_title("Single Component Entropy")
ax.set_xticks(single_entropy.keys())

# plt.show()

plt.savefig(fname + ".eps")

# plt.plot(plotdata)
# plt.ylabel('some sheet')
# plt.show()
