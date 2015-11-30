import os
import sys
import matplotlib.pyplot as plt

fname = sys.argv[1]
fhandle = open(fname, "r")

width = 1

joint_entropy = {}
plotdata = []

maxcol = 0

for line in fhandle:
    data = line.split(",")
    cmin = int(data[0])
    cmax = int(data[1])
    pmf = float(data[2])
    jpmf = float(data[3])

    maxcol = cmax if cmax > maxcol else maxcol

    if cmin not in joint_entropy:
        joint_entropy[cmin] = []
    joint_entropy[cmin].append((cmax, jpmf))

plt.close('all')
fig, ax = plt.subplots()

for cmin in joint_entropy:
    data = joint_entropy[cmin]
    print "Plotting %d %s" % (cmin, str(data))

    x = range(cmin + 1, cmax + 1)
    y = map(lambda x : x[1], data)
    print x, y
    plt.plot(x, y)

#plt.legend(["Offset = %d" % (d) for d in joint_entropy], loc='upper left')

ax.set_ylabel("Entropy")
ax.set_xlabel("Name Component Offset")
ax.set_title("URI Joint Entropy")
ax.set_xticks(range(maxcol))

plt.show()

#ax.plot(plotdata)
#fig.autofmt_xdate()
#import matplotlib.dates as mdates
#ax.fmt_xdata = mdates.DateFormatter('%m-%d-%Y')

#plt.title('Entropy')

#plt.xticks(range(1, index), ticks)

#plt.show()

#plt.savefig(fname + ".png");

# plt.plot(plotdata)
# plt.ylabel('some sheet')
# plt.show()
