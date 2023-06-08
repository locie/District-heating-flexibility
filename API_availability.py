# -*- coding: utf-8 -*-
"""
ACCESSING RTE API FOR GETTING DECLARATION OF PP1/PP2 FOR THE NEXT DAY
"""

import os
from datetime import timedelta
from requests_oauthlib import OAuth2Session
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import numpy as np



########################################################################################################################
# ACCESSING RTE API TO FIND OUT WHETHER TOMORROW IS DECLARED AS PP1/PP2 OR NOT
########################################################################################################################
def access_rte(start_year , start_month , end_year , end_month):
    """
    Accessing RTE API to find out whether tomorrow is declared as PP1/PP2 or not
    :return: pp_declare: (bool) whether tommorow is a PP1/PP2 day or not,alert_day
    """
    
    # Credentials
    token_url = 'https://digital.iservices.rte-france.com/token/oauth/'
    pp_credentials = {"client_ID": "61f0c15b-658f-4a81-88c5-e61ea2a43764",
                      "client_secret": "73546e3b-ed6f-4762-bc34-eb1c9ba1bd40",
                      "key": "NjFmMGMxNWItNjU4Zi00YTgxLTg4YzUtZTYxZWEyYTQzNzY0OjczNTQ2ZTNiLWVkNmYtNDc2Mi1iYzM0LWViMWM5YmExYmQ0MA=="}

    # Opening a session for fetching the token
    rte = OAuth2Session(client_id=pp_credentials["client_ID"])
    rte.proxies = {'all': "http://195.220.19.49:3128/"}

    # Fetching token
    token = rte.fetch_token(token_url=token_url, method='POST', code=pp_credentials["key"],
                            username="yolan.blanchon@grenoble-inp.fr", password="!38G2Elab",
                            client_id=pp_credentials["client_ID"], client_secret=pp_credentials["client_secret"])
    
    #print(token)
    df=pd.DataFrame()
    
    list_day=[1,5,10,15,20,25,1]

    for y in range(start_year , end_year+1):
        sm=1
        em=12
        
        if y == start_year:
            sm=start_month 
        if y == end_year:  
            em=end_month
            
        for m in range (sm , em+1):
            for i in range(len(list_day)-1):
                
                m1=m
                y1=y
                m2=m
                y2=y
                
                if i == 5:
                    m2=m2+1
                    if m == 12:
                        y2=y+1
                        m2=1 

                  
                print(f"start :{y1}-{m1}-{list_day[i]}")
                print(f"end :{y2}-{m2}-{list_day[i+1]}")
    
                URL = f"https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v4/generation_unavailabilities?start_date={y1}-{m1}-{list_day[i]}T00:00:00%2B02:00&end_date={y2}-{m2}-{list_day[i+1]}T00:00:00%2B02:00&last_version=true"
                #URL = "https://digital.iservices.rtefrance.com/open_api/unavailability_additional_information/v4/sandbox/transmission_network_unavailabilities"
                
                # Accessing resource in JSON format
                resource = OAuth2Session(token=token)
                resource.proxies = {'all': "http://195.220.19.49:3128/"}
                response = resource.get(URL)
                
                print(response.status_code)
            
                # Declaring global variables
            
                # IF response status is OK
                if response.status_code == 200:
                    resource_json_InstalledPower = response.json()
            
                else:
                    # Recording error on log
                    print("CONNECTION ERROR")
            
                    # raising connection error
                    raise ConnectionError("Bad Connection")
                    
                #df = pd.DataFrame(resource_json_InstalledPower['generation_unavailabilities'])
                df1 = pd.DataFrame(resource_json_InstalledPower['generation_unavailabilities'])
            
                df = pd.concat([df , df1 ], ignore_index=True)
            

            
            df=df.drop_duplicates(subset='identifier' , ignore_index=True)
  
    l=len(df)
    L_name=[]
    L_installed_power=[]
    L_available_capacity=[]
    L_unit_type=[]
    for i in range(l):
        dff= df.loc[i,'unit']
        L_name.append(dff["name"])
        L_installed_power.append(dff['installed_capacity'])
        L_unit_type.append(dff['type'])
        
        dfff= df.loc[i,'values']
        L_available_capacity.append(dfff[0]["available_capacity"])
        

    df['name'] = L_name
    df['installed_capacity'] = L_installed_power
    df['available_capacity'] = L_available_capacity
    df['unit_type'] = L_unit_type


    #del df['identifier']
    del df['version']
    del df['updated_date']
    del df['creation_date']
    del df['producer']
    del df['eic_code_producer']
    del df['message_id']
    del df['unit']
    del df['reason']
    del df['remarks']
    del df['values']
    
    df=df.loc[df.loc[:,'status']!='DISMISSED']
    
    with open(f"unvailability_{start_year}-{start_month}_to_{end_year}-{end_month}.txt", 'w') as csv_file:
        df.to_csv(index= False ,path_or_buf=csv_file)
        
 
    return df
       



def DataFrame_format(file_name):
    df = pd.read_csv(file_name , encoding='latin-1')
    #print (df)
    df_start=df.drop(columns='end_date')
    df_start = df_start.rename(columns={'start_date' : 'date'})
    df_start.insert(2, "date_type", "start", True)
    
    df_end = df.drop(columns='start_date')
    df_end = df_end.rename(columns={'end_date' : 'date'})
    df_end.insert(2, "date_type", "end", True)


    df_format = pd.concat([df_start , df_end ], ignore_index=True)
    df_format=df_format.sort_values(by=['date'])
    df_format = df_format.reset_index(drop=True)
    return(df_format)
    
    
def Plants_names(file_name):    
    df = pd.read_csv(file_name , encoding='latin-1')
    del df['identifier']
    del df['start_date']
    del df['end_date']
    del df['type']
    del df['status']
    del df['available_capacity']
    df=df.drop_duplicates(subset=['name'], ignore_index=True)
    df=df.sort_values(by=['production_type','name'])
    return df
    #types=df["name"].values
    

if __name__ == "__main__":
    #i = access_rte(2020, 1 , 2023 , 5)   # start : yyyy  , mm   , end : yyyy ,  mm
    #print('y :',y)
    test=DataFrame_format('unvailability_2020-1_to_2023-5.txt')
    test2=Plants_names('unvailability_2020-1_to_2023-5.txt')
