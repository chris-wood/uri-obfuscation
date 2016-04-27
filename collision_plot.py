import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

width = 0.35
n = np.arange(1, 21)
m = [185769, 10159460, 138848082, 305236992, 356952045, 225092000, 162898537,
     98471166, 40003541, 19165574, 10485282, 7597933, 3514400, 2540599,
     1952318, 1193997, 1066544, 1044263, 771267, 646401]
pexp = [9.31e-10, 2.80e-6, 5.12e-4, 2.41e-3, 3.27e-3, 1.33e-3, 7.01e-4, 2.59e-4,
        4.31e-5, 9.93e-6, 2.96e-6, 1.57e-6, 3.34e-7, 1.75e-7, 1.05e-7, 3.73e-8,
        3.21e-8, 3.05e-8, 1.70e-8, 1.07e-8]
pana = [9.35e-10, 2.79e-6, 5.12e-4, 2.41e-3, 3.27e-3, 1.32e-3, 7.01e-4, 2.59e-4,
        4.31e-5, 9.93e-6, 2.98e-6, 1.56e-6, 3.35e-7, 1.75e-7, 1.03e-7, 3.86e-8,
        3.08e-8, 2.96e-8, 1.61e-8, 1.13e-8]

fig = plt.figure()

ax1 = fig.add_subplot(211)
ax1.bar(n + (width / 2), m, width, color='#0072bd', log=True)
ax1.set_ylabel(r'Number of unique prefixes $m$')
ax1.set_xticks(n + width)
ax1.set_xticklabels(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                     '12', '13', '14', '15', '16', '17', '18', '19', '20'))
ax1.set_xlim([0.8, 21])
ax1.grid(True)

ax2 = fig.add_subplot(212)
ax2.bar(n, pexp, width, color='#d95319', log=True)
ax2.bar(n + width, pana, width, color='#eeb429', log=True)
ax2.set_xlabel(r'Number of prefix segments $n$')
ax2.set_ylabel(r'Probability of Collision $f(2^+)$')
ax2.set_xticks(n + width)
ax2.set_xticklabels(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                     '12', '13', '14', '15', '16', '17', '18', '19', '20'))
ax2.set_xlim([0.8, 21])
ax2.grid(True)

# Save to file.
pp = PdfPages('collision_plot.pdf')
plt.savefig(pp, format='pdf')
pp.close()
