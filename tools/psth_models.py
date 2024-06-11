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

    results_folder = '/home/samuel/Desktop/results/' 
    folder_path = '/home/samuel/Desktop/'
    folder_names = os.listdir(results_folder)

    for folder in folder_names:

        groups = ['L23E', 'L23I', 'L4E', 'L4I', 'L5E', 'L5I', 'L6E', 'L6I']
        
        for group in groups:

            aux_csv = []
            with open(results_folder+folder+'/'+group+'.csv', 'r') as csvfile:
                # Create a reader object
                csv_reader = csv.reader(csvfile)
    
                # Iterate through the rows in the CSV file
                for row in csv_reader:
                    # Access each element in the row
                    float_row = [float(string) for string in row]
                    aux_csv.append(float_row)
            
            exec(group+folder[0]+'=np.mean(aux_csv, axis=0)')

    bins = np.arange(10, 1000, 20)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L23I1, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L23I2, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L23I3, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L23I4, linewidth=2.0, color='#b015b6')
    plt.title('PSTH L23I', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L23I.png', dpi=300)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L23E1, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L23E2, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L23E3, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L23E4, linewidth=2.0, color='#0063B2')    
    plt.title('PSTH L23E', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L23E.png', dpi=300)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L4I1, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L4I2, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L4I3, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L4I4, linewidth=2.0, color='#b015b6')   
    plt.title('PSTH L4I', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16) 
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L4I.png', dpi=300)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L4E1, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L4E2, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L4E3, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L4E4, linewidth=2.0, color='#0063B2') 
    plt.title('PSTH L4E', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16)      
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L4E.png', dpi=300)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L5I1, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L5I2, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L5I3, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L5I4, linewidth=2.0, color='#b015b6')
    plt.title('PSTH L5I', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16) 
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L5I.png', dpi=300)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L5E1, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L5E2, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L5E3, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L5E4, linewidth=2.0, color='#0063B2') 
    plt.title('PSTH L5E', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16) 
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L5E.png', dpi=300)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L6I1, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L6I2, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L6I3, linewidth=2.0, color='#b015b6')
    plt.plot(bins, L6I4, linewidth=2.0, color='#b015b6')
    plt.title('PSTH L6I', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16) 
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L6I.png', dpi=300)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(bins, L6E1, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L6E2, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L6E3, linewidth=2.0, color='#0063B2')
    plt.plot(bins, L6E4, linewidth=2.0, color='#0063B2')
    plt.title('PSTH L6E', fontsize=22)
    plt.xlabel('time [ms]', fontsize=16)
    plt.ylabel('spikes', fontsize=16) 
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlim(-20,1020)
    plt.tight_layout()
    plt.savefig(folder_path + 'L6E.png', dpi=300)