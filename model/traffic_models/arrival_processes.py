import numpy as np

from abc import ABC, abstractmethod
from scipy.optimize import curve_fit


class ArrivalProcess(ABC):

    def __init__(self, seed=0, **kwargs):
        self.initial_state = 0
        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def interarrival_time(self, *args) -> float:
        pass

    @abstractmethod
    def mvf(self, t, *args, **kwargs):
        pass

    def fit(self, x, y):
       optimal_params, cov = curve_fit(self.mvf, x, y, p0=self.model_params,
                                       method='trf', bounds=self.bounds)
       return tuple(optimal_params)

    @property
    @abstractmethod
    def model_params(self):
        pass

    @property
    @abstractmethod
    def bounds(self):
        pass


class PoissonProcess(ArrivalProcess):

    def __init__(self, rate, seed=0, **kwargs):
        super().__init__(seed=seed, **kwargs)
        self.rate = rate

    def interarrival_time(self, *args) -> float:
        scale = 1 / self.rate
        return self.rng.exponential(scale)

    def mvf(self, t, lam, *args, **kwargs):
        return lam * t

    @property
    def model_params(self):
        return self.rate

    @property
    def bounds(self):
        return 0, +np.inf


class BPM3pProcess(ArrivalProcess):

    def __init__(self, beta, gamma, rho, seed=0, initial_state=0, **kwargs):
        super().__init__(seed=seed, **kwargs)
        self._validate_model_parameters(beta, gamma, rho)
        self.beta = beta
        self.gamma = gamma
        self.rho = rho
        self.initial_state = initial_state

    def mvf(self, t, gamma, beta, rho, *args, **kwargs):
        r = beta / gamma
        p = np.exp(-gamma * self._Kappa_s_t(0, t, rho))
        return self.initial_state + r * (1 - p) / p

    def interarrival_time(self, k, s) -> float:
        return self._inverse_cdf(self.gamma, self.beta, self.rho, k, s)

    @staticmethod
    def _kappa_t(t, rho):
        return 1/(1 + rho * t)

    @staticmethod
    def _Kappa_s_t(s, t, rho):
        return (1/rho) * np.log((1 + rho * t)/(1 + rho * s))

    @staticmethod
    def _validate_model_parameters(beta, gamma, rho):
        if not rho > 0:
            raise ValueError('BPM-3p parameters must be strictly positive')
        return gamma, beta, rho

    @staticmethod
    def _inverse_cdf(gamma, beta, rho, k, s):
        random = np.random.rand()
        exponent = -rho / (beta + gamma * k)
        second_factor = np.power(1 - random, exponent)
        return ((1 + rho * s) * second_factor - 1) / rho

    @property
    def model_params(self):
        return self.beta, self.gamma, self.rho

    @property
    def bounds(self):
        return [0, 0, 0], [+np.inf, +np.inf, +np.inf]


PROCESS_TYPES = {
    'poisson': PoissonProcess,
    'bpm3p': BPM3pProcess
}
