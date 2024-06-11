"""Hace el histograma
summary_
"""
import os
import csv
import time
import numpy as np

import warnings
import tools.histogram_single_microcircuit as hist_spikes

import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')
    file_names = os.listdir(folder_path)

    folder_names = [file for file in file_names if file.startswith('2024')]

    L23I = []
    L23E = []
    L4I = []
    L4E = []
    L5I = []
    L5E = []
    L6I = []
    L6E = []

    i=0

    for folder in folder_names:
        t = time.time()
        print("---> Making hist for "+folder+" ...")
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

    bins = bins+10
    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L23I, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#b015b6')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L23I.png", dpi=300)
    
    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L23E, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#0063B2')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L23E.png", dpi=300)

    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L4I, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#b015b6')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L4I.png", dpi=300)
    
    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L4E, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#0063B2')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L4E.png", dpi=300)

    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L5I, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#b015b6')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L5I.png", dpi=300)
    
    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L5E, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#0063B2')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L5E.png", dpi=300)

    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L6I, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#b015b6')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L6I.png", dpi=300)
    
    fig = plt.figure(figsize=(6, 4))
    n = np.mean(L6E, axis=0)
    plt.plot(bins, n, linewidth=2.0, color='#0063B2')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(80,1020)
    plt.tight_layout()
    plt.savefig(folder_path + "/" +str(i)+ "_L6E.png", dpi=300)