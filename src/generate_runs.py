import os
import subprocess
import warnings

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/')

    for j in [0.0, 1.0, 2.0]:
        for k in [100.0, 200.0, 300.0]:
            for l in range(10):
                comando = ["python", "-m", "src.run_experiment", 
                           "--ns", str(0.2), "--ks", str(0.2), 
                           "--stim_rate_ecrf", str(k),
                           "--v1", "--lat",
                           "--v2", str(j)
                           , "--ff", "--fb"]
                subprocess.run(comando)


