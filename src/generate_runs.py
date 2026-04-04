import os
import subprocess
import warnings

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    for j in range(1):
        for k in range(1):
            for l in range(10):
                comando = ["python", "-m", "src.run_experiment", 
                           "--ns", str(0.3), "--ks", str(0.3), 
                           "--stim_rate_ecrf", str(300.0),
                           "--v1", "--v2",
                           "--lat", "--ff", "--fb"]
                subprocess.run(comando)


