import os
import sys
import math

# compute entropy and conditional entropy for each component index (using data) --- this would help the transparent encryption paper ONLY, not the obfuscation paper
# compute list of MI between two names based on applying obfuscation technique at each component index

def compute_conditional_entropy(pmfs, jpmfs, index = 0, acc = 0, indices = []):
    '''
    Input:
        - list of individual pmfs: pmf(x1), pmf(x2), pmf(x3), ...
        - list of joint pmfs: pmf(x1), pmf(x2 | x1), pmf(x3 | x1 ^ x2), ...
        - symbol index for entropy, e.g., 1
            1 returns H(x2 | x1)
            2 returns H(x3 | x1 ^ x2)
    Output: conditional entropy
    '''
    length = len(jpmfs)
    if index == (length - 1):
        entropy = 0
        for xi in pmfs[index]:
            new_index = tuple(indices[:] + [xi[0]])
            if new_index in jpmfs[index]:
                entropy += (jpmfs[index][new_index] * math.log(jpmfs[index][new_index], 2))
        return (entropy * -1)
    else:
        entropy = 0
        for xi in pmfs[index]:
            new_index = tuple(indices[:] + [xi[0]])
            if new_index in jpmfs[index]:
                entropy += (jpmfs[index][new_index] * compute_conditional_entropy(pmfs, jpmfs, index + 1, acc, list(new_index)))
        return entropy

def compute_pair_conditional_entropy(pmfX, pmfY, pmfXY):
    '''
    Input:
        pmfX is map from (x) -> probability
        pmfY is map from (y) -> probability
        pmfXY is a map from (x, y) -> probability
    Output: conditional entropy
    '''
    # H(Y | X) = \sum_{x \in X} p(x) H(Y | X = x)
    #          = - \sum_{x \in X} p(x) \sum_{y \in Y} p(y | x) * log2(p(y | x))
    total = 0
    for (x) in pmfX:
        inner = 0
        for (y) in pmfY:
            if (x[0],y[0]) in pmfXY:
                inner += pmfXY[(x[0], y[0])] * math.log(pmfXY[(x[0],y[0])], 2)
        total += pmfX[x] * inner
    return (total * -1)

def compute_entropy(pmf):
    '''
    Input: pmf is a map from (x) -> probability
    Output: entropy
    '''
    # H(X) = - \sum_{x \in X} p(x) log2(p(x)) --> p(x) is PMF
    total = 0
    for x in pmf:
        total += (pmf[x] * math.log(pmf[x], 2))
    return (total * -1)

def compute_mutual_information(pairs):
    # I(X;Y) -> H(X) - H(Y)
    pass

def compute_entropy_efficiency(pairs):
    # Eff(X) = - \sum_{i=1}^{n} \frac{p(x_i)log(p(x_i))}{log(n)}
    # n = number of bits in each element of the alphabet
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

    print "======="
    print cmin, cmax
    print pairs

    pmfs = []
    for i in range(cmin, cmax):
        pmf = compute_pmf(pairs[i])
        pmfs.append(pmf)

    jpmfs = []
    for i in range(cmin, cmax):
        jpmf = compute_joint_pmf(pairs[cmin:(i+1)])
        jpmfs.append(jpmf)

    if len(jpmfs) > 0:
        joint_entropy = compute_conditional_entropy(pmfs, jpmfs)
        single_entropy = compute_entropy(pmfs[-1])
        if (joint_entropy > single_entropy):
            raise Exception("Impossible!")
        print "general", cmin, cmax, joint_entropy, single_entropy
    else:
        entropy = compute_entropy(pmfs[0])
        print "first", cmin, cmax, entropy

    print "=======\n"

with open(sys.argv[1], "r") as f:
    matrix = map(lambda line: line.strip()[1:].split("/"), f.readlines())
    num_cols = int(sys.argv[2]) # max number of components in a URI
    num_rows = len(matrix)

    # For each possible column slice
    for cmin in range(0, num_cols):
        for cmax in range(cmin + 1, num_cols + 1):
            # This will hold the columns of the matrix
            columns = []

            # For each column in the matrix
            for c in range(cmax):
                column = map(lambda row : row[c], filter(lambda row : len(row) > c, matrix))
                columns.append(column)

            # Compute the distribution information from this column set
            compute_distribution(columns, cmin, cmax)
