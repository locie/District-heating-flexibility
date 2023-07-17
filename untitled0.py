# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 14:49:16 2023

@author: blanchoy
"""

import math

import numpy as np
import seaborn as sn
from matplotlib.colors import LogNorm

data = np.random.rand(20, 20)
data[0,0]=0

log_norm = LogNorm(vmin=data.min().min(), vmax=data.max().max())
cbar_ticks = [math.pow(10, i) for i in range(math.floor(math.log10(data.min().min())), 1+math.ceil(math.log10(data.max().max())))]

sn.heatmap(
    data,
    norm=log_norm,
    cbar_kws={"ticks": cbar_ticks}
)