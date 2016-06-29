# TODO: integrate the memoization speedup
def compute_joint_entropy(cmin, cmax, pmfs, jpmfs, index = 0, acc = {}, indices = []):
    '''
    Input:
        - TODO
    Output: joint entropy
    '''
    # H(Y,X) = H(X,Y) = - \sum_{x \in X} \sum_{y \in Y} p(x,y) * log2(p(x,y))
    length = len(jpmfs)
    if index == (length - 1):
        entropy = 0
        for x in pmfs[index]:
            new_index = tuple(indices[:] + [x[0]])
            if new_index in jpmfs[index]:
                entropy += (jpmfs[index][new_index]) * math.log(jpmfs[index][new_index], 2)
        return (entropy * -1)
    else:
        entropy = 0
        for x in pmfs[index]:
            new_index = tuple(indices[:] + [x[0]])
            if new_index in jpmfs[index]:
                # entropy += (jpmfs[index][new_index] * compute_joint_entropy(cmin, cmax, pmfs, jpmfs, index + 1, acc, list(new_index)))
                entropy += (compute_joint_entropy(cmin, cmax, pmfs, jpmfs, index + 1, acc, list(new_index)))
        return entropy

# compute entropy and conditional entropy for each component index (using data) --- this would help the transparent encryption paper ONLY, not the obfuscation paper
# compute list of MI between two names based on applying obfuscation technique at each component index

# TODO: this is not correct! it uses the joint PMF, not conditional PMF
def compute_conditional_entropy(cmin, cmax, pmfs, jpmfs, index = 0, acc = {}, indices = []):
    '''
    Input:
        - list of individual pmfs: pmf(x1), pmf(x2), pmf(x3), ...
        - list of joint pmfs: pmf(x1), pmf(x2 | x1), pmf(x3 | x1 ^ x2), ...
        - symbol index for entropy, e.g., 1
            1 returns H(x2 | x1)
            2 returns H(x3 | x1 ^ x2)
    Output: conditional entropy
    '''
    # H(Y | X) = \sum_{x \in X} p(x) H(Y | X = x)
    #          = - \sum_{x \in X} p(x) \sum_{y \in Y} p(y | x) * log2(p(y | x))
    #          = ...
    #          = \sum_{x \in X, y \in Y} p(x,y) log2(p(x,y) / p(x))

    # OLD!
    # length = len(jpmfs)
    # if index == (length - 1):
    #     entropy = 0
    #     for xi in pmfs[index]:
    #         new_index = tuple(indices[:] + [xi[0]])
    #         if new_index in jpmfs[index]:
    #             tmp_index = (cmin, cmax, new_index)
    #             if tmp_index not in acc:
    #                 acc[tmp_index] = math.log(jpmfs[index][new_index], 2)
    #             entropy += (jpmfs[index][new_index] * acc[tmp_index])
    #     return entropy
    # else:
    #     entropy = 0
    #     for xi in pmfs[index]:
    #         new_index = tuple(indices[:] + [xi[0]])
    #         if new_index in jpmfs[index]:
    #             tmp_index = (cmin, cmax, new_index)
    #             if tmp_index not in acc:
    #                 acc[tmp_index] = compute_conditional_entropy(cmin, cmax, pmfs, jpmfs, index + 1, acc, list(new_index))
    #             entropy += (jpmfs[index][new_index] * acc[tmp_index])
    #     return entropy

    # Compute using Bayes' Theorem for entropy

    length = len(jpmfs)
    if index == (length - 1):
        return compute_joint_entropy(cmin, cmax, pmfs, jpmfs, 0, {}, [])
    else:
        full_entropy = compute_joint_entropy(cmin, cmax, pmfs, jpmfs, 0, {}, [])
        partial_entropy = compute_joint_entropy(cmin, cmax, pmfs[0:len(pmfs)-1], jpmfs[0:len(jpmfs)-1], 0, {}, [])

        if partial_entropy > full_entropy:
            print >> sys.stderr, "Error: entropy miscalculated %d %d %f %f" % (cmin, cmax, partial_entropy, full_entropy)
            # print pmfs
            # print jpmfs
            sys.exit()

        return (full_entropy - partial_entropy)

def compute_pair_conditional_entropy(pmfX, pmfY, pmfXY):
    '''
    NOTE: THIS IS DEPRECATED NOW

    Input:
        pmfX is map from (x) -> probability
        pmfY is map from (y) -> probability
        pmfXY is a map from (x, y) -> probability
    Output: conditional entropy
    '''
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
