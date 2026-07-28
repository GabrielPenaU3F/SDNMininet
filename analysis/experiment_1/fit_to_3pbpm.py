from pathlib import Path
from sys import argv

import pandas as pd
import matplotlib
matplotlib.use('QtAgg')
from matplotlib import pyplot as plt

from config.environment import Environment
from model.traffic_models.arrival_processes import BPM3pProcess


def fit_parameters(x, y, seed=42):
    beta_0, gamma_0, rho_0 = 1, 1, 1
    model = BPM3pProcess(beta_0, gamma_0, rho_0, seed)
    return model.fit(x, y)

if __name__ == '__main__':

    csv_path = Path(argv[1])
    seed = int(argv[2])

    df = pd.read_csv(csv_path)
    x = df['timestamp'].to_numpy()
    y = df['packets'].to_numpy()

    beta, gamma, rho = fit_parameters(x, y, seed)

    print(f'beta = {beta}')
    print(f'gamma = {gamma}')
    print(f'rho = {rho}')
    print(f'H = {gamma/rho}')

    model = BPM3pProcess(beta, gamma, rho, seed=seed)
    y_pred = model.mvf(x, beta, gamma, rho)

    plt.plot(x, y, linestyle='--', label='Data')
    plt.plot(x, y_pred, linestyle='-', label='MVF')
    plt.legend()
    plt.show()

    # project_root = Environment.get_environment().project_root
    # plt.savefig(project_root / 'analysis' / 'experiment_1' / 'fit.png', dpi=300)
