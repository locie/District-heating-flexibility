# -*- coding: utf-8 -*-
"""
Created on Fri May 26 10:01:37 2023

@author: blanchoy
"""




import bisect
import copy
import heapq
import itertools
import math
import matplotlib.pyplot as plt
plt.plot(), plt.close()
import numpy as np
import os
from functools import reduce
import time
import tracemalloc
import warnings
import pandas as pd
import csv




def Initialization(list_power_unit):
    df=pd.DataFrame(data = {'power' : list_power_unit , 'combinations'  : [1]*len(list_power_unit) })  #'power' : [list_power_unit] , 'combinations'  : [1]*len(list_power_unit) 
    #df['power']=df.loc[:,'power']+1
    return df
    plt.bar(df['power'], df['combinations'], width=0.8, bottom=None,  align='center', data=None)


def Add_Unit(df_flexibility, list_power_unit):
    for i in range(len(list_power_unit)):
        df=copy.deepcopy(df_flexibility)
        df['power']=df.loc[:,'power']+list_power_unit[i]
        #df=df.merge(df_flexibility, how='outer', on='power')
        #df.set_index('power', inplace=True)
        #df_flexibility.set_index('power', inplace=True)
        print(df)
        print(df_flexibility)
        df2 = pd.concat([df, df_flexibility], ignore_index=True)
        print("\n")
        print(df2)
        df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
        print(df2.drop_duplicates(subset = 'power', keep = 'last'))
        #print(df2)
        #liste = df2.duplicate()
        #print(liste)
        #df1 = df2.groupby(df2.index).get_group(3).sum()
        #print(df1)
        #print(df.groupby('power').sum().add(df_flexibility))
        #df['combination'] =     df.loc[:,'combinations_x']+df.loc[:,'combinations_y']  
        #print (df)
    
def Sub_Unit():
    pass


list_power_unit_1 = [0 , 3 , 7]
init=Initialization(list_power_unit_1)
Add_Unit(init,[3])
