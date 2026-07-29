import numpy as np

from abc import ABC, abstractmethod
from scipy.optimize import curve_fit


class ArrivalProcess(ABC):

    def __init__(self, seed=0, initial_state=0, **kwargs):
        self._validate_model_parameters()
        self._initial_state = initial_state
        self._rng = np.random.default_rng(seed)

    @staticmethod
    @abstractmethod
    def mvf_function(t, *params):
        pass

    @abstractmethod
    def _validate_model_parameters(self):
        pass


    @abstractmethod
    def interarrival_time(self, *args) -> float:
        pass

    def mvf(self, t):
        return self._initial_state + self.mvf_function(t, *self.parameters)

    def fit(self, x, y):
       optimal_params, cov = curve_fit(self.mvf_function, x, y,
                                       p0=self.parameters,
                                       method='trf',
                                       bounds=self.bounds)
       return tuple(optimal_params)

    @property
    @abstractmethod
    def parameters(self):
        pass

    @property
    @abstractmethod
    def bounds(self):
        pass


class PoissonProcess(ArrivalProcess):

    def __init__(self, rate, seed=0, initial_state=0):
        self.rate = rate

        super().__init__(seed=seed, initial_state=initial_state)

    def interarrival_time(self, *args) -> float:
        scale = 1 / self.rate
        return self._rng.exponential(scale)

    @staticmethod
    def mvf_function(t, lam):
        return lam * t

    def _validate_model_parameters(self):
        if not self.rate > 0:
            raise ValueError('Poisson rate must be strictly positive')

    @property
    def parameters(self):
        return (self.rate,)

    @property
    def bounds(self):
        return 0, +np.inf


class BPM3pProcess(ArrivalProcess):

    def __init__(self, beta, gamma, rho, seed=0, initial_state=0):
        self.beta = beta
        self.gamma = gamma
        self.rho = rho

        super().__init__(seed=seed, initial_state=initial_state)

    @staticmethod
    def mvf_function(t, beta, gamma, rho):
        r = beta / gamma
        p = np.exp(-gamma * BPM3pProcess._Kappa_s_t(0, t, rho))
        return r * (1 - p) / p

    def interarrival_time(self, k, s) -> float:
        return self._inverse_cdf(self.gamma, self.beta, self.rho, k, s)

    @staticmethod
    def _kappa_t(t, rho):
        return 1/(1 + rho * t)

    @staticmethod
    def _Kappa_s_t(s, t, rho):
        return (1/rho) * np.log((1 + rho * t)/(1 + rho * s))

    def _validate_model_parameters(self):
        if any(x <= 0 for x in (self.beta, self.gamma, self.rho)):
            raise ValueError('BPM-3p parameters must be strictly positive')

    def _inverse_cdf(self, gamma, beta, rho, k, s):
        random = self._rng.random()
        exponent = -rho / (beta + gamma * k)
        second_factor = np.power(1 - random, exponent)
        return ((1 + rho * s) * second_factor - 1) / rho

    @property
    def parameters(self):
        return self.beta, self.gamma, self.rho

    @property
    def bounds(self):
        return [1e-3, 1e-3, 1e-3], [+np.inf, +np.inf, +np.inf]


PROCESS_TYPES = {
    'poisson': PoissonProcess,
    'bpm3p': BPM3pProcess
}
