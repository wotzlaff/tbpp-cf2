import math
import time
import tbpp_cf2
import gurobipy as gp


def read_bounds():
    res = {}
    with open('./data/lb_servers_1.csv') as f:
        for line in f.readlines()[1:]:
            inst_name, value = line.split(',')
            res[inst_name] = int(value)
    return res


def main():
    root = './data/TestInstances'
    groups = tbpp_cf2.data.format1.get_groups(root)

    lb_servers_dict = read_bounds()
    gamma = 1.0

    log = open('./data/log_1.csv', 'w')
    log.write(
        'inst_name,model_name,nvar,ncon,nnz,dt_model,dt_solve,dt_relax,solved,val,val_relax,servers,fireups\n'
    )

    for n, t, cat in groups:
        group_name = f'n{n} t{t} {cat}'
        for inst_name, inst in tbpp_cf2.data.format1.read_instances(root, group_name):
            # lift instance
            inst = tbpp_cf2.lift(inst).sorted()
            inst = tbpp_cf2.InstanceTBPPFU.extend(inst, gamma=gamma)

            # apply heuristic
            alloc = tbpp_cf2.heuristic.best_look_ahead(
                inst, {1, 2, 3, 5, 10, 20, inst.n // 4, inst.n // 2, inst.n}
            )
            vheu = inst.compute_value(alloc)
            ub_servers = int(
                math.ceil(round(vheu) / (1.0 + inst.gamma) - 1e-8))
            lb_servers = lb_servers_dict[inst_name]
            print(
                f'''
{inst_name}
heuristic value = {vheu:.0f}
minimal server count = {lb_servers}
maximal server count = {ub_servers}'''
            )

            # build and solve compact model
            for model_name, build in [
                ('model1', tbpp_cf2.model1.build),
                ('model2', tbpp_cf2.model2.build),
                ('model3', tbpp_cf2.model3.build),
            ]:
                t0 = time.time()
                model = build(
                    inst,
                    lb_servers=lb_servers,
                    ub_servers=ub_servers,
                )
                model.setParam('OutputFlag', 0)
                model.setParam('TimeLimit', 1800)
                model.update()
                model._set_start(alloc)
                dt_model = time.time() - t0

                t0 = time.time()
                model.optimize()
                dt_solve = time.time() - t0

                if model.Status == gp.GRB.Status.INTERRUPTED:
                    raise KeyboardInterrupt()
                solved = model.Status == gp.GRB.Status.OPTIMAL
                val = model.ObjVal
                servers = model._servers.getValue()
                fireups = model._fireups.getValue()

                model_relax = model.relax()
                t0 = time.time()
                model_relax.optimize()
                if model_relax.Status == gp.GRB.Status.INTERRUPTED:
                    raise KeyboardInterrupt()
                assert model_relax.Status == gp.GRB.Status.OPTIMAL
                val_relax = model_relax.ObjVal
                dt_relax = time.time() - t0

                log.write(
                    f'{inst_name},{model_name},{model.NumVars},{model.NumConstrs},{model.NumNZs},{dt_model},{dt_solve},{dt_relax},{solved},{val:.0f},{val_relax},{servers:.0f},{fireups:.0f}\n'
                )
                log.flush()


if __name__ == '__main__':
    main()
