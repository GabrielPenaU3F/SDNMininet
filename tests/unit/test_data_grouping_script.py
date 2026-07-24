from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from analysis.csv_preprocessing.group_packet_data import (
    normalize_traffic_statistics,
)
from tests.utilities.traffic_statistics_generation import generate_poisson_statistics


def read_output(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


@pytest.fixture
def input_csv(tmp_path):
    return tmp_path / 'input.csv'

@pytest.fixture
def output_csv(tmp_path):
    return tmp_path / 'output.csv'

@pytest.fixture
def multiple_switch_port_df(input_csv):
    pd.DataFrame(
        {
            'poll_id': [
                0, 0, 0, 0,
                1, 1, 1, 1,
            ],
            'timestamp': [
                0, 0, 0, 0,
                1, 1, 1, 1,
            ],
            'switch_id':[
                1, 1, 2, 2,
                1, 1, 2, 2,
            ],
            'port_no':[
                1, 2, 1, 2,
                1, 2, 1, 2,
            ],
            'rx_packets': [
                3, 4, 5, 6,
                5, 6, 7, 8,
            ],
        }
    ).to_csv(input_csv, index=False)


def test_single_switch_single_port(input_csv, output_csv):

    pd.DataFrame(
        {
            'poll_id': [0, 1, 2, 3, 4],
            'timestamp': [0.1, 1.1, 2.1, 3.1, 4.1],
            'switch_id': [1] * 5,
            'port_no': [1] * 5,
            'rx_packets': [0, 2, 5, 7, 11],
        }
    ).to_csv(input_csv, index=False)

    normalize_traffic_statistics(input_csv, output_csv)

    result = read_output(output_csv)

    expected = pd.DataFrame(
        {
            'timestamp': [0.0, 1.0, 2.0, 3.0, 4.0],
            'packets': [0, 2, 5, 7, 11],
        }
    )

    pd.testing.assert_frame_equal(result, expected)

def test_multiple_ports_are_summed(input_csv, output_csv):

    pd.DataFrame(
        {
            'poll_id': [0, 0, 1, 1, 2, 2],
            'timestamp': [0, 0, 1, 1, 2, 2],
            'switch_id': [1] * 6,
            'port_no': [1, 2, 1, 2, 1, 2],
            'rx_packets': [3, 4, 5, 6, 7, 8],
        }
    ).to_csv(input_csv, index=False)

    normalize_traffic_statistics(input_csv, output_csv)

    result = read_output(output_csv)

    expected = pd.DataFrame(
        {
            'timestamp': [0., 1., 2.],
            'packets': [7, 11, 15],
        }
    )

    pd.testing.assert_frame_equal(result, expected)

def test_input_order_does_not_matter(input_csv, output_csv):

    df = pd.DataFrame(
        {
            'poll_id': [1, 0, 2, 0, 1, 2],
            'timestamp': [1, 0, 2, 0, 1, 2],
            'switch_id': [1] * 6,
            'port_no': [2, 1, 2, 2, 1, 1],
            'rx_packets': [6, 3, 8, 4, 5, 7],
        }
    )

    df.to_csv(input_csv,index=False)

    normalize_traffic_statistics(input_csv,output_csv)

    result = read_output(output_csv)

    expected = pd.DataFrame(
        {
            'timestamp': [0., 1., 2.],
            'packets': [7, 11, 15],
        }
    )

    pd.testing.assert_frame_equal(result,expected)

def test_multiple_switches_are_summed(input_csv, output_csv):

    pd.DataFrame(
        {
            'poll_id': [0, 0, 1, 1],
            'timestamp': [0, 0, 1, 1],
            'switch_id': [1, 2, 1, 2],
            'port_no': [1, 1, 1, 1],
            'rx_packets': [10, 20, 15, 30],
        }
    ).to_csv(input_csv,index=False)

    normalize_traffic_statistics(input_csv,output_csv)

    result = read_output(output_csv)

    expected = pd.DataFrame(
        {
            'timestamp': [0., 1.],
            'packets': [30, 45],
        }
    )

    pd.testing.assert_frame_equal(result,expected)

def test_incomplete_poll_is_removed(input_csv, output_csv):

    pd.DataFrame(
        {
            'poll_id':[
                0, 0,
                1, 1,
                2
            ],
            'timestamp':[
                0, 0,
                1, 1,
                2
            ],
            'switch_id':[
                1, 2,
                1, 2,
                1
            ],
            'port_no':[
                1, 1,
                1, 1,
                1
            ],
            'rx_packets':[
                10, 20,
                15, 30,
                18
            ],
        }
    ).to_csv(input_csv,index=False)

    normalize_traffic_statistics(input_csv,output_csv)

    result = read_output(output_csv)

    assert len(result) == 2

def test_multiple_switches_multiple_ports(input_csv, output_csv, multiple_switch_port_df):

    normalize_traffic_statistics(input_csv, output_csv)

    result = read_output(output_csv)

    expected = pd.DataFrame(
        {
            'timestamp': [0., 1.],
            'packets': [18, 26],
        }
    )

    pd.testing.assert_frame_equal(result, expected)

def test_filter_by_switch_id(input_csv, multiple_switch_port_df, tmp_path):

    output_1 = tmp_path / 'output_1'
    output_2 = tmp_path / 'output_2'

    normalize_traffic_statistics(
        input_csv,
        output_csv=output_1,
        switch_id=1
    )

    normalize_traffic_statistics(
        input_csv,
        output_csv=output_2,
        switch_id=2
    )

    result_1 = read_output(output_1)
    result_2 = read_output(output_2)

    expected_1 = pd.DataFrame(
        {
            'timestamp': [0., 1.],
            'packets': [7, 11],
        }
    )

    expected_2 = pd.DataFrame(
        {
            'timestamp': [0., 1.],
            'packets': [11, 15],
        }
    )

    pd.testing.assert_frame_equal(result_1, expected_1)
    pd.testing.assert_frame_equal(result_2, expected_2)

def test_poisson_single_port_statistics(tmp_path):

    rng = np.random.default_rng(1234)

    lam = 5.0
    duration = 60.0
    sampling = 0.2

    n_realizations = 50

    average_packets = None
    timestamps = None

    for i in range(n_realizations):

        input_csv = tmp_path / f'input_{i}.csv'
        output_csv = tmp_path / f'output_{i}.csv'

        generate_poisson_statistics(
            lam=lam,
            duration=duration,
            sampling_interval=sampling,
            rng=rng,
            n_ports=1,
            n_switches=1
        ).to_csv(input_csv, index=False)

        normalize_traffic_statistics(
            input_csv,
            output_csv,
        )

        result = pd.read_csv(output_csv)

        if average_packets is None:
            timestamps = result['timestamp'].to_numpy()
            average_packets = result['packets'].to_numpy(dtype=float)
        else:
            average_packets += result['packets'].to_numpy(dtype=float)

    average_packets /= n_realizations

    slope, _ = np.polyfit(timestamps, average_packets, deg=1)

    np.testing.assert_almost_equal(slope, lam, decimal=2)

def test_superposition_of_poisson_processes(tmp_path):

    rng = np.random.default_rng(1234)

    lam = 5.0
    duration = 60.0
    sampling = 0.2

    n_switches = 2
    n_ports = 2

    n_realizations = 50

    average_packets = None
    timestamps = None

    expected_lambda = lam * n_switches * n_ports

    for i in range(n_realizations):

        input_csv = tmp_path / f'input_{i}.csv'
        output_csv = tmp_path / f'output_{i}.csv'

        generate_poisson_statistics(
            lam=lam,
            duration=duration,
            sampling_interval=sampling,
            rng=rng,
            n_switches=n_switches,
            n_ports=n_ports,
        ).to_csv(input_csv, index=False)

        normalize_traffic_statistics(
            input_csv,
            output_csv,
        )

        result = pd.read_csv(output_csv)

        if average_packets is None:
            timestamps = result['timestamp'].to_numpy()
            average_packets = result['packets'].to_numpy(dtype=float)
        else:
            average_packets += result['packets'].to_numpy(dtype=float)

    average_packets /= n_realizations

    slope, _ = np.polyfit(timestamps, average_packets, deg=1)

    assert np.abs(expected_lambda - slope < 0.15)