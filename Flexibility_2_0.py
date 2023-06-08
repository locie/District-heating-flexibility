# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 11:05:15 2023

@author: blanchoy
"""




import bisect
import copy
import heapq
import itertools
import math
import matplotlib.pyplot as plt
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




def Add_Unit_normalized(df_flexibility, list_power_unit):
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
    #print("df2 :",df2)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df2 = df2.drop_duplicates(subset = ['power'], keep = 'first')
    df2=df2.sort_values(by=['power'])
    #plt.bar(df2['power'], df2['combinations'], width=0.8, bottom=None,  align='center', data=None)
    return df2


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


def Sub_Unit(df_flexibility, list_power_unit):
    df=pd.DataFrame()
    p1min = min(df_flexibility["power"])
    p1max = max(df_flexibility["power"])
    p0min = p1min - min(list_power_unit)
    p0max = p1max - max(list_power_unit)
    #print (p1min , p1max , p0min , p0max)
    #print("p0max+p1min =", p0max+p1min)
    for p in df_flexibility["power"]:
        #print("\n")
        #print("p =",p)
        list_1=[element for element in list_power_unit if element <= p-p0min]
        #print("liste = ", list_1)
        if len(list_1)==1 :
            df2=pd.DataFrame({"power":[p-list_1[0]], "combinations" : [df_flexibility.loc[df_flexibility["power"]==p,"combinations"].values[0]]})
            df=pd.concat([df, df2], ignore_index=True)
            if p==p0max-list_power_unit[0]:
                return df
            
        if len(list_1)>=2:
            sub_value=0
            for i in range(len(list_1)-1):
                if len(df.loc[df["power"]==p-list_1[i+1],"combinations"].values) != 0:
                    sub_value += df.loc[df["power"]==p-list_1[i+1],"combinations"].values[0]
                    #print('sub_value =',sub_value, type(sub_value))
            df2=pd.DataFrame({"power":[p-list_1[0]], "combinations" : [df_flexibility.loc[df_flexibility["power"]==p,"combinations"].values[0]-sub_value]})
            df=pd.concat([df, df2], ignore_index=True)
            if p==p0max+list_power_unit[0]:
                return df
        #print('df =',df)

                
             

    

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
           df.loc[:,"combinations"]=df.loc[:,"combinations"]/max(df.loc[:,"combinations"])
           #plt.figure()
           #plt.bar(df['power'], df['combinations'], width=0.8, bottom=None,  align='center', data=None)
           print (i)
        tic_end = time.time()
        print("calculation time :", tic_end - tic_start)    
        return df
    
    
    
    
def plot_flexi(f):
    l=[]
    #for i in range(len(f)):
        #print(f.loc[i,])
        #l.append(log10(f.loc[:,"combinations"][i]/min(f.loc[:,"combinations"])))
    plt.bar(f['power'], f["combinations"], width=0.8, bottom=None,  align='center', data=None)
    
   



#list_unit= [list(range(0,900,100))]*1 + [list(range(0,1300,100))]*1 + [list(range(0,1450,100))]*1
list_unit_prod = [list(range(0,100))]*300
print(list_unit_prod)


unit=[-1,0,6]

f=build_Op_flex(list_unit_prod)



plt.figure()
plt.bar(f['power'], f["combinations"], color='g')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Operational multiplicity  (\u03A9)", weight='bold')
plt.title('Operational multiplicity distribution (2.0)', weight='bold')

plt.figure()
f2=Add_Unit(f, unit)
plt.bar(f2['power'], f2["combinations"] , color='g')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Operational multiplicity  (\u03A9)", weight='bold')
plt.title('Operational multiplicity distribution (2.0)', weight='bold')

plt.figure()
f3=Sub_Unit(f2,unit)
plt.bar(f3['power'], f3["combinations"], color='g')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Operational multiplicity  (\u03A9)", weight='bold')
plt.title('Operational multiplicity distribution (2.0)', weight='bold')