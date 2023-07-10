# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 11:01:19 2023

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







def init(unit):
    l=list(range(unit[0]-1,unit[1]+2))
    #print(l, len(l))
    #print( [0]+[1]*len(l)+[0] , len([0]+[1]*(len(l)-2)+[0]))
    df=pd.DataFrame(data = {'power' :l , 'combinations'  :  [0]+[1]*(len(l)-2)+[0] })  #'power' : [list_power_unit] , 'combinations'  : [1]*len(list_power_unit) 
    #df['power']=df.loc[:,'power']+1
    return df







def add_unit_1(f , unit):
    lenth=len(f)
    l=list(range(f.head(1)["power"].values[0]+unit[0] , 1+f.tail(1)["power"].values[0]+unit[1]))
    df=pd.DataFrame(data = {'power' :l , 'combinations'  :  [0]*len(l) })
    for h in range(1,max(f["combinations"])+1):
        
        start_bool=False
        end_bool=False
        
        for p in range(min(f["power"]), max(f["power"])):
            #print("la : ",f.loc[i,"combinations"])
            #dn =  f.loc[i+1,"combinations"] - f.loc[i,"combinations"] 
            #print("pppppppppppp = ", f.loc[f.loc[:,"power"]==p]["combinations"].values[0])
            if f.loc[f.loc[:,"power"]==p]["combinations"].values[0] <= h-1 and f.loc[f.loc[:,"power"]==p+1]["combinations"].values[0] >= h:
                start=p+1
                start_bool=True
                
            if f.loc[f.loc[:,"power"]==p]["combinations"].values[0] >= h and f.loc[f.loc[:,"power"]==p+1]["combinations"].values[0] <= h-1:
                end=p+1
                end_bool=True
                
            #print("bool  =",start_bool,end_bool)
        
            if start_bool and end_bool:
                #print("start end =" , start , end)
                for p in range(start+unit[0], end+unit[1]):
                    #print("j =",p)
                    df.loc[df['power'] == p, 'combinations'] += 1
                    start_bool=False
                    end_bool=False
            #print("df  =",df)
            
    df_unit=init(unit)
    df= pd.concat([df, df_unit ,f], ignore_index=True)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df['combinations'] = df.groupby("power")["combinations"].transform("sum")
    #print("df2 :",df2)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df = df.drop_duplicates(subset = ['power'], keep = 'first')
    df=df.sort_values(by=['power'])
    
    return df








def add_unit_2(f , unit):
    lenth=len(f)
    l=list(range(f.head(1)["power"].values[0]+unit[0] , 1+f.tail(1)["power"].values[0]+unit[1]))
    #print("l =",l)
    variation_df=pd.DataFrame(data = {'power' :l , 'combinations'  :  [0]*len(l) })
    df=pd.DataFrame(data = {'power' :l , 'combinations'  :  [0]*len(l) })
    for p in range(min(f["power"]), max(f["power"])):
        
        power0 = 0
        power1 = 0
        if p in f.loc[:,"power"].values:
            power0 = f.loc[f.loc[:,"power"]==p]["combinations"].values[0]
        if p+1 in f.loc[:,"power"].values:
            power1 = f.loc[f.loc[:,"power"]==p+1]["combinations"].values[0]
        delta = power1 - power0

        #print("delta =", delta)
        if delta < 0  :
            variation_df.loc[variation_df['power'] == p+unit[1]+1 , 'combinations']  += delta
                
        if delta > 0 :
            variation_df.loc[variation_df['power'] == p+unit[0]+1 , 'combinations'] += delta
        #print("variation_df =",variation_df)
        
    for p in range(min(df["power"]), max(df["power"])):
        #print("\n")
        #print(p)
        #print("df-1 =" , df)
        #print("variation =", variation_df.loc[variation_df['power'] == p , 'combinations'])
        df.loc[variation_df['power'] == p+1, 'combinations'] = df.loc[variation_df['power'] == p, 'combinations'].values[0] + variation_df.loc[variation_df['power'] == p+1, 'combinations'].values[0]
        #print("df =",df)
    
    df_unit=init(unit)
    df= pd.concat([df, df_unit ,f], ignore_index=True)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df['combinations'] = df.groupby("power")["combinations"].transform("sum")
    #print("df2 :",df2)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df = df.drop_duplicates(subset = ['power'], keep = 'first')
    df=df.sort_values(by=['power']) 
    
    return df







def remove_unit_1(f , unit):
    start_1 = min(f.loc[:,"power"])+1
    end_1 = max(f.loc[:,"power"])-1
    
    if unit[0] < 0:
        start_0 = start_1 - unit[0]
        start =  'before'
    if unit[0] == 0:
        start_0 = start_1 
        start =  'same'
    if unit[0] > 0:
        start_0 = start_1
        start =  'after'
    if unit[1] < 0:
        end_0 = end_1 
        end =  "before"
    if unit[1] == 0:
        end_0 = end_1
        end =  "same"
    if unit[1] > 0:
        end_0 = end_1 - unit[1]
        end =  "after"

    print('+1 :', start_1 ,  end_1 ,'   +0 :',start_0 , end_0 )
    print("start :",start , "    end :", end)
    
    
    df_unit= init(unit)
    df_unit.loc[:,"combinations"] = - df_unit.loc[:,"combinations"]
    df= pd.concat([df_unit ,f], ignore_index=True)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df['combinations'] = df.groupby("power")["combinations"].transform("sum")
    #print("df2 :",df2)
    #df2['combinations'] = df2.duplicated().groupby(df2.index).sum().add(df2['combinations'])
    df = df.drop_duplicates(subset = ['power'], keep = 'first')
    df=df.sort_values(by=['power'])
    
    print('df_init ='  ,df)
    
    lenth=len(f)
    l1=list(range(f.head(1)["power"].values[0] , 1+f.tail(1)["power"].values[0]))
    #print("l =",l)
    variation_df=pd.DataFrame(data = {'power' :l1 , 'combinations'  :  [0]*len(l1) })
    df_remove=pd.DataFrame(data = {'power' :l1 , 'combinations'  :  [0]*len(l1) })

    for p in range(min(df["power"]), max(df["power"])):
        print("\n")
        print("p =",p)
        delta =  df.loc[df.loc[:,"power"]==p+1]["combinations"].values[0] - df.loc[df.loc[:,"power"]==p]["combinations"].values[0]
        print("delta =", delta)

        
        if start == "before" and delta > 0 :
            variation_df.loc[variation_df['power'] == p-unit[0]+1 , 'combinations']  = delta - variation_df.loc[variation_df['power'] == p+1 , 'combinations'].values[0]
            print("cas 1 :")
            
        if start == "same" and delta > 0 :
            variation_df.loc[variation_df['power'] == p-unit[0]+1 , 'combinations']  = delta/2
            print("cas 2 :")
            
        if start == "after" and delta > 0 :      
            if p-unit[0]+1 in l1:
                variation_df.loc[variation_df['power'] == p+1 , 'combinations']  = delta - variation_df.loc[variation_df['power'] == p-unit[0]+1 , 'combinations'].values[0]
            else:
                variation_df.loc[variation_df['power'] == p+1 , 'combinations']  = delta
            print("cas 3 :")
        
        if end == "before" and delta < 0 :
            variation_df.loc[variation_df['power'] == p-unit[1]+1 , 'combinations']  = delta - variation_df.loc[variation_df['power'] == p+1 , 'combinations'].values[0]
            print("cas 4 :")
            
        if end == "same" and delta < 0 :
            variation_df.loc[variation_df['power'] == p-unit[1]+1 , 'combinations']  = delta/2
            print("cas 5 :")    
        
        if end == "after" and delta < 0 :
            if p-unit[1]+1 in l1 and variation_df.loc[variation_df['power'] == p-unit[1]+1 , 'combinations'].values[0] <0:   
                variation_df.loc[variation_df['power'] == p+1 , 'combinations']  = delta - variation_df.loc[variation_df['power'] == p-unit[1]+1 , 'combinations'].values[0]
            else:
                variation_df.loc[variation_df['power'] == p+1 , 'combinations']  = delta
            print("cas 6 :")
            
        print("variation_df =",variation_df)

    for p in range(min(df_remove["power"]), max(df_remove["power"])):
         #print("\n")
         #print(p)
         #print("df-1 =" , df)
         #print("variation =", variation_df.loc[variation_df['power'] == p , 'combinations'])
         df_remove.loc[df_remove['power'] == p+1, 'combinations'] = df_remove.loc[df_remove['power'] == p, 'combinations'].values[0] + variation_df.loc[variation_df['power'] == p+1, 'combinations'].values[0]
    
    #print("variation_df =",df_remove)
          
    dif_start = start_0-start_1
    drop_start=list(range(dif_start))
    dif_end = end_1-end_0     
    drop_end=list(range(len(df_remove)-dif_end , len(df_remove) ))
    
    df_remove.drop(drop_start, axis=0, inplace=True)
    df_remove.drop(drop_end, axis=0, inplace=True)
 
    #print("variation_df =",df_remove)
    return df_remove







def build_Op_flex_1(list_unit):
    tic_start = time.time()
    if len(list_unit)<1:
        raise ValueError('no unit')
    if len(list_unit)==1:
        return Initialization(list_unit[0])
    else:
        df=init(list_unit[0])
        for i in range(1,len(list_unit)):
           df=add_unit_1(df, list_unit[i])
           #plt.figure()
           #plt.bar(df['power'], df['combinations'], width=0.8, bottom=None,  align='center', data=None)
           print (i)
        tic_end = time.time()
        #print("calculation time :", tic_end - tic_start)    
        return df
    
    
    
    
    
    
    
def build_Op_flex_2(list_unit):
    tic_start = time.time()
    if len(list_unit)<1:
        raise ValueError('no unit')
    if len(list_unit)==1:
        return Initialization(list_unit[0])
    else:
        df=init(list_unit[0])
        for i in range(1,len(list_unit)):
           df=add_unit_2(df, list_unit[i])
           #plt.figure()
           #plt.bar(df['power'], df['combinations'], width=0.8, bottom=None,  align='center', data=None)
           #print(df)
           print (i)
        tic_end = time.time()
        #print("calculation time :", tic_end - tic_start)    
        return df


def build_Op_flex_2_normanized(list_unit):
    tic_start = time.time()
    if len(list_unit)<1:
        raise ValueError('no unit')
    if len(list_unit)==1:
        return Initialization(list_unit[0])
    else:
        df=init(list_unit[0])
        for i in range(1,len(list_unit)):
           df=add_unit_2(df, list_unit[i])
           df.loc[:,"combinations"]=df.loc[:,"combinations"]/max(df.loc[:,"combinations"])
           #plt.figure()
           #plt.bar(df['power'], df['combinations'], width=0.8, bottom=None,  align='center', data=None)
           #print(df)
           print (i)
        tic_end = time.time()
        print("calculation time :", tic_end - tic_start)    
        return df
    
    
    
    

unit=[[0,1]]*10+[[0,5]]*10+[[2,12]]*5
unit2=[[1,9]]

unit1=[[0,2],[0,2]]+unit2

unit3=[[14,15],[2,3],[3,4],[-1,0],[-1,1]]

f1=build_Op_flex_2(unit3)



plt.figure()
plt.bar(f1['power'], f1["combinations"], color='g')
#plt.yscale('log')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Structural multiplicity  (\u03A9)", weight='bold')
plt.title('Structural multiplicity distribution (2.0)', weight='bold')


f2=remove_unit_1(f1, unit[0])



plt.figure()
plt.bar(f2['power'], f2["combinations"], color='g')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Structural multiplicity  (\u03A9)", weight='bold')
plt.title('Structural multiplicity distribution (2.0)', weight='bold')

f3=add_unit_2(f2, [0,2])


plt.figure()
plt.bar(f3['power'], f3["combinations"], color='g')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Structural multiplicity  (\u03A9)", weight='bold')
plt.title('Structural multiplicity distribution (2.0)', weight='bold')

