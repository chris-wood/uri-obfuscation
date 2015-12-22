import os
import sys
import math
import logging
import numpy as np
import itertools

def single_entropy(X):
    probs = [np.mean(X == c) for c in set(X)]
    return np.sum(-p * np.log2(p) for p in probs)

def two_entropy(X,Y):
    probs = []
    for c1 in set(X):
        for c2 in set(Y):
            probs.append(np.mean(np.logical_and(X == c1, Y == c2)))

    return np.sum(-p * np.log2(p) for p in probs)

def entropy(jpmfs, *X):
    n_insctances = len(X[0])
    H = 0
    i = 0
    for classes in itertools.product(*[set(x) for x in X]):
        # Only attempt to accumulate entropy bits if the combination is actually observed.
        found = False
        for i in range(len(jpmfs)):
            if classes in jpmfs[i]:
                found = True

        if found:
            v = np.array([True] * n_insctances)
            for predictions, c in zip(X, classes):
                v = np.logical_and(v, predictions == c)
            p = np.mean(v)
            H += -p * np.log2(p) if p > 0 else 0
    return H

def conditional_entropy(jpmfs, Xs):
    if len(Xs) == 1:
        return entropy(jpmfs, *Xs)
    else:
        full = entropy(jpmfs, *Xs)
        partial = entropy(jpmfs, *Xs[0:len(Xs)-1])
        return full - partial

def mutual_information(X,Y,XY):
    # I(X;Y) -> H(X) - H(Y) - H(X,Y)
    Hx = entropy(*X)
    Hy = entropy(*Y)
    Hxy = entropy(*XY)
    return (Hx - Hy + Hxy)

def entropy_efficiency(pairs):
    # Eff(X) = - \sum_{i=1}^{n} \frac{p(x_i)log(p(x_i))}{log(n)}
    # n = number of bits in each element of the alphabet
    pass

def compute_conditional_pmf(samples_list):
    '''
    Input: list of samples lists: [[sample-list-1], [sample-list-2], ...]
    Output: map from (symbol1, symbol2, ...) -> probability
    '''
    # TODO: use Bayes' Thm
    pass

def compute_joint_pmf(samples_list):
    '''
    Input: list of samples lists: [[sample-list-1], [sample-list-2], ...]
    Output: map from (symbol1, symbol2, ...) -> probability
    '''
    pmf = {}

    num_samples = min(reduce(lambda x, y: x + [len(y)], samples_list, []))
    num_lists = len(samples_list)
    for i in range(num_samples):
        symbols = []
        for j in range(num_lists):
            symbols.append(samples_list[j][i])

        key = tuple(symbols)
        pmf[key] = 1 if key not in pmf else pmf[key] + 1

    total = num_samples
    for key in pmf:
        pmf[key] = pmf[key] / float(total)

    return pmf

def compute_pmf(samples):
    '''
    Input: list of samples
    Output: map from symbol -> probability
    '''
    pmf = {}
    for sample in samples:
        pmf[(sample,)] = 1 if (sample,) not in pmf else pmf[(sample,)] + 1
    total = len(samples)
    for key in pmf:
        pmf[key] = pmf[key] / float(total)
    return pmf

def compute_distribution(pairs, cmin, cmax):
    if len(pairs) == 0:
        print cmin, cmax, "Can't compute the PMF of nothing!"
        return

    logging.debug("Starting run for cmin=%d cmax=%d" % (cmin, cmax))
    logging.debug("Pairs = %s" % (str(pairs)))

    # print cmin, cmax, pairs

    pmfs = []
    for i in range(cmin, cmax):
        pmf = compute_pmf(pairs[i])
        logging.debug(str(pmf))
        pmfs.append(pmf)


    jpmfs = []
    for i in range(cmin, cmax):
        jpmf = compute_joint_pmf(pairs[cmin:(i+1)])
        logging.debug(str(jpmf))
        jpmfs.append(jpmf)

    H = entropy(jpmfs, *pairs[cmin:cmax])
    Hc = conditional_entropy(jpmfs, pairs[cmin:cmax])

    print >> sys.stderr, ("%d,%d,%f,%f" % (cmin, cmax, H, Hc))
    print >> sys.stdout, ("%d,%d,%f,%f" % (cmin, cmax, H, Hc))

    # if len(jpmfs) > 0:
    #     single_entropy = compute_entropy(pmfs[-1])
    #     joint_entropy = compute_joint_entropy(cmin, cmax, pmfs, jpmfs)
    #     conditional_entropy = compute_conditional_entropy(cmin, cmax, pmfs, jpmfs)
    #
    #
    #     # Sanity check...
    #     if (joint_entropy > single_entropy and joint_entropy != 0.0 and single_entropy != 0.0):
    #         raise Exception("Impossible condition: The joint entropy cannot be larger than the single entropy")
    #     logging.debug("Joint=%f and Single=%f entropy result for cmin=%d cmax=%d" % (joint_entropy, single_entropy, cmin, cmax))
    # else:
    #     entropy = compute_entropy(pmfs[0])
    #     logging.debug("Single=%f entropy result for cmin=%d cmax=%d" % (single_entropy, cmin, cmax))

def main(args):
    logging.basicConfig(filename='entropy_log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(args[1], "r") as f:
        matrix = map(lambda line: line.strip()[1:].split("/"), f.readlines())
        num_cols = int(args[2]) # max number of components in a URI
        num_rows = len(matrix)

        # For each possible column slice
        for cmin in range(0, num_cols):
            for cmax in range(cmin + 1, num_cols + 1):
                # This will hold the columns of the matrix
                columns = []

                # For each column in the matrix
                for c in range(cmax):
                    column = map(lambda row : row[c], filter(lambda row : len(row) > cmax, matrix))
                    columns.append(np.array(column))

                # Compute the distribution information from this column set
                compute_distribution(columns, cmin, cmax)

if __name__ == "__main__":
    main(sys.argv)
