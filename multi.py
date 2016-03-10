import multiprocessing as mp
import itertools
import time
import csv

def count(*samples_list):
    print samples_list
    time.sleep(1)
    pass

def dispatch(samples_list, N = 8):
    pool = mp.Pool()

    pids = pool.map(func=count, iterable=samples_list, chunksize=10)

    jobs = []
    for i, s in enumerate(slice):
        # print s 
        j = mp.Process(target=count, args=s)
        jobs.append(j)
    for j in jobs:
        j.start()

    pass

dispatch([1] * 100)
