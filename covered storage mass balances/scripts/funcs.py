'''
useful functions

'''

import pandas as pd
import numpy as np

def convert_units(df):
    '''
    need correct units to use equation from paper
    -
    returns | dfconvert: dataframe of converted values with precipitation in mm and temp in C
              aconvert: converted area [mm^2]
    -
    args | df: original dataframe 
           area: area of covered storage [ft^2]
    '''

    dfconvert = df.copy()
    dfconvert['precip [in]'] = df.loc[:,'precip [in]'] * 25.4 #1 inch = 25.4 mm
    dfconvert['Tavg [F]'] = (df.loc[:,'Tavg [F]'] - 32) * 5/9 #F to C
    dfconvert = dfconvert.rename(columns={'precip [in]' : 'P[mm]', 'Tavg [F]': 'Tavg[C]'})
    dfconvert = dfconvert.round(2) #round decimal places

    return dfconvert


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
    dfmb = pd.DataFrame(columns=['week', 'Pin[mm]','Tavg[C]', 'Rhavg[%]', 'Eout[mm]', 'Net Change[ft^3]', 'Pumping Cost [$]'])

    for i in range(wks + 1):
        wk = i + 1 #week
        end_date = wk * 7 #end date index for week
        start_date = end_date - 7 #start date index for week

        #perform mass balance: (Pin [mm/wk] - Eout [mm/wk]) * area [ft^2] * 1 [wk] = net [ft^3]
        Pin = df.iloc[start_date:end_date, 1].sum() #cumulative precipitation for wk [mm/wk]
        avgs = df.iloc[start_date:end_date, 2:].mean() #weekly averages for equation
        Eout = 10 * (0.135 * avgs[0] - 0.024 * Pin - 0.099 * avgs[1] + 7.14) #equation from paper for raw manure evaporation, converted to [mm/wk]
        net = (Pin - Eout) * 0.00328 * area #net water volume change of system [ft^3]

        #financial calculation: pumping cost = net[ft^3] * 7.481 [gal/ft^3] * 0.01 [$/gal]
        pcost = net * 7.481 * 0.01

        row = pd.Series([wk, Pin, avgs[0], avgs[1], Eout, net, pcost], index= ['week', 'Pin[mm]', 'Tavg[C]', 'Rhavg[%]', 'Eout[mm]', 'Net Change[ft^3]', 'Pumping Cost [$]']) #row to add to dfmb
        dfmb.loc[wk] = row
        dfmb= dfmb.round(2)
    
    return dfmb




    
