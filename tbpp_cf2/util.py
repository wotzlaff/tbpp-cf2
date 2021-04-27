from itertools import tee
from .instance import InstanceTBPP

__all__ = ['pairwise', 'compute_conflict_cliques']


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def remove_small_or_dominated(cs: list[set[int]]) -> list[set[int]]:
    return [
        c for cp, c, cn in zip([set[int]()] + cs, cs, cs[1:] + [set[int]()])
        if len(c) > 1 and not (c <= cp or c <= cn)
    ]


def compute_cliques(inst: InstanceTBPP) -> list[set[int]]:
    ts = set(inst.s)
    te = set(inst.e)
    tse = ts | te
    ts_nd = {
        t0 for t0, t1 in pairwise(sorted(tse))
        if t0 in ts and t1 in te
    }
    return [
        {
            j
            for j in range(inst.n)
            if inst.s[j] <= t and t < inst.e[j]
        }
        for t in ts_nd
    ]


def compute_conflict_cliques(inst: InstanceTBPP, ub_servers: int):
    cliques = compute_cliques(inst)
    cs_0 = dict[int, list[set[int]]]()
    ccs = list[dict[int, list[set[int]]]]()
    # "large" cliques
    c0 = [
        {j for j in c if 2 * inst.c[j] > inst.cap}
        for c in cliques
    ]
    c0nd = remove_small_or_dominated(c0)
    if len(c0nd) > 0:
        cs_0[-1] = c0nd

    # item cliques
    for i in range(inst.n):
        ci = inst.c[i]
        if 2 * ci > inst.cap:
            continue
        c1 = [
            {j for j in c if ci + inst.c[j] > inst.cap} | {i}
            for c in cliques
            if i in c
        ]
        c1nd = remove_small_or_dominated(c1)
        if len(c1nd) == 0:
            continue
        cs_0[i] = c1nd
    ccs.append(cs_0)

    for k in range(ub_servers - 1):
        cs_k = {}
        for i, cs in cs_0.items():
            csnd = remove_small_or_dominated([
                c - {k}
                for c in cs
            ])
            if len(csnd) == 0:
                continue
            cs_k[i] = csnd
        ccs.append(cs_k)
        cs_0 = cs_k
    return ccs
