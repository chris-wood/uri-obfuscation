from concurrent.futures import *
import itertools
import time
import csv

def single_count(l):
    return (l, 1)

def group_counts(result):
    groups = {}
    total = 0
    for item, count in result:
        groups[item] = 1 if item not in groups else groups[item] + 1
        total += count
    return groups, total

def reduce(l):
    return (l[0], sum(pair[1] for pair in l[1]))

with ThreadPoolExecutor(max_workers=2) as executor:
    result = executor.map(single_count, XXX)
    group, count = group_counts(result)
    result = executor.map(lambda l : float(group[l]) / count, group)
    for v in result:
        print v,
