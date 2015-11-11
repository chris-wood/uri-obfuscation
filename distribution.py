import os
import sys

# compute entropy and conditional entropy for each component index (using data) --- this would help the transparent encryption paper ONLY, not the obfuscation paper
# compute list of MI between two names based on applying obfuscation technique at each component index

def compute_conditional_entropy(pairs):
    # H(Y | X) = \sum_{x \in X} p(x) H(Y | X = x)
    pass

def compute_entropy(pairs):
    # H(X) = - \sum_{x \in X} p(x) log(p(x)) --> p(x) is PMF
    pass

def compute_mutual_information(pairs):
    # I(X;Y) -> H(X) - H(Y)
    pass

def compute_entropy_efficiency(pairs):
    # Eff(X) = - \sum_{i=1}^{n} \frac{p(x_i)log(p(x_i))}{log(n)}
    # n = number of bits in each element of the alphabet
    pass

def compute_pmf(pairs):
    pmf = {}
    for pair in pairs:
        event = pair[0]
        outcome = pair[1]
        pmf[outcome] = 1 if outcome not in pmf else pmf[outcome] + 1
    total = len(pairs)
    for key in pmf:
        pmf[key] = pmf[key] / float(total)
    return pmf

def compute_distribution(pairs):
    pmf = compute_pmf(pairs)
    print pmf

with open(sys.argv[1], "r") as f:
    pairs = map(lambda line: line.strip().split(","), f.readlines())
    compute_distribution(pairs)
