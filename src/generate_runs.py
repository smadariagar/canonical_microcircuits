"""Hace el histograma
summary_
"""
import os
import warnings
warnings.filterwarnings("ignore")

if __name__ == '__main__':

    for i in range(5):
        os.system("python -m src.run_model_busse")
    os.system("python -m src.generate_hist_folders")
