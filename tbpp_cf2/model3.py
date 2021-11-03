from typing import Collection, Optional
import gurobipy as gp
from . import InstanceTBPPFU

__all__ = ['build', 'set_start']


def set_start(model: gp.Model, inst: InstanceTBPPFU, alloc: Collection[frozenset[int]]):
    model.update()

    x = model._vars['x']
    w = model._vars['w']

    for i, k in x:
        x[i, k].Start = 0

    for pat in alloc:
        spat = sorted(pat)
        k = spat[0]
        for idx, i in enumerate(spat):
            x[i, k].Start = 1
            w[i].Start = 0 if any(
                inst.e[j] >= inst.s[i]
                for j in spat[:idx]
            ) else 1


def build(
    inst: InstanceTBPPFU,
    lb_servers: int = 0,
    ub_servers: Optional[int] = None,
    mods={'vi1', 'vi2', 'dominance'},
):

    assert set(mods) <= {
        'vi1', 'vi2',
        'dominance',
        'continuous_w'
    }

    idx_i = range(inst.n)
    m = gp.Model()

    # add variables
    x = m.addVars(
        [
            (i, k)
            for i in idx_i
            for k in idx_i[:i + 1]
            if (
                k == i or
                inst.e[k] <= inst.s[i] or
                inst.c[i] + inst.c[k] <= inst.cap
            )
        ],
        vtype=gp.GRB.BINARY,
        name='x'
    )
    w = m.addVars(
        idx_i,
        vtype=gp.GRB.CONTINUOUS if 'continuous_w' in mods else gp.GRB.BINARY,
        name='w'
    )

    m._vars = dict(x=x, w=w)
    m._set_start = lambda alloc: set_start(m, inst, alloc)

    servers = gp.quicksum(x[i, i] for i in idx_i)
    fireups = w.sum()
    m.setObjective(servers + inst.gamma * fireups, gp.GRB.MINIMIZE)
    m._servers = servers
    m._fireups = fireups

    # exactly one server per job
    m.addConstrs((
        x.sum(i, '*') == 1
        for i in idx_i
    ), name='assign')

    # capacity constraints
    use_dominance = 'dominance' in mods

    m.addConstrs((
        gp.quicksum(
            inst.c[j] * x[j, k]
            for j in idx_i[:i + 1]
            if (j, k) in x and inst.e[j] > inst.s[i]
        ) <= inst.cap * x[k, k]
        for (i, k) in x
        if k != i and (
            not use_dominance or
            i == max(
                j for j in idx_i
                if inst.s[i] == inst.s[j] and (j, k) in x
            )
        )
    ), name='cap')

    # fireup constraints
    m.addConstrs((
        x[i, k] <= w[i] + gp.quicksum(
            x[j, k]
            for j in idx_i[:i]
            if (j, k) in x and inst.e[j] >= inst.s[i]
        )
        for (i, k) in x
    ), name='fireup')

    # use bound on server count
    if lb_servers > 0:
        m.addConstr(
            sum(x[k, k] for k in idx_i) >= lb_servers,
            name='lb_server'
        )

    if 'vi1' in mods:
        # add VI
        m.addConstrs((
            x[k, k] <= w[k]
            for k in idx_i
        ), name='use_fireup')

    if 'vi2' in mods:
        m.addConstrs((
            x[i, k] <= x[k, k]
            for (i, k) in x
            if k != i
        ), name='assign_use')

    return m
