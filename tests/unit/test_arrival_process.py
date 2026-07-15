import numpy as np
import pytest

from model.traffic_models.arrival_processes import PoissonProcess, ArrivalProcess


class TestBaseClass:

    # noinspection PyAbstractClass
    def test_arrival_process_is_abstract(self):
        with pytest.raises(TypeError):
            ArrivalProcess()


@pytest.fixture
def make_n_poisson_times():
    def _make(rate, seed, n=100):
        poisson = PoissonProcess(rate=rate, seed=seed)
        times = np.array([poisson.interarrival_time() for _ in range(n)])
        return times
    return _make

class TestPoisson:

    def test_interarrival_times_are_positive(self, make_n_poisson_times):
        times = make_n_poisson_times(rate=1, seed=0)
        assert np.all(times > 0)

    def test_same_seed_generates_same_arrivals(self, make_n_poisson_times):
        times_1 = make_n_poisson_times(rate=10, seed=0)
        times_2 = make_n_poisson_times(rate=10, seed=0)
        assert np.allclose(times_1, times_2)

    def test_different_seed_generates_different_arrivals(self, make_n_poisson_times):
        times_1 = make_n_poisson_times(rate=10, seed=0)
        times_2 = make_n_poisson_times(rate=10, seed=42)
        assert not np.allclose(times_1, times_2)

    # Warning: this test only works due to ergodicity.
    # For non-ergodic processes, one should generate independent trajectories
    def test_interarrival_time_mean_matches_theoretical_mean(self, make_n_poisson_times):
        rate = 5.0
        n = 2000
        times = make_n_poisson_times(rate=rate, seed=0, n=n)
        sample_mean = np.mean(times)
        theoretical_mean = 1.0 / rate
        assert sample_mean == pytest.approx(theoretical_mean, rel=0.05)

