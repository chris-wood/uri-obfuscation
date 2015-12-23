import os
import sys
import itertools
import matplotlib as m
import matplotlib.pyplot as plt

fname = sys.argv[1]
fhandle = open(fname, "r")
fname = fname[0:fname.index(".")]

width = 1

joint_entropy = {}
conditional_entropy = {}
plotdata = []

maxcol = 0

colors = itertools.cycle(['red', 'black', 'blue', 'brown', 'green'])

for line in fhandle:
    data = line.split(",")
    cmin = int(data[0])
    cmax = int(data[1])
    jpmf = float(data[2])
    cpmf = float(data[3])

    maxcol = cmax if cmax > maxcol else maxcol

    if cmin not in joint_entropy:
        joint_entropy[cmin] = []
        conditional_entropy[cmin] = []
    joint_entropy[cmin].append((cmax, jpmf))
    conditional_entropy[cmin].append((cmax, cpmf))

plt.close('all')
fig, ax = plt.subplots()

cmin = 0
seen = []
total = joint_entropy.keys()
for color in colors:
    if cmin in joint_entropy:
        data = joint_entropy[cmin]
        print "Plotting %d %s" % (cmin, str(data))

        x = range(cmin + 1, cmax + 1)
        y = map(lambda x : x[1], data)
        print x, y
        plt.plot(x, y, color=color)

        data = conditional_entropy[cmin]
        x = range(cmin + 1, cmax + 1)
        y = map(lambda x : x[1], data)
        plt.plot(x, y, ls="dashed", color=color)

        seen.append(cmin)

    if seen == total:
        break
    cmin += 1

#plt.legend(["Offset = %d" % (d) for d in joint_entropy], loc='upper left')

ax.set_ylabel("Entropy")
ax.set_xlabel("Name Component Offset")
ax.set_title("URI Joint and Conditional Entropy")
ax.set_xticks(range(maxcol))

# plt.show()

#ax.plot(plotdata)
#fig.autofmt_xdate()
#import matplotlib.dates as mdates
#ax.fmt_xdata = mdates.DateFormatter('%m-%d-%Y')

#plt.title('Entropy')

#plt.xticks(range(1, index), ticks)

#plt.show()

plt.savefig(fname + ".png")

# plt.plot(plotdata)
# plt.ylabel('some sheet')
# plt.show()
