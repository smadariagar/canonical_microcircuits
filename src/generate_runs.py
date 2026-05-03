import os
import subprocess
import warnings

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/')

    for j in range(1):
        for k in [300.0]:
            for l in range(1):
                comando = ["python", "-m", "src.run_experiment", 
                           "--ns", str(0.2), "--ks", str(0.2), 
                           "--stim_rate_ecrf", str(k),
                           "--v1", "--v2",
                           "--lat", "--ff", "--fb"]
                subprocess.run(comando)


