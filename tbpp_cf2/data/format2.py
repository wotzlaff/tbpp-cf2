import glob
import os
import re
from .. import InstanceTBPP

__all__ = ['read_file', 'read_instances']


def read_file(f):
    lines = open(f).read().split('\n')
    n, cap, taus = [int(v) for v in lines[0].split('\t')]
    c = [int(ci) for ci in lines[1:][:n]]
    rem = lines[3+n:]
    s = [-1] * n
    e = [-1] * n
    active = set()
    for t, step in enumerate(rem):
        items = set([int(v) for v in step.split('\t') if len(v) > 0])
        for item in active.copy():
            if item not in items:
                active.remove(item)
                e[item] = t
        for item in items:
            if item not in active:
                active.add(item)
                s[item] = t
    tlast = len(rem)
    for item in active:
        e[item] = tlast
    return InstanceTBPP(s=s, e=e, c=c, cap=cap)


def read_instances(root):
    files = glob.glob(os.path.join(root, '*.txt'))
    instances = []
    for f in files:
        b = os.path.basename(f)
        m = re.search('I_(?P<it>\d+)\.txt_(?P<tau>\d+)_(?P<cap>\d+)\.txt', b)
        if m is None:
            continue
        res = dict(
            it=int(m.group('it')),
            tau=int(m.group('tau')),
            cap=int(m.group('cap')),
            file=b,
        )
        res['cls'] = 1 + (res['it'] - 1) // 10
        instances.append(res)
    return instances
