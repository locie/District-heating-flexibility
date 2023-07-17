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
import seaborn as sns
from matplotlib.colors import LogNorm




from API_availability import *



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


def Remove_Unit(df_flexibility, list_power_unit):
    df=pd.DataFrame()
    p1min = min(df_flexibility["power"])
    p1max = max(df_flexibility["power"])
    p0min = p1min - min(list_power_unit)
    p0max = p1max - max(list_power_unit)
    #print (p1min , p1max , p0min , p0max)
    #print("p0max+p1min =", p0max+p1min)
    for p in df_flexibility["power"]:
        #print("\n")
        print("p =",p ,'   pmaax = ',p0max)
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

def Remove_Unit_2(df_flexibility, list_power_unit):
    p1min = df_flexibility["power"].min()
    p1max = df_flexibility["power"].max()
    p0min = p1min - min(list_power_unit)
    p0max = p1max - max(list_power_unit)

    df_0=pd.DataFrame()

    for i in range(len(list_power_unit)):
        if i ==1:
            df = df_flexibility.loc[df_flexibility.loc[:,'power'] < list_power_unit[1]] 
            df_flexibility['power'] -= list_power_unit[0]
        if i >= 2:
            df = df_flexibility.loc[list_power_unit[i] <  df_flexibility.loc[:,'power'] < list_power_unit[i+1]] 
            for j in range(2,len(list_power_unit)):
                su_df = df_0.loc[df_0.loc[:,'power'] < list_power_unit[1]]
     
             

    

def build_Op_flex(df_units):
    tic_start = time.time()
    if len(df_units)<1:
        raise ValueError('no unit')
    if len(df_units)==1:
        return Initialization(df_units.loc[1,'list_power'])
    else:
        df=Initialization(df_units.loc[1,'list_power'])
        for i in range(1,len(df_units)):
           df=Add_Unit(df, df_units.loc[i,'list_power'])
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


def Create_df_units(df, nb_elements):
    list_power=[]
    unit_name=[]
    for i in range(len(df)):
        if  df.loc[i,"production_type"][0:5] == "HYDRO" and  df.loc[i,"unit_type"] == "PRODUCTION_UNIT":
            installed_p = df.loc[i,"installed_capacity"]
            liste = np.linspace(-installed_p, 0, nb_elements)
            liste = np.round(liste).astype(int).tolist()
            liste = list(set(liste))
            liste.sort()
            unit_name.append(df.loc[i,"name"])
        else:
            installed_p = df.loc[i,"installed_capacity"]
            liste = np.linspace(0, installed_p, nb_elements)
            liste = np.round(liste).astype(int).tolist()
            liste = list(set(liste))
            liste.sort()
            unit_name.append(df.loc[i,"name"])
        list_power.append(liste)
    #print(list_power, type(list_power))
    df2=pd.DataFrame({"name":unit_name, "list_power" : list_power})
    return (df2)



def build_df_events(f1, list_events, df_units):
    df_HeatMap = pd.DataFrame()
    df_N0 = f1
    for i in range(len(f1)):
        df_N0.reset_index()
        name = list_events.loc[i,'name']
        
        if list_events.loc[i,'date_type']=='start' and df_units.loc[df_units.loc[:,'name']==name]['list_power'].values[0] != [0,0]:
            print(df_units.loc[df_units.loc[:,'name']==name])
            df_N1 = Remove_Unit(df_N0 , df_units.loc[df_units.loc[:,'name']==name]['list_power'].values[0])  
            
        if list_events.loc[i,'date_type']=='end':
            print(df_units.loc[df_units.loc[:,'name']==name])
            df_N1 = Add_Unit(df_N0 , df_units.loc[df_units.loc[:,'name']==name]['list_power'].values[0])
            
        df_HeatMap = pd.concat([df_HeatMap, df_N1], ignore_index=True)
        df_N0 = df_N1




def build_df_dipso(df_units, list_events, nb_elements):
    df_units_available =df_units.transpose()
    #print(df_units_available)
    #print(df_units_available.loc['name',:])
    df_units_available.columns = df_units_available.loc['name',:]
    df_units_available.insert(loc=0 , column="Date", value=['','init'])
    df_units_available =  df_units_available.drop('name')
    
    for i in range(len(list_events)):
        df = df_units_available.tail(1)
        
        date = list_events.loc[i,'date']
        unit_name = list_events.loc[i,'name']
        power = list_events.loc[i,'available_capacity']
        unit_type = list_events.loc[i,'unit_type']
        
        if unit_type == "PRODUCTION_UNIT":
            liste = np.linspace(-power, 0, nb_elements)
            liste = np.round(liste).astype(int).tolist()
            liste = list(set(liste))
            liste.sort()
        else:
            liste = np.linspace(0, power, nb_elements)
            liste = np.round(liste).astype(int).tolist()
            liste = list(set(liste))
            liste.sort()
            
        df.columns 
        #print(unit_name)
        #print(liste)    
            
        df_units_available=pd.concat([df_units_available, df], ignore_index=True)    
        df_units_available.tail(1).loc[:,'Date']=date
        df_units_available.at[len(df_units_available)-1 ,unit_name]= liste
        print (i)
        
    with open("df_availability.txt", 'w') as csv_file:
        df_units_available.to_csv(index= False ,path_or_buf=csv_file)
    return df_units_available       
        



def Build_df_heatmap(file_name):
    df_heatmap= pd.DataFrame()
    df = pd.read_csv(file_name , encoding='latin-1')
    m=1
    y=2020
    p=False
    for year in ['2020','2021','2022']:
        for month in ['01',"02","03","04",'05',"06","07","08",'09',"10","11","12"]:
            for i in range(len(df)):
                date=df.loc[i,'Date'][:7]
                if date == year+"-"+month:
                    #print ("la",date)
                    liste=df.loc[i,:].values[1:]
                    liste_convertie = [eval(element) for element in liste]
                    #print(liste_convertie)
                    df_liste = pd.DataFrame({'list_power' : liste_convertie})
                    #print(df_liste)
                    flexi=build_Op_flex(df_liste).reset_index()
                    print(flexi)
                    if p == False:
                        df_heatmap['power'] = flexi.loc[:,'power']
                        df_heatmap[date] = flexi.loc[:,'combinations']
                        MinGlob= min(flexi.loc[:,'combinations'])
                        p = True
                    else:
                        df_heatmap[date] = MinGlob
                        for i in range(len(flexi)):
                            MinLoc = min(flexi.loc[:,'combinations'])
                            power=flexi.loc[i,'power']
                            combinations=flexi.loc[i,'combinations']
                            print(power, year, month)
                            if combinations == 0:
                                combinations = MinGlob
                            df_heatmap.loc[df_heatmap.loc[:,'power']==power , date]= combinations*MinGlob/MinLoc
                            print(type( df_heatmap.loc[df_heatmap.loc[:,'power']==power,date]))
                    break
    with open("HM_YtotMtot.txt", 'w') as csv_file:
        df_heatmap.to_csv(index= False ,path_or_buf=csv_file)
    return df_heatmap
            
#df['name'] = L_name




def Plot_Heatmap(file_name):
    df_heatmap = pd.read_csv(file_name , encoding='latin-1')
    df_heatmap = df_heatmap.set_index('power')
    print(df_heatmap)
    df_heatmap_log = np.log10(df_heatmap)
    sns.heatmap(df_heatmap_log)


#a = Build_df_heatmap('df_availability.txt')

b=Plot_Heatmap("HM_YtotMtot.txt")



"""
a = Build_df_heatmap('df_availability.txt')
sns.heatmap(a)


 


df= pd.read_csv('unvailability_2020-1_to_2023-5.txt' , encoding='latin-1')
test=DataFrame_format('unvailability_2020-1_to_2023-5.txt')
list_plants=Plants_names('unvailability_2020-1_to_2023-5.txt') 
list_events = DataFrame_format('unvailability_2020-1_to_2023-5.txt')

df_units = Create_df_units(list_plants,2)


df_units_available = build_df_dipso(df_units, list_events,2)

a = Build_df_heatmap('df_availability.txt')


f1 = build_Op_flex(df_units)

build_df_events(f1, list_events , df_units)


plt.bar(f1['power'], f1["combinations"] , color='g')
#plt.yscale('log')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Operational multiplicity  (\u03A9)", weight='bold')
plt.title('Operational multiplicity distribution (2.0)', weight='bold')



U1=[0,1,2,3]
U2=[-1,2,7]

f1=Initialization(U1)
f2=Add_Unit(f1, U2)
f3=Remove_Unit(f2, U1)

plt.figure()
plt.bar(f1['power'], f1["combinations"] , color='g')
#plt.yscale('log')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Operational multiplicity  (\u03A9)", weight='bold')
plt.title('Operational multiplicity distribution (2.0)', weight='bold')


plt.figure()
plt.bar(f2['power'], f2["combinations"] , color='g')
#plt.yscale('log')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Operational multiplicity  (\u03A9)", weight='bold')
plt.title('Operational multiplicity distribution (2.0)', weight='bold')



plt.figure()
plt.bar(f3['power'], f3["combinations"] , color='g')
#plt.yscale('log')
plt.xlabel("Power demand", weight='bold')
plt.ylabel("Operational multiplicity  (\u03A9)", weight='bold')
plt.title('Operational multiplicity distribution (2.0)', weight='bold')
"""