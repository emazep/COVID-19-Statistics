# ETL utilities
import datetime as dt
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

ERR_DATE = date.fromisoformat('2020-03-10')
ERR_DATE_P1 = ERR_DATE + timedelta(days=1)
MISSING_CASES = 600

def it_data_load():
    ds_it = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv', parse_dates=['data'])
    ds_it['data'] = ds_it['data'].dt.date
    ds_it.set_index('data', inplace=True)
    return ds_it

def reg_data_load():
    ds_reg = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv', parse_dates=['data'])
    ds_reg['data'] = ds_reg['data'].dt.date
    ds_reg.set_index('data', inplace=True)
    return ds_reg

def fix_2020_03_10(ds, region=False):
    if not region:
        # National
        ds.loc[ERR_DATE, 'totale_casi'] = 10_149 + MISSING_CASES
        ds.loc[ERR_DATE, 'totale_positivi'] = 8_514 + MISSING_CASES

        ds.loc[ERR_DATE, 'nuovi_positivi'] = 529 + MISSING_CASES
        ds.loc[ERR_DATE_P1, 'nuovi_positivi'] = 2076 - MISSING_CASES
    else:
        # Regional
        ds.loc[ERR_DATE, 'totale_casi'] = 5_791 + MISSING_CASES
        ds.loc[ERR_DATE, 'totale_positivi'] = 4_427 + MISSING_CASES

        ds.loc[ERR_DATE, 'nuovi_positivi'] = 322 + MISSING_CASES
        ds.loc[ERR_DATE_P1, 'nuovi_positivi'] = 1_489 - MISSING_CASES        
        
def add_delta_growth_perc(ds):
    # Deltas
    ds['totale_casi_DELTA'] = ds['totale_casi'].diff()
    ds['totale_positivi_DELTA'] = ds['totale_positivi'].diff()
    ds['tamponi_DELTA'] = ds['tamponi'].diff()
    ds['casi_testati_DELTA'] = ds['casi_testati'].diff()
    ds['dimessi_guariti_DELTA'] = ds['dimessi_guariti'].diff()
    ds['deceduti_DELTA'] = ds['deceduti'].diff()
    
    # Cum
    ds['terapia_intensiva_CUM'] = ds['terapia_intensiva'].cumsum()
    
    ds['growth_factor_cum_infected'] = ds['totale_casi_DELTA'].pct_change() + 1
    ds['growth_factor_curr_infected'] = ds['totale_positivi_DELTA'].pct_change() + 1
    
    ds['positive_test_RATIO'] = ds['totale_casi_DELTA'] / ds['tamponi_DELTA']
    ds['positive_test_RATIO_TRUE'] = ds['totale_casi_DELTA'] / ds['casi_testati_DELTA']
    ds['tamponi_negativi'] = ds['tamponi_DELTA'] - ds['totale_casi_DELTA']
    ds['tamponi_negativi_TRUE'] = ds['casi_testati_DELTA'] - ds['totale_casi_DELTA']
    
    ds['terapia_intensiva_RATIO'] = ds['terapia_intensiva'] / ds['totale_positivi']
    ds['totale_ospedalizzati_RATIO'] = ds['totale_ospedalizzati'] / ds['totale_positivi']
    ds['totale_casi_DELTA_RATIO'] = ds['totale_casi_DELTA'] / ds['totale_positivi']
    ds['totale_casi_DELTA_RATIO-7'] = ds['totale_casi_DELTA'] / ds['totale_positivi'].shift(periods=7)
    ds['totale_casi_DELTA_RATIO-10'] = ds['totale_casi_DELTA'] / ds['totale_positivi'].shift(periods=10)
    
    # Then fix some problems
    ds['totale_casi_DELTA'].fillna(0, inplace=True)
    fix_date = dt.date(2020, 3, 11)
    ds.loc[ds.index < fix_date, 'positive_test_RATIO'] = np.NaN
    
    # The mean goes after the fix
    ds['positive_test_RATIO_MEAN'] = ds['positive_test_RATIO'].mean()
    
    # R₀
    ds['totale_positivi_10_R0'] = ds['totale_positivi'].shift(periods=10)
    ds['totale_casi_DELTA_RA_5_R0'] = ds['totale_casi_DELTA'].rolling(window=5).mean()

def add_ra_days(ds, days):
    ds['totale_casi_RA_' + str(days)] = ds['totale_casi'].rolling(window=days, center=True, min_periods=4).mean()
    ds['totale_casi_DELTA_RA_' + str(days)] = ds['totale_casi_DELTA'].rolling(window=days, center=True, min_periods=4).mean()
    ds['growth_factor_cum_infected_RA_' + str(days)] = ds['growth_factor_cum_infected'].rolling(window=days, center=True, min_periods=4).mean()
    
def add_ra(ds):
    add_ra_days(ds, days=7)
