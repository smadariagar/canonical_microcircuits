"""Hace el histograma
summary_
"""
import os
import warnings
warnings.filterwarnings("ignore")

if __name__ == '__main__':

    path = "/home/samuelmr/Documentos/NEST/canonical_microcircuits/results/potjans_diesmann/20240503151459/"
    name = 'spike_recorder'

    sd_files = []
    sd_names = []
    for fn in os.listdir(path):
        if fn.startswith(name):
            sd_files.append(fn)
            # spike recorder name and its ID
            fnsplit = '-'.join(fn.split('-')[:-1])
            if fnsplit not in sd_names:
                sd_names.append(fnsplit)

    print(sd_files)
    print('*********************************')
    #sd_files = [os.path.join(path, f) for f in sd_files] # add path to each file
    #sd_files.sort(key=lambda x: os.path.getmtime(x))
    #print(sd_files)
    
    
    
    
    sd_files.sort(key=lambda fn: os.path.getmtime(os.path.join(path, fn)))

    print(sd_files)

    for i in range(1):
        print(i)
        #os.system("python -m src.run_connected_4_microcircuits")
