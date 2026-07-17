# Run with sudo

.venv/bin/python -m launch_experiment experiment_1 \
 --duration 10 --seed 1 --sampling_interval 0.1

.venv/bin/python -m analysis.csv_preprocessing.group_packet_data \
 experiments/experiment_1/measurements/traffic_stats.csv \
 experiments/experiment_1/measurements/grouped_packets.csv \
 -1 1.0
