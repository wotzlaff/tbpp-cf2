import dataclasses
from collections.abc import Collection
from random import randint

Pattern = frozenset[int]
Allocation = list[Pattern]

__all__ = ['InstanceTBPP', 'InstanceTBPPFU']

@dataclasses.dataclass
class InstanceTBPP:
    s: list[int]
    e: list[int]
    c: list[int]
    cap: int

    @property
    def n(self) -> int:
        return len(self.s)

    def sorted(self):
        s, e, c = [list(t) for t in zip(*sorted(zip(self.s, self.e, self.c)))]
        return InstanceTBPP(s, e, c, self.cap)

    def is_feasible(self, alloc: Allocation):
        for pat in alloc:
            for j in pat:
                load = sum(
                    self.c[i] for i in pat if self.s[i]
                    <= self.s[j] and self.e[i] > self.s[j]
                )
                if load > self.cap:
                    return False
        at_most_once = sum(len(pat) for pat in alloc) == self.n
        at_least_once = all(
            any(i in pat for pat in alloc)
            for i in range(self.n)
        )
        return at_most_once and at_least_once

    def compute_value(self, alloc: Allocation) -> float:
        return len(alloc)

    def sub(self, subset: Collection[int]):
        s = [self.s[i] for i in subset]
        e = [self.e[i] for i in subset]
        c = [self.c[i] for i in subset]
        return InstanceTBPP(s, e, c, self.cap)

    @classmethod
    def random(cls, n: int, cap: int, max_s: int = 10, max_dt: int = 10, min_c: int = 1, max_c: int = -1):
        if max_c == -1:
            max_c = cap
        s = [randint(1, max_s) for _ in range(n)]
        e = [si + randint(1, max_dt) for si in s]
        c = [randint(min_c, max_c) for _ in range(n)]
        return InstanceTBPP(s, e, c, cap).sorted()

    @property
    def jobs_for_time(self):
        return {
            t: {i for i in range(self.n) if self.s[i] <= t and t < self.e[i]}
            for t in set(self.s)
        }


@dataclasses.dataclass
class InstanceTBPPFU(InstanceTBPP):
    gamma: float

    @staticmethod
    def extend(inst: InstanceTBPP, gamma: float):
        return InstanceTBPPFU(**dataclasses.asdict(inst), gamma=gamma)

    def compute_value(self, alloc: Allocation) -> float:
        fireups = 0
        for pat in alloc:
            last_e = float('-inf')
            for j in sorted(pat):
                if self.s[j] > last_e:
                    fireups += 1
                last_e = max(last_e, self.e[j])
        servers = len(alloc)
        return servers + self.gamma * fireups

    def sorted(self):
        return InstanceTBPPFU.extend(super().sorted(), self.gamma)

    def sub(self, subset: Collection[int]):
        return InstanceTBPPFU.extend(super().sub(subset), self.gamma)

    @classmethod
    def random(cls, n: int, cap: int, max_s: int = 10, max_dt: int = 10, min_c: int = 1, max_c: int = -1, gamma: float = 1.0):
        return InstanceTBPPFU.extend(super().random(n, cap, max_s, max_dt, min_c, max_c), gamma)
