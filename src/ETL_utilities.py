# ETL utilities
import math
import datetime as dt
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

ERR_DATE_2020_03_10 = date.fromisoformat('2020-03-10')
ERR_DATE_2020_03_10_P1 = ERR_DATE_2020_03_10 + timedelta(days=1)
MISSING_CASES_2020_03_10 = 600

ERR_DATE_2020_05_12 = date.fromisoformat('2020-05-12')
ERR_DATE_2020_05_12_P1 = ERR_DATE_2020_05_12 + timedelta(days=1)
EXCESS_CASES_2020_05_12 = 419

ERR_DATE_2020_05_27 = date.fromisoformat('2020-05-27')
ERR_DATE_2020_05_27_P1 = ERR_DATE_2020_05_12 + timedelta(days=1)
EXCESS_CASES_2020_05_27 = 168

ERR_DATE_2020_08_15 = date.fromisoformat('2020-08-15')
DECEDUTI_DELTA_2020_08_15 = 4

ERR_DATE_2020_08_17 = date.fromisoformat('2020-08-17')
CASI_TESTATI_2020_08_17 = 4_477_310
CASI_TESTATI_LIGURIA_2020_08_17 = 113_740

SOURCE_NATIONAL = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
#SOURCE_NATIONAL = 'C:\\Users\\emazep\\Downloads\\dpc-covid19-ita-andamento-nazionale.csv'

def it_data_load():
    ds_it = pd.read_csv(SOURCE_NATIONAL, parse_dates=['data'])
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
        ds.loc[ERR_DATE_2020_03_10, 'totale_casi'] = 10_149 + MISSING_CASES_2020_03_10
        ds.loc[ERR_DATE_2020_03_10, 'totale_positivi'] = 8_514 + MISSING_CASES_2020_03_10

        ds.loc[ERR_DATE_2020_03_10, 'nuovi_positivi'] = 977 + MISSING_CASES_2020_03_10
        ds.loc[ERR_DATE_2020_03_10_P1, 'nuovi_positivi'] = 2313 - MISSING_CASES_2020_03_10
    else:
        # Regional
        ds.loc[ERR_DATE_2020_03_10, 'totale_casi'] = 5_791 + MISSING_CASES_2020_03_10
        ds.loc[ERR_DATE_2020_03_10, 'totale_positivi'] = 4_427 + MISSING_CASES_2020_03_10

        ds.loc[ERR_DATE_2020_03_10, 'nuovi_positivi'] = 322 + MISSING_CASES_2020_03_10
        ds.loc[ERR_DATE_2020_03_10_P1, 'nuovi_positivi'] = 1_489 - MISSING_CASES_2020_03_10

def fix_2020_05_12(ds, region=False):
    if not region:
        # National
        ds.loc[ERR_DATE_2020_05_12, 'totale_casi_DELTA'] = 1_402 - EXCESS_CASES_2020_05_12
        ds.loc[ERR_DATE_2020_05_12, 'nuovi_positivi'] = 1_402 - EXCESS_CASES_2020_05_12
    else:
        # Regional
        ds.loc[ERR_DATE_2020_05_12, 'totale_casi_DELTA'] = 1_402 - EXCESS_CASES_2020_05_12
        ds.loc[ERR_DATE_2020_05_12, 'nuovi_positivi'] = 1_402 - EXCESS_CASES_2020_05_12

def fix_2020_05_27(ds, region=False):
    if not region:
        # National
        ds.loc[ERR_DATE_2020_05_27, 'totale_casi_DELTA'] = 584 - EXCESS_CASES_2020_05_27
        ds.loc[ERR_DATE_2020_05_27, 'nuovi_positivi'] = 584 - EXCESS_CASES_2020_05_27
    else:
        # Regional
        ds.loc[ERR_DATE_2020_05_27, 'totale_casi_DELTA'] = 584 - EXCESS_CASES_2020_05_27
        ds.loc[ERR_DATE_2020_05_27, 'nuovi_positivi'] = 584 - EXCESS_CASES_2020_05_27

def fix_2020_08_15(ds, region=False):
    if not region:
        # National
        ds.loc[ERR_DATE_2020_08_15, 'deceduti_DELTA'] = DECEDUTI_DELTA_2020_08_15

def fix_2020_08_17(ds, region=False):
    if not region:
        # National
        ds.loc[ERR_DATE_2020_08_17, 'casi_testati'] = CASI_TESTATI_2020_08_17

def add_delta_growth_perc(ds):
    # Deltas
    #ds['totale_casi_DELTA'] = ds['totale_casi'].diff()
    ds['totale_casi_DELTA'] = ds['nuovi_positivi']
    ds['totale_casi_DELTA2'] = ds['totale_casi_DELTA'].diff()
    
    ds['totale_positivi_DELTA'] = ds['totale_positivi'].diff()
    ds['totale_positivi_DELTA2'] = ds['totale_positivi_DELTA'].diff()
    ds['tamponi_DELTA'] = ds['tamponi'].diff()
    ds['casi_testati_DELTA'] = ds['casi_testati'].diff()
    ds['dimessi_guariti_DELTA'] = ds['dimessi_guariti'].diff()
    
    ds['deceduti_DELTA'] = ds['deceduti'].diff()
    fix_2020_08_15(ds) # deceduti_DELTA - do it here, otherwise deceduti_DELTA won't work!
    
    ds['terapia_intensiva_DELTA'] = ds['terapia_intensiva'].diff()
    ds['totale_ospedalizzati_DELTA'] = ds['totale_ospedalizzati'].diff()
    
    ds['casi_da_sospetto_diagnostico_DELTA'] = ds['casi_da_sospetto_diagnostico'].diff()
    ds['casi_da_screening_DELTA'] = ds['casi_da_screening'].diff()
    
    # Cum
    ds['terapia_intensiva_CUM'] = ds['terapia_intensiva'].cumsum()
    
    # %
    ds['growth_factor_cum_infected'] = ds['totale_casi_DELTA'].pct_change() + 1
    
    ds['totale_positivi_PCT'] = ds['totale_positivi'].pct_change()
    ds['terapia_intensiva_PCT'] = ds['terapia_intensiva'].pct_change()
    ds['totale_casi_DELTA_PCT'] = ds['totale_casi_DELTA'].pct_change()
    ds['totale_positivi_DELTA_PCT'] = ds['totale_positivi_DELTA'].pct_change()
    
    ds['positive_test_RATIO'] = ds['totale_casi_DELTA'] / ds['tamponi_DELTA']
    ds['positive_test_RATIO_100'] = round(ds['positive_test_RATIO']*100, 2)
    ds['positive_test_diagnostici_RATIO'] = ds['totale_casi_DELTA'] / ds['casi_testati_DELTA']
    ds['positive_test_diagnostici_RATIO_100'] = round(ds['positive_test_diagnostici_RATIO']*100, 2) 
    ds['tamponi_negativi_DELTA'] = ds['tamponi_DELTA'] - ds['totale_casi_DELTA']
    ds['tamponi_diagnostici_negativi_DELTA'] = ds['casi_testati_DELTA'] - ds['totale_casi_DELTA']
    ds['tamponi_totali_negativi_DELTA'] = ds['tamponi_DELTA'] - ds['tamponi_diagnostici_negativi_DELTA'] - ds['totale_casi_DELTA']
    
    ds['terapia_intensiva_RATIO'] = ds['terapia_intensiva'] / ds['totale_positivi']
    ds['totale_ospedalizzati_RATIO'] = ds['totale_ospedalizzati'] / ds['totale_positivi']
    ds['totale_casi_DELTA_RATIO'] = ds['totale_casi_DELTA'] / ds['totale_positivi']
    ds['totale_casi_DELTA_RATIO-7'] = ds['totale_casi_DELTA'] / ds['totale_positivi'].shift(periods=7)
    ds['totale_casi_DELTA_RATIO-10'] = ds['totale_casi_DELTA'] / ds['totale_positivi'].shift(periods=10)
    
    # Then fix some problems
    ds['totale_casi_DELTA'].fillna(0, inplace=True)
    fix_date = dt.date(2020, 3, 11)
    ds.loc[ds.index < date.fromisoformat('2020-04-15'), 'positive_test_RATIO'] = np.NaN
    ds.loc[ds.index < date.fromisoformat('2020-05-09'), 'positive_test_diagnostici_RATIO'] = np.NaN
    ds['casi_testati_DELTA_fixed'] = ds['casi_testati_DELTA']
    ds.loc[ds.index < date.fromisoformat('2020-05-09'), 'casi_testati_DELTA_fixed'] = np.NaN
    
    # The mean goes after the fix
    ds['positive_test_RATIO_MEAN'] = ds['positive_test_RATIO'].mean()
    
    # R₀
    ds['totale_positivi_10_R0'] = ds['totale_positivi'].shift(periods=10)
    ds['totale_casi_DELTA_RA_5_R0'] = ds['totale_casi_DELTA'].rolling(window=5).mean()

def add_ra_days(ds, days=7):
    min_periods = math.ceil(days/2)
    ds['totale_casi_RA_' + str(days)] = ds['totale_casi'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['totale_positivi_RA_' + str(days)] = ds['totale_positivi'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['terapia_intensiva_RA_' + str(days)] = ds['terapia_intensiva'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['totale_casi_DELTA_RA_' + str(days)] = ds['totale_casi_DELTA'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['casi_da_screening_DELTA_RA_' + str(days)] = ds['casi_da_screening_DELTA'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['casi_da_sospetto_diagnostico_DELTA_RA_' + str(days)] = ds['casi_da_sospetto_diagnostico_DELTA'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['totale_casi_DELTA2_RA_' + str(days)] = ds['totale_casi_DELTA2'].rolling(window=days, center=True, min_periods=min_periods).mean()

    ds['deceduti_DELTA_RA_' + str(days)] = ds['deceduti_DELTA'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['dimessi_guariti_DELTA_RA_' + str(days)] = ds['dimessi_guariti_DELTA'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['tamponi_DELTA_RA_' + str(days)] = ds['tamponi_DELTA'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['totale_positivi_DELTA_RA_' + str(days)] = ds['totale_positivi_DELTA'].rolling(window=days, center=True, min_periods=min_periods).mean()

    ds['growth_factor_cum_infected_RA_' + str(days)] = ds['growth_factor_cum_infected'].rolling(window=days, center=True, min_periods=min_periods).mean()
    
    ds['totale_casi_DELTA_PCT_RA_' + str(days)] = ds['totale_casi_DELTA_PCT'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['totale_positivi_PCT_RA_' + str(days)] = ds['totale_positivi_PCT'].rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['terapia_intensiva_PCT_RA_' + str(days)] = ds['terapia_intensiva_PCT'].rolling(window=days, center=True, min_periods=min_periods).mean()
    
    ds['totale_positivi_RA_' + str(days) + '_PCT_RA_' + str(days)] = ds['totale_positivi_RA_' + str(days)].pct_change().rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['terapia_intensiva_RA_' + str(days) + '_PCT_RA_' + str(days)] = ds['terapia_intensiva_RA_' + str(days)].pct_change().rolling(window=days, center=True, min_periods=min_periods).mean()
    ds['totale_casi_DELTA_RA_' + str(days) + '_PCT_RA_' + str(days)] = ds['totale_casi_DELTA_RA_' + str(days)].pct_change().rolling(window=days, center=True, min_periods=min_periods).mean()
    
def add_ra(ds, days=7):
    add_ra_days(ds, days=days)

def normalize_columns_peak(ds, column_names):
    for column in column_names:
        ds[column+'_NORM'] = ds[column] / ds[column].max()

def new_columns_mapping(ds, unit_name):
    new_column_names = {}
    for column_name in ds.columns:
        new_column_names[column_name] = column_name + '_' + unit_name
    return new_column_names

### REGIONAL DATA RESHAPING ###
def regional_data_reshaping(ds_reg):
    # Except Lombardia
    ITALIAN_REGIONS = [
        'Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna', 'Friuli Venezia Giulia', 'Lazio', 'Liguria', 'Marche', 'Molise',
        'P.A. Bolzano', 'P.A. Trento', 'Piemonte', 'Sardegna', 'Sicilia', 'Puglia', 'Toscana', 'Umbria', "Valle d'Aosta", 'Veneto'
    ]
    INTERESTING_FIELDS = [
        'totale_casi', 'tamponi', 'casi_testati', 'dimessi_guariti', 'deceduti', 'totale_positivi',
        'variazione_totale_positivi', 'nuovi_positivi', 'terapia_intensiva',
        'ricoverati_con_sintomi', 'totale_ospedalizzati', 'isolamento_domiciliare', 'casi_da_screening', 'casi_da_sospetto_diagnostico'
    ]

    # Only Lombardia processed here
    ds_Lombardia = ds_reg.loc[ds_reg['denominazione_regione'] == 'Lombardia'].loc[:,INTERESTING_FIELDS].copy()
    # Corrections first
    fix_2020_03_10(ds_Lombardia, region=True)
    # Then
    add_delta_growth_perc(ds_Lombardia)
    add_ra(ds_Lombardia)
    # Lastly
    ds_Lombardia.rename(columns=new_columns_mapping(ds_Lombardia, 'Lombardia'), inplace=True)

    # Build a new ds for each region (except Lombardia) as a dict value keyed by its corresponding region name
    region_dss = {'Lombardia': ds_Lombardia}
    for region_str in ITALIAN_REGIONS:
        region_dss[region_str] = ds_reg.loc[ds_reg['denominazione_regione'] == region_str].loc[:,INTERESTING_FIELDS].copy()

    # Init region sided ds
    ds_regions_sided = ds_Lombardia

    # Exclude the already processed Lombardia from this second loop!
    for region_str in ITALIAN_REGIONS:
        region_ds = region_dss[region_str]
        # First add calculated columns
        add_delta_growth_perc(region_ds)
        add_ra(region_ds)
        # Then rename the otherwise conflicting columns
        region_ds.rename(columns=new_columns_mapping(region_ds, region_str), inplace=True)
        # Lastly merge the ds
        ds_regions_sided = pd.merge(left=ds_regions_sided, right=region_ds, on='data').copy()
    
    return ds_regions_sided

def make_regions_group_w_ra(ds_regions_sided, plot_columns, days=7):
    ds_regions_group = ds_regions_sided.loc[:,plot_columns].copy()
    ds_regions_group['mean'] = ds_regions_group.mean(axis=1)
    ds_regions_group['mean_RA'] = ds_regions_group['mean'].rolling(window=days, center=True, min_periods=math.ceil(days/2)).mean()
    return ds_regions_group

# Upon request of the column to plot, prepend the local unit (regione/provincia) to it.
def localize_plot_column(column, local_strs):
    return [column + '_' + local_str for local_str in local_strs]

def province_data_load():
    ds_prov = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv', parse_dates=['data'])
    #ds_prov = pd.read_csv('C:/Users/emazep/Downloads/dpc-covid19-ita-province.csv', parse_dates=['data'])
    #ds_prov = pd.read_csv('dpc-covid19-ita-province.csv', parse_dates=['data'])
    ds_prov['data'] = ds_prov['data'].dt.date
    ds_prov.set_index('data', inplace=True)
    return ds_prov

### PROVINCE DATA RESHAPING ###
def province_data_reshaping(ds_prov):
    PROVINCE = ['Bergamo', 'Brescia', 'Cremona', 'Lodi', 'Milano', 'Pavia', 'Piacenza', 'Torino', 'Alessandria']
    INTERESTING_FIELDS = ['totale_casi']

    # Build a new ds for each region (except Lombardia) as a dict value keyed by its corresponding region name
    province_dss = {}
    for provincia_str in PROVINCE:
        province_dss[provincia_str] = ds_prov.loc[ds_prov['denominazione_provincia'] == provincia_str].loc[:,INTERESTING_FIELDS].copy()

    ds_province_sided = None
    first_iteration = True
    for provincia_str in PROVINCE:
        provincia_ds = province_dss[provincia_str]
        # First add calculated columns
        provincia_ds['totale_casi_DELTA'] = provincia_ds['totale_casi'].diff()
        # Then rename the otherwise conflicting columns
        provincia_ds.rename(columns=new_columns_mapping(provincia_ds, provincia_str), inplace=True)
        # Lastly merge the ds
        if first_iteration:
            ds_province_sided = provincia_ds
            first_iteration = False
        else:
            ds_province_sided = pd.merge(left=ds_province_sided, right=provincia_ds, on='data').copy()
    
    return ds_province_sided

def make_province_group_w_ra(ds_province_sided, plot_columns, days=7):
    ds_province_group = ds_province_sided.loc[:,plot_columns].copy()
    ds_province_group['mean'] = ds_province_group.mean(axis=1)
    ds_province_group['mean_RA'] = ds_province_group['mean'].rolling(window=days).mean()
    return ds_province_group
