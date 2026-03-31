import os
import subprocess
import warnings

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    for j in range(1):
        for k in range(1):
            for l in range(10):
                comando = ["python", "-m", "src.run_model_busse_params", "1", "3"]
                subprocess.run(comando)


    # carpetas = [nombre for nombre in os.listdir(folder_path)
    #         if os.path.isdir(os.path.join(folder_path, nombre))]
    # for carpeta in carpetas:
       
    #     os.system("python -m src.lfp "+carpeta)