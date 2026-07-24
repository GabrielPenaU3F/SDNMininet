import numpy as np
import pandas as pd


def generate_poisson_statistics(
    *,
    lam: float,
    duration: float,
    sampling_interval: float,
    rng: np.random.Generator,
    n_switches: int = 2,
    n_ports: int = 2,
) -> pd.DataFrame:
    """
    Generates synthetic OpenFlow statistics.

    Each (switch, port) pair carries an independent Poisson process
    of intensity ``lam``.
    """

    poll_times = np.arange(
        0.0,
        duration + sampling_interval,
        sampling_interval,
    )

    rows = []

    for switch_id in range(1, n_switches + 1):
        for port_no in range(1, n_ports + 1):

            arrivals = np.cumsum(
                rng.exponential(
                    scale=1 / lam,
                    size=int(lam * duration * 5),
                )
            )

            arrivals = arrivals[arrivals <= duration]

            counters = np.searchsorted(arrivals, poll_times)

            for poll_id, (t, count) in enumerate(zip(poll_times, counters)):
                rows.append(
                    {
                        'poll_id': poll_id,
                        'timestamp': t,
                        'switch_id': switch_id,
                        'port_no': port_no,
                        'rx_packets': count,
                    }
                )

    return pd.DataFrame(rows)