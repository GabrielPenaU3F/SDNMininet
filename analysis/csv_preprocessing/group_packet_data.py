from pathlib import Path
from sys import argv

import pandas as pd


'''
This preprocessing assumes that all port statistics belonging to the same polling cycle 
fall within the same aggregation window. Therefore, the aggregation window
(i.e., sampling frequency of the monitor) should be chosen significantly larger 
than the controller polling jitter.
'''
def normalize_traffic_statistics(input_csv: Path, output_csv: Path,
    switch_id: int = -1, timestamp_scale: float = 1.0, from_zero: bool = False) -> None:
    """
    Converts statistics to the format

        measurement timestamp, cumulative packets

    Parameters
    ----------
    input_csv
        Input file path

    output_csv
        Output file path

    switch_id
        If it is none, every switch is included.
        Otherwise, the indicated switch is chosen.

    timestamp_scale
        Unit conversion factor.

    """
    df = pd.read_csv(input_csv)

    # Optional filtering
    if switch_id != -1:
        df = df[df['switch_id'] == switch_id]

    if df.empty:
        raise ValueError('No measurements remain after filtering')

    # Normalize timestamps
    t0 = df['timestamp'].min()
    df['timestamp'] = (df['timestamp'] - t0) * timestamp_scale

    # Keep the last measurement for each (poll, switch, port)
    df = (
        df.sort_values('timestamp')
        .groupby(
            ['poll_id', 'switch_id', 'port_no'],
            as_index=False
        )
        .last()
    )

    # Remove incomplete polling rounds
    rows_per_poll = df.groupby('poll_id').size()
    expected_rows = rows_per_poll.max()

    valid_polls = rows_per_poll[rows_per_poll == expected_rows].index

    df = df[df['poll_id'].isin(valid_polls)]

    # Aggregate counters across ports
    df = (
        df.groupby('poll_id', as_index=False)
        .agg(
            timestamp=('timestamp', 'min'),
            packets=('rx_packets', 'sum'),
        )
    )

    # Optional: translate counter so it starts at zero
    if from_zero:
        df['packets'] -= df['packets'].iloc[0]

    # Round timestamps
    df['timestamp'] = df['timestamp'].round(3)

    # Remove poll_id
    df = df[['timestamp', 'packets']]

    df.to_csv(output_csv, index=False)


if __name__ == '__main__':

    input_csv, output_csv, switch_id, scale = [argv[1], argv[2], argv[3], argv[4]]
    normalize_traffic_statistics(Path(input_csv), Path(output_csv),
         switch_id=int(switch_id), timestamp_scale=float(scale))
