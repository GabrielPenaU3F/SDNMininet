import numpy as np

from abc import ABC, abstractmethod


class ArrivalProcess(ABC):

    @abstractmethod
    def interarrival_time(self) -> float:
        pass


class PoissonProcess(ArrivalProcess):

    def __init__(self, rate, seed=0):
        self.rate = rate
        self.rng = np.random.default_rng(seed)

    def interarrival_time(self):
        scale = 1 / self.rate
        return self.rng.exponential(scale)


PROCESS_TYPES = {
    "poisson": PoissonProcess,
}
