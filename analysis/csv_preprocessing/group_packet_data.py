from pathlib import Path
from sys import argv

import numpy as np
import pandas as pd


'''
This preprocessing assumes that all port statistics belonging to the same polling cycle 
fall within the same aggregation window. Therefore, the aggregation window should be 
chosen significantly larger than the controller polling jitter.
'''
def normalize_traffic_statistics(input_csv: str, output_csv: str,
    switch_id: int = -1, timestamp_scale: float = 1.0, bin_width: float = 0.01,
) -> None:
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

    bin_width
        Length of the time window over which packets are grouped.
    """
    input_csv = Path(input_csv)
    output_csv = Path(output_csv)
    df = pd.read_csv(input_csv)

    # Optional filtering
    if switch_id != -1:
        df = df[df['switch_id'] == switch_id]

    # Unit conversion
    t0 = df['timestamp'].iloc[0]
    df["timestamp"] -= t0
    df['timestamp'] *= timestamp_scale

    # Assign each sample to a window
    df['timestamp'] = np.round(np.floor(df['timestamp'] / bin_width) * bin_width, 3)

    # Sort (security)
    df = df.sort_values('timestamp')

    # Read the last entry of each port
    df = (
        df.groupby(['timestamp', 'port_no'], as_index=False)['rx_packets']
        .last()
    )

    # Sum across every port of the requested switch/s
    df = (
        df.groupby('timestamp', as_index=False)['rx_packets']
        .sum()
    )

    timestamps = np.arange(
        0,
        df['timestamp'].iloc[-1] + bin_width,
        bin_width,
    ).round(3)

    df = (
        df.set_index('timestamp')
        .reindex(timestamps)
        .ffill()
        .fillna(0)
        .rename_axis('timestamp')
        .reset_index()
    )

    # Normalize so it starts on 0
    df['rx_packets'] -= df['rx_packets'].iloc[0]

    # Save data
    df.to_csv(output_csv, index=False)


if __name__ == '__main__':

    input_csv, output_csv, switch_id, scale, bin_width = [argv[1], argv[2], argv[3], argv[4], argv[5]]
    normalize_traffic_statistics(input_csv, output_csv,
         switch_id=int(switch_id), timestamp_scale=float(scale), bin_width=float(bin_width))