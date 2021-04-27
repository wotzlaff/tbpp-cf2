import copy
import dataclasses
import gurobipy as gp
from .instance import InstanceTBPP

__all__ = ['lift']


@dataclasses.dataclass
class InstanceKP:
    a: list[int]
    c: list[int]
    cap: int

    def __post_init__(self):
        assert self.n == len(self.c)

    @property
    def n(self):
        return len(self.a)


def solve_knapsack(inst: InstanceKP):
    m = gp.Model()
    m.setParam('OutputFlag', 0)
    x = m.addVars(inst.n, obj=inst.c, vtype=gp.GRB.BINARY, name='x')
    m.addConstr(gp.quicksum(
        inst.a[i] * x[i]
        for i in range(inst.n)
    ) <= inst.cap)
    m.setAttr('ModelSense', gp.GRB.MAXIMIZE)
    m.optimize()
    return int(m.ObjVal + 0.5)


def lift(inst: InstanceTBPP):
    idx_i = range(inst.n)
    idx_a = {
        i: {
            j for j in idx_i
            if max(inst.s[i], inst.s[j]) < min(inst.e[i], inst.e[j])
        } - {i}
        for i in idx_i
    }
    cn = list(inst.c)
    for i in idx_i:
        coeff = [cn[j] for j in idx_a[i]]
        rhs = inst.cap - cn[i]
        eps = solve_knapsack(InstanceKP(coeff, coeff, rhs))
        cn[i] = inst.cap - eps

    lifted_inst = copy.copy(inst)
    lifted_inst.c = cn
    return lifted_inst
