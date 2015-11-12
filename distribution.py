import os
import sys
import math

# compute entropy and conditional entropy for each component index (using data) --- this would help the transparent encryption paper ONLY, not the obfuscation paper
# compute list of MI between two names based on applying obfuscation technique at each component index

def compute_conditional_entropy(pmfs):
    # H(Y | X) = \sum_{x \in X} p(x) H(Y | X = x)
    #          = - \sum_{x \in X} p(x) \sum_{y \in Y} p(y | x) * log(p(y | x))
    pass

def compute_entropy(pmf):
    # H(X) = - \sum_{x \in X} p(x) log(p(x)) --> p(x) is PMF
    total = 0
    for x in pmf:
        total += (pmf[x] * math.log2(pmf[x]))
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
    
    num_samples = reduce(lambda x, y: min(len(x), len(y)), samples_list)
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
        pmf[sample] = 1 if sample not in pmf else pmf[sample] + 1
    total = len(samples)
    for key in pmf:
        pmf[key] = pmf[key] / float(total)
    return pmf

def compute_distribution(pairs):
    if len(pairs) == 0:
        raise Exception("Can't compute the PMF of nothing!")
    num_cols = len(pairs)
    for i in range(num_cols):
        pmf = compute_pmf(pairs[i])
        print pmf
    pmf = compute_joint_pmf(pairs)
    print pmf

with open(sys.argv[1], "r") as f:
    matrix = map(lambda line: line.strip().split(","), f.readlines())
    length = len(matrix[0])
    pairs = []
    for i in range(length):
        pairs.append(map(lambda l : l[i], matrix))
    compute_distribution(pairs)

