

import wx
import random
import numpy as np

from hypomods import *
from hypoparams import *
from hypodat import *
from hypogrid import *



class SpikeDat():
    def __init__(self):

        self.maxspikes = 100000
        self.spikecount = 0
        self.times = pdata(self.maxspikes)
        self.isis = pdata(self.maxspikes)

        # initialise arrays for spike interval analysis
        self.histsize = 10000
        self.hist1 = pdata(self.histsize + 1)
        self.hist5 = pdata(self.histsize + 1)
        self.hist1norm = pdata(self.histsize + 1)
        self.hist5norm = pdata(self.histsize + 1)
        self.haz1 = pdata(self.histsize + 1)
        self.haz5 = pdata(self.histsize + 1)

        self.normscale = 10000



    def Analysis(self):

        # reset spike interval analysis stores
        for i in range(self.histsize):
            self.hist1[i] = 0
            self.hist5[i] = 0
            self.haz1[i] = 0	
            self.haz5[i] = 0	
            self.hist1norm[i] = 0
            self.hist5norm[i] = 0

        self.hist1.xmax = 0
        self.hist5.xmax = 0
        self.hist1norm.xmax = 0
        self.hist5norm.xmax = 0
        self.haz1.xmax = 0
        self.haz5.xmax = 0

        mean = 0
        variance = 0
        norm = 1
        binsize = 5

        if self.spikecount == 0: return

        # ISIs, Histogram, Freq, Variance

        isicount = self.spikecount - 1
        # if(neurodat) times[0] = datneuron->times[0];

        # 1ms ISI Histogram
        for i in range(isicount):                                   
            if i > self.maxspikes: break
            # if(neurodat) times[i+1] = datneuron->times[i+1];
            self.isis[i] = self.times[i+1] - self.times[i]
            if self.hist1.xmax < int(self.isis[i]): self.hist1.xmax = int(self.isis[i])
            self.hist1[int(self.isis[i])] += 1
            mean = mean + self.isis[i] / isicount
            variance = self.isis[i] * self.isis[i] / isicount + variance;

        # spike interval statistics
        isisd = sqrt(variance - mean * mean)
        freq = 1000 / mean
        if mean == 0: freq = 0
        meanisi = mean
        isivar = variance

        # 5ms ISI Histogram
        for i in range(self.hist1.xmax + 1):
            if i/binsize > self.hist5.xmax: self.hist5.xmax =  i/binsize
            self.hist5[i/binsize] = self.hist5[i/binsize] + self.hist1[i]

        # Normalise histograms
        for i in range(self.hist1.xmax + 1):
            self.hist1norm[i] = self.normscale * self.hist1[i] / isicount
            self.hist5norm[i] = self.normscale * self.hist5[i] / isicount

        self.hist1norm.xmax = self.hist1.xmax
        self.hist5norm.xmax = self.hist5.xmax
        
        # Hazards
        hazcount = 0
        self.haz1.xmax = self.hist1.xmax
        self.haz5.xmax = self.hist5.xmax

        # 1ms Hazard
        for i in range(self.hist1.xmax + 1):
            self.haz1[i] = self.hist1[i] / (self.spikecount - hazcount)
            hazcount = hazcount + self.hist1[i]

        # 5ms Hazard 
        for i in range(self.hist1.xmax + 1):                                                
            self.haz5[i/binsize] = self.haz5[i/binsize] + self.haz1[i]

