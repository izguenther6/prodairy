'''
useful functions

'''

import pandas as pd
import numpy as np

def convert_units(df):
    '''
    need correct units to use equation from paper
    -
    returns | df: dataframe of converted values with precipitation, snowfall in mm and temp in C
    -
    args | df: original dataframe 
           area: area of covered storage [ft^2]
    '''
    #get rid of trace (T) and missing (M) values as zeros...also remove (S), not sure what this is
    df = df.replace(to_replace='T', value = 0.0)
    df = df.replace(to_replace='M', value = 0.0)
    df = df.replace(to_replace='S', value = 0.0)
    
    #make sure all values are numeric...helps catch errors in data entries
    pd.to_numeric(df['Tavg [F]'], errors='coerce')
    pd.to_numeric(df['P [in]'])
    pd.to_numeric(df['S [in]'])
    pd.to_numeric(df['Rhavg'])

    #convert P, S, and T
    df['P [in]'] = df.loc[:,'P [in]'] * 25.4 #1 inch = 25.4 mm
    df['S [in]'] = df.loc[:,'S [in]'] * 25.4 #1 inch = 25.4 mm
    df['Tavg [F]'] = (df.loc[:,'Tavg [F]'] - 32) * 5/9 #F to C

    #rename columns
    df = df.rename(columns={'P [in]' : 'P[mm]', 'S [in]': 'S[mm]', 'Tavg [F]': 'Tavg[C]'})
    df = df.round(2) #round decimal places

    return df


def mass_bal(df, area):
    '''
    returns | dfmb: dataframe of cumulative precipitation for a week, cumulative evaporation, net water volume into system,
                    and pumping cost
    -
    args | df: dataframe of daily data
           area: area of covered storage
    '''
    
    days = df.shape[0]
    wks = int((days - days % 7) / 7) #only looking at full weeks
    dfmb = pd.DataFrame(columns=['week', 'Tavg[C]', 'P[mm]', 'S[mm]', 'Rhavg[%]', 'Eout[mm]', 'Net Volume Change[ft^3]', 
                                 'Total Vol [ft^3]', 'Pumping Cost Change [$]', 'Pumping Cost Total [$]'], index = range(1, wks + 1))
#    dfmb.at[0, 'Total Vol [ft^3]'] = 0 #set initial volume to 0

    for wk in range(1, wks + 1):
        end_date = wk * 7 #end date index for week
        start_date = end_date - 7 #start date index for week

        #perform mass balance: (P[mm/wk] + S[mm] - Eout [mm/wk]) * area [ft^2] * 1 [wk] = chg [ft^3]
        #totV = prev + net
        #totPC = prev + pcost
        P = df.iloc[start_date:end_date, 2].sum() #cumulative precipitation for wk [mm/wk]
        Sconv = .1 #estimate for water content in snow
        S = df.iloc[start_date:end_date, 3].sum() * Sconv #cumulative snowfall for wk [mm/wk]
        Ptot = P + S
        Tavg = df.iloc[start_date:end_date, 1].mean() #weekly average for temperature [C]
        Rhavg = df.iloc[start_date:end_date, 4].mean() #weekly average for temperature
        Eout = 10 * (0.135 * Tavg - 0.024 * Ptot - 0.099 * Rhavg + 7.14) #equation from paper for raw manure evaporation, converted to [mm/wk]
        if Eout < 0: Eout = 0
        net = (Ptot - Eout) * 0.00328 * area #net water volume change of system [ft^3]
        if net > 0: pcost = net * 7.481 * 0.01 #financial calculation: pumping cost = net[ft^3] * 7.481 [gal/ft^3] * 0.01 [$/gal]
        else: pcost = 0
        if wk == 1:  #assume starting at zero
            totV = net
            totPC = pcost  
        else: 
            totV = dfmb.loc[wk - 1, 'Total Vol [ft^3]'] + net #total vol of additional water in storage
            totPC = dfmb.loc[wk - 1, 'Pumping Cost Total [$]'] + pcost #total vol of additional water in storage

        

        row = pd.Series([wk, Tavg, P, S, Rhavg, Eout, net, totV, pcost, totPC], 
                        index= ['week', 'Tavg[C]', 'P[mm]', 'S[mm]', 'Rhavg[%]', 'Eout[mm]', 'Net Volume Change[ft^3]', 
                                 'Total Vol [ft^3]', 'Pumping Cost Change [$]', 'Pumping Cost Total [$]']) #row to add to dfmb
        dfmb.loc[wk] = row.round(2)

    dfmb= dfmb.round(2)
    
    return dfmb




    
