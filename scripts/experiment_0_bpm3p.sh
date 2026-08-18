# Run with sudo

.venv/bin/python -m launch_experiment experiment_0 \
 --duration 120 --seed 1 --sampling_interval 0.1

.venv/bin/python -m analysis.csv_preprocessing.group_packet_data \
 experiments/experiment_0/measurements/traffic_stats.csv \
 experiments/experiment_0/measurements/grouped_packets.csv \
 1 1.0

.venv/bin/python -m experiments.experiment_1.analysis.fit_to_3pbpm \
 experiments/experiment_0/measurements/grouped_packets.csv \
 1
