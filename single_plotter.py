import os
import sys
import matplotlib.pyplot as plt

fname = sys.argv[1]
fhandle = open(fname, "r")

width = 1

single_entropy = {}
joint_entropy = {}

for line in fhandle:
    data = line.split(",")
    cmin = int(data[0])
    cmax = int(data[1])
    pmf = float(data[2])
    jpmf = float(data[3])

    single_entropy[cmax] = pmf
    joint_entropy[(cmin, cmax)] = jpmf   

plt.close('all')
fig, ax = plt.subplots(1)
rects = ax.bar(single_entropy.keys(), single_entropy.values(), width, color='r')
ax.set_ylabel("Entropy")
ax.set_title("Single Component Entropy")
ax.set_xticks(single_entropy.keys())

plt.show()

#plt.savefig(fname + ".png");

# plt.plot(plotdata)
# plt.ylabel('some sheet')
# plt.show()
