import glob
import os
import numpy as np
from .. import InstanceTBPP

__all__ = ['read_file', 'get_groups', 'read_instances']


def read_file(filename):
    raw = np.loadtxt(filename, dtype=int)
    n = raw[0, 0]
    cap = raw[0, 1]
    s = raw[1:, 1].tolist()
    e = raw[1:, 2].tolist()
    c = raw[1:, 3].tolist()
    return InstanceTBPP(s=s, e=e, c=c, cap=cap)


def get_groups(root):
    groups = []
    for group_path in sorted(glob.glob(os.path.join(root, '*'))):
        group_name = os.path.basename(group_path)
        tmp = group_name.split(' ')
        groups.append((int(tmp[0][1:]), int(tmp[1][1:]), tmp[2]))

    groups = sorted(groups)
    return groups


def read_instances(root, group_name):
    for inst_path in sorted(glob.glob(os.path.join(root, group_name, '*.txt'))):
        inst_name = os.path.basename(inst_path)
        inst = read_file(inst_path)
        yield inst_name, inst
