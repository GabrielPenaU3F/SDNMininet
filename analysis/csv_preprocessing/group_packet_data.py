from pathlib import Path
from sys import argv

import pandas as pd


'''
This preprocessing assumes that all port statistics belonging to the same polling cycle 
fall within the same aggregation window. Therefore, the aggregation window should be 
chosen significantly larger than the controller polling jitter.
'''
def normalize_traffic_statistics(input_csv: str, output_csv: str,
    switch_id: int = -1, timestamp_scale: float = 1.0) -> None:
    """
    Converts statistics to the format

        measurement timestamp, cumulative packets

    Parameters
    ----------
    switch_id
        If it is none, every switch is included.
        Otherwise, the indicated switch is chosen.

    timestamp_scale
        Unit conversion factor.

    """

    input_csv = Path(input_csv)
    output_csv = Path(output_csv)
    df = pd.read_csv(input_csv)

    # Optional filtering
    if switch_id != -1:
        df = df[df['switch_id'] == switch_id]

    # Normalize timestamps
    t0 = df['timestamp'].iloc[0]
    df['timestamp'] = (df['timestamp'] - t0) * timestamp_scale

    # Group
    df = (
        df.sort_values('timestamp')
        .groupby(
            ['poll_id', 'switch_id', 'port_no'],
            as_index=False
        )
        .last()
    )

    # Keep only complete polling rounds
    expected_rows = df.groupby('poll_id').size().max()

    valid_polls = (
        df.groupby('poll_id')
        .size()
        .loc[lambda s: s == expected_rows]
        .index
    )

    df = df[df['poll_id'].isin(valid_polls)]


    # Aggregate all ports
    df = (
        df.groupby('poll_id', as_index=False)
        .agg(
            timestamp=('timestamp', 'min'),
            rx_packets=('rx_packets', 'sum')
        )
    )

    # Drop innecessary column
    df = df.drop(columns='poll_id')

    # Normalize so it starts on 0
    df['rx_packets'] -= df['rx_packets'].iloc[0]

    # Rename if desired
    df = df.rename(columns={'rx_packets': 'packets'})

    # Round timestamps
    df['timestamp'] = df['timestamp'].round(3)

    # Save data
    df.to_csv(output_csv, index=False)


if __name__ == '__main__':

    input_csv, output_csv, switch_id, scale = [argv[1], argv[2], argv[3], argv[4]]
    normalize_traffic_statistics(input_csv, output_csv,
         switch_id=int(switch_id), timestamp_scale=float(scale))
