import numpy as np
import pytest

from traffic_models.arrival_processes import PoissonProcess, ArrivalProcess, BPM3pProcess


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

@pytest.fixture
def poisson_process():
    return PoissonProcess(5)

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

    def test_default_seed_is_zero(self):
        p1 = PoissonProcess(rate=1)
        p2 = PoissonProcess(rate=1, seed=0)
        arrivals1 = [p1.interarrival_time() for _ in range(100)]
        arrivals2 = [p2.interarrival_time() for _ in range(100)]
        assert np.allclose(arrivals1, arrivals2)

    def test_default_initial_state_is_zero(self, poisson_process):
        assert poisson_process._initial_state == 0

    def test_mvf_respects_initial_state(self):
        process = PoissonProcess(rate=5, initial_state=10)
        t = np.array([0.0, 1.0, 2.0])
        expected = np.array([10.0, 15.0, 20.0])
        assert np.allclose(process.mvf(t), expected)

    def test_mvf_and_mvf_function_are_consistent(self, poisson_process):
        t = np.linspace(0, 10)
        assert np.allclose(
            poisson_process.mvf(t),
            poisson_process._initial_state +
            poisson_process.mvf_function(t, *poisson_process.parameters)
        )

    def test_curve_fit_returns_correct_lambda(self, poisson_process):
        rng = np.random.default_rng(0)
        lam = 5
        x = np.linspace(0, 100, 200)
        noise = rng.normal(0, 2, size=x.size)
        y = lam * x + noise
        estimated, = poisson_process.fit(x, y)
        assert estimated == pytest.approx(lam, rel=0.05)

    @pytest.mark.parametrize('rate', [0, -1])
    def test_poisson_rate_must_be_positive(self, rate):
        with pytest.raises(ValueError, match='Poisson rate must be strictly positive'):
            PoissonProcess(rate)


@pytest.fixture
def bpm_process():
    return BPM3pProcess(beta=2.0, gamma=1.0, rho=0.5)


@pytest.fixture
def make_n_bpm_times():
    def _make(beta, gamma, rho, seed, n=100):
        bpm = BPM3pProcess(beta=beta, gamma=gamma, rho=rho, seed=seed)
        times = []
        current_time = 0.0

        for k in range(n):
            current_time = bpm.interarrival_time(k, current_time)
            times.append(current_time)

        return np.array(times)

    return _make


class TestBPM3p:

    def test_interarrival_times_are_strictly_increasing(self, make_n_bpm_times):
        times = make_n_bpm_times(beta=2, gamma=1, rho=0.5, seed=0)
        assert np.all(np.diff(times) > 0)

    def test_mvf_matches_closed_form(self, bpm_process):
        t = np.linspace(0, 10, 100)

        expected = (
            bpm_process.beta / bpm_process.gamma
            * (
                np.exp(
                    bpm_process.gamma
                    * BPM3pProcess._Kappa_s_t(0, t, bpm_process.rho)
                )
                - 1
            )
        )

        assert np.allclose(bpm_process.mvf(t), expected)

    def test_curve_fit_recovers_parameters(self, bpm_process):
        rng = np.random.default_rng(0)

        beta = 2.0
        gamma = 1.0
        rho = 0.5

        process = BPM3pProcess(beta, gamma, rho)

        x = np.linspace(0, 20, 200)
        y = process.mvf(x)
        y += rng.normal(0, 0.02, size=x.size)

        beta_hat, gamma_hat, rho_hat = process.fit(x, y)

        assert beta_hat == pytest.approx(beta, rel=0.05)
        assert gamma_hat == pytest.approx(gamma, rel=0.05)
        assert rho_hat == pytest.approx(rho, rel=0.05)

    @pytest.mark.parametrize(
        "beta,gamma,rho",
        [
            (0, 1, 1),
            (-1, 1, 1),
            (1, 0, 1),
            (1, -1, 1),
            (1, 1, 0),
            (1, 1, -1),
        ],
    )
    def test_parameters_must_be_positive(self, beta, gamma, rho):
        with pytest.raises(
            ValueError,
            match="BPM-3p parameters must be strictly positive",
        ):
            BPM3pProcess(beta, gamma, rho)