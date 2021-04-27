import math
import tbpp_cf2


def main():
    # generate and lift a random instance
    inst = tbpp_cf2.InstanceTBPP.random(20, 100)
    inst = tbpp_cf2.lift(inst)
    inst = tbpp_cf2.InstanceTBPPFU.extend(inst, gamma=1.0)

    # apply heuristic
    alloc = tbpp_cf2.heuristic.best_look_ahead(inst, {1, 2, 3, 4, 5, 10})
    vheu = inst.compute_value(alloc)
    ub_servers = int(math.ceil(round(vheu) / (1.0 + inst.gamma) - 1e-8))
    print(f'heuristic value = {vheu}\nmaximal server count = {ub_servers}')

    # build a model and solve it
    model = tbpp_cf2.model1.build(inst, ub_servers=ub_servers)
    model.optimize()
    print(f'''
z* = {model.ObjVal:.0f}
servers = {model._servers.getValue():.0f}
fireups = {model._fireups.getValue():.0f}''')


if __name__ == '__main__':
    main()
