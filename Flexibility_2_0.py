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
from math import *
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
    df=copy.deepcopy(df_flexibility)
    df2=pd.DataFrame()
    for i in range(len(list_power_unit)):
        df['power']=df_flexibility.loc[:,'power']+list_power_unit[i]
        #df=df.merge(df_flexibility, how='outer', on='power')
        #df.set_index('power', inplace=True)
        #df_flexibility.set_index('power', inplace=True)
        df2 = pd.concat([df, df2], ignore_index=True)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df2['combinations'] = df2.groupby("power")["combinations"].transform("sum")
    df2 = df2.sort_values(by=['power'])
    #print("df2 :",df2)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df2 = df2.drop_duplicates(subset = ['power'], keep = 'first')
    df2=df2.sort_values(by=['power'])
    #plt.bar(df2['power'], df2['combinations'], width=0.8, bottom=None,  align='center', data=None)
    return df2


def build_Op_flex(list_unit):
    tic_start = time.time()
    if len(list_unit)<1:
        raise ValueError('no unit')
    if len(list_unit)==1:
        return Initialization(list_unit[0])
    else:
        df=Initialization(list_unit[0])
        for i in range(1,len(list_unit)):
           df=Add_Unit(df, list_unit[i])
           #df.loc[:,"combinations"]=df.loc[:,"combinations"]/max(df.loc[:,"combinations"])
           #plt.figure()
           #plt.bar(df['power'], df['combinations'], width=0.8, bottom=None,  align='center', data=None)
        tic_end = time.time()
        print("calculation time :", tic_end - tic_start)    
        return df
    
def plot_flexi(f):
    l=[]
    #for i in range(len(f)):
        #print(f.loc[i,])
        #l.append(log10(f.loc[:,"combinations"][i]/min(f.loc[:,"combinations"])))
    plt.bar(f['power'], f["combinations"], width=0.8, bottom=None,  align='center', data=None)
    
   
def Sub_Unit():
    pass



#list_unit= [list(range(0,900,100))]*1 + [list(range(0,1300,100))]*1 + [list(range(0,1450,100))]*1
list_unit = [[0,100,200,300,400],
             [0,100]]


f=build_Op_flex(list_unit)

plt.plot(f['power'], f["combinations"])
#plt.plot(f['power'], f['combinations'])
