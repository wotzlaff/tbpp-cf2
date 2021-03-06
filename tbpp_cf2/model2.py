from typing import Collection
import gurobipy as gp
from . import InstanceTBPPFU
from .util import pairwise, compute_conflict_cliques

__all__ = ['build', 'set_start']


def set_start(model: gp.Model, inst: InstanceTBPPFU, alloc: Collection[frozenset[int]]):
    model.update()
    # sort by first job
    alloc = sorted(alloc, key=lambda pat: min(pat))

    x = model._vars['x']
    z = model._vars['z']
    w = model._vars['w']

    for i, k in x:
        x[i, k].Start = 0

    for k in z:
        z[k].Start = 0

    for k, pat in enumerate(alloc):
        for i in pat:
            x[i, k].Start = 1
        z[k].Start = 1

    for t, k in w:
        if k >= len(alloc):
            w[t, k].Start = 0
            continue

        if t not in model._times['ts_k'][k]:
            w[t, k].Start = 0
            continue

        tk = model._times['t_k'][k]
        t0 = tk[0]
        if t == t0:
            w[t, k].Start = 1 if any(
                inst.s[i] <= t and inst.e[i] > t
                for i in alloc[k]
            ) else 0
        else:
            tp = next(tp for tp in reversed(tk) if tp < t)
            w[t, k].Start = 1 if any(
                inst.s[i] <= t and inst.e[i] > t
                for i in alloc[k]
            ) and not any(
                inst.s[i] <= tp and inst.e[i] > tp
                for i in alloc[k]
            ) else 0


def build(
    inst: InstanceTBPPFU,
    lb_servers: int = 0, ub_servers: int = 0,
    mods: set[str] = {'conflicts'},
):

    assert mods <= {'conflicts'}

    # idx set of items (jobs)
    idx_i = range(inst.n)
    n_servers = inst.n if ub_servers == 0 else ub_servers
    idx_k = range(n_servers)

    ts_k = {k: set(inst.s[k:]) for k in idx_k}
    te_k = {k: set(inst.e[k:]) for k in idx_k}
    t_k = {k: sorted(ts_k[k] | te_k[k]) for k in idx_k}

    tsnd_k = {
        k: {
            t0 for t0, t1 in pairwise(t_k[k])
            if t0 in ts_k[k] and t1 in te_k[k]
        }
        for k in idx_k
    }

    m = gp.Model()
    # add variables
    x = m.addVars(
        [(i, k) for i in idx_i for k in idx_k if k <= i],
        vtype=gp.GRB.BINARY, name='x'
    )
    w = m.addVars(
        [(l, k) for k in idx_k for l in ts_k[k]],
        obj=inst.gamma, vtype=gp.GRB.BINARY, name='w'
    )
    z = m.addVars(idx_k, obj=1, vtype=gp.GRB.BINARY, name='z')

    m._servers = z.sum()
    m._fireups = w.sum()
    m._vars = dict(x=x, z=z, w=w)
    m._times = dict(t_k=t_k, ts_k=ts_k, te_k=te_k)
    m._set_start = lambda alloc: set_start(m, inst, alloc)

    # exactly one server per job
    m.addConstrs((
        x.sum(i, '*') == 1
        for i in idx_i
    ), name='assign')

    m.addConstrs((
        gp.quicksum(
            inst.c[j] * x[j, k]
            for j in idx_i[:i+1] if j >= k and inst.s[i] < inst.e[j]
        ) <= inst.cap * z[k]
        for k in idx_k
        for i in idx_i
        if k <= i and inst.s[i] in tsnd_k[k]
    ), name='cap')
    m.addConstrs((
        x[i, k] <= z[k]
        for k in idx_k
        for i in idx_i
        if k <= i
    ), name='use')
    m.addConstrs((
        x[i, k] <= w[inst.s[i], k] +
        gp.quicksum(
            x[j, k]
            for j in idx_i[k:i]
            if inst.e[j] >= inst.s[i]
        )
        for k in idx_k
        for i in idx_i
        if k <= i
    ), name='fireup')

    # use bound on server count
    if lb_servers > 0:
        m.addConstr(
            sum(z[k] for k in idx_k[:lb_servers]) == lb_servers,
            name='lb_server'
        )

    # break symmetry
    m.addConstrs((
        z[k] >= z[k+1]
        for k in idx_k[lb_servers:-1]
    ), name='break_symmetry')

    # add VI
    m.addConstrs((
        z[k] <= w.sum('*', k)
        for k in idx_k
    ), name='server_fireup')

    if 'conflicts' in mods:
        ccs = compute_conflict_cliques(inst, n_servers)
        for k, cs_k in enumerate(ccs):
            for i, cs in cs_k.items():
                for l, c in enumerate(cs):
                    m.addConstr(
                        gp.quicksum(x[j, k] for j in c) <= z[k],
                        name=f'conflict[{k},{i},{l}]'
                    )

    return m
