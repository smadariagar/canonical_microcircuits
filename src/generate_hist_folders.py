"""Hace el histograma
summary_
"""
import os
import csv
import time

import warnings
import numpy as np

import matplotlib.pyplot as plt
import tools.histogram_single_microcircuit as hist_spikes

warnings.filterwarnings("ignore")


def psht_plot(l2e, l2i, l4e, l4i, l5e, l5i, l6e, l6i, mcc, bins):

    fig, axes = plt.subplots(4, 2, figsize=(9, 12))    
    bins = bins+10

    n = np.mean(l2e, axis=0)
    axes[0][0].plot(bins, n, linewidth=2.0, color='#0063B2')
    axes[0][0].tick_params(axis='both', which='major', labelsize=10)
    axes[0][0].tick_params(axis='both', which='minor', labelsize=10)
    axes[0][0].set_xlim(20,np.max(bins)-10)
    axes[0][0].set_ylim(bottom=np.min(n[1:]))
    axes[0][0].set_title("L23 e")
    
    n = np.mean(l2i, axis=0)
    axes[0][1].plot(bins, n, linewidth=2.0, color='#b015b6')
    axes[0][1].tick_params(axis='both', which='major', labelsize=10)
    axes[0][1].tick_params(axis='both', which='minor', labelsize=10)
    axes[0][1].set_xlim(20,np.max(bins)-10)
    axes[0][1].set_ylim(bottom=np.min(n[1:]))
    axes[0][1].set_title("L23 i")

    n = np.mean(l4e, axis=0)
    axes[1][0].plot(bins, n, linewidth=2.0, color='#0063B2')
    axes[1][0].tick_params(axis='both', which='major', labelsize=10)
    axes[1][0].tick_params(axis='both', which='minor', labelsize=10)
    axes[1][0].set_xlim(20,np.max(bins)-10)
    axes[1][0].set_ylim(bottom=np.min(n[1:]))
    axes[1][0].set_title("L4 e")
    
    n = np.mean(l4i, axis=0)
    axes[1][1].plot(bins, n, linewidth=2.0, color='#b015b6')
    axes[1][1].tick_params(axis='both', which='major', labelsize=10)
    axes[1][1].tick_params(axis='both', which='minor', labelsize=10)
    axes[1][1].set_xlim(20,np.max(bins)-10)
    axes[1][1].set_ylim(bottom=np.min(n[1:]))
    axes[1][1].set_title("L4 i")

    n = np.mean(l5e, axis=0)
    axes[2][0].plot(bins, n, linewidth=2.0, color='#0063B2')
    axes[2][0].tick_params(axis='both', which='major', labelsize=10)
    axes[2][0].tick_params(axis='both', which='minor', labelsize=10)
    axes[2][0].set_xlim(20,np.max(bins)-10)
    axes[2][0].set_ylim(bottom=np.min(n[1:]))
    axes[2][0].set_title("L5 e")
    
    n = np.mean(l5i, axis=0)
    axes[2][1].plot(bins, n, linewidth=2.0, color='#b015b6')
    axes[2][1].tick_params(axis='both', which='major', labelsize=10)
    axes[2][1].tick_params(axis='both', which='minor', labelsize=10)
    axes[2][1].set_xlim(20,np.max(bins)-10)
    axes[2][1].set_ylim(bottom=np.min(n[1:]))
    axes[2][1].set_title("L5 i")

    n = np.mean(l6e, axis=0)
    axes[3][0].plot(bins, n, linewidth=2.0, color='#0063B2')
    axes[3][0].tick_params(axis='both', which='major', labelsize=10)
    axes[3][0].tick_params(axis='both', which='minor', labelsize=10)
    axes[3][0].set_xlim(20,np.max(bins)-10)
    axes[3][0].set_ylim(bottom=np.min(n[1:]))
    axes[3][0].set_title("L6 e")
    
    n = np.mean(l6i, axis=0)
    axes[3][1].plot(bins, n, linewidth=2.0, color='#b015b6')
    axes[3][1].tick_params(axis='both', which='major', labelsize=10)
    axes[3][1].tick_params(axis='both', which='minor', labelsize=10)
    axes[3][1].set_xlim(20,np.max(bins)-10)
    axes[3][1].set_ylim(bottom=np.min(n[1:]))
    axes[3][1].set_title("L6 i")

    plt.tight_layout()    
    plt.savefig(folder_path + "/" + mcc + ".png", dpi=300)

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')
    file_names = os.listdir(folder_path)

    folder_names = [file for file in file_names if file.startswith('2024')]

    mccs = ['V1_A', 'V1_B', 'V1_C', 'V2']

    for i in range(2):

        L23I = []
        L23E = []
        L4I = []
        L4E = []
        L5I = []
        L5E = []
        L6I = []
        L6E = []

        for folder in folder_names:
            t = time.time()
            print("---> Making hist for " + folder + " ...")
            data, bins = hist_spikes.apliccation_metrics_folders(folder_path, folder)

            L23I.append(data[(i*8)+0])
            L23E.append(data[(i*8)+1])
            L4I.append(data[(i*8)+2])
            L4E.append(data[(i*8)+3])
            L5I.append(data[(i*8)+4])
            L5E.append(data[(i*8)+5])
            L6I.append(data[(i*8)+6])
            L6E.append(data[(i*8)+7])

        if True:
            with open(os.path.join(folder_path, 'L23I.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L23I)

            with open(os.path.join(folder_path, 'L23E.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L23E)

            with open(os.path.join(folder_path, 'L4I.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L4I)

            with open(os.path.join(folder_path, 'L4E.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L4E)

            with open(os.path.join(folder_path, 'L5I.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L5I)

            with open(os.path.join(folder_path, 'L5E.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L5E)

            with open(os.path.join(folder_path, 'L6I.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L6I)

            with open(os.path.join(folder_path, 'L6E.csv'), 'w') as file:
                write = csv.writer(file)
                write.writerows(L6E)
        
        print(time.time() - t)

        psht_plot(L23E, L23I, L4E, L4I, L5E, L5I, L6E, L6I, mccs[i], bins)


    