#!/usr/bin/env python
# coding: utf-8

# # Trend COVID-19 Italia
# 
# Generazione di grafici relativi all'epidemia di COVID-19 scoppiata nel 2020 in Italia.
# 
# ## Istruzioni
# 
# 1. Installare tutte le librerie Python rinvenibili nelle `import` presenti nella prima cella del notebook.
# 2. Clonare questo repository.
# 2. Scaricare il notebook ed eseguirne tutte le celle (verrà generato il grafico aggiornato ai dati più recenti), tranne al più l'ultima cella che serve ad esportare i grafici come immagine PNG su file.
# 
# Fonte dati: <https://github.com/pcm-dpc/COVID-19>
# 
# Codice rilasciato in licenza MIT: <https://opensource.org/licenses/MIT>
# 
# Autore: *Emanuele Zeppieri*

# In[2]:


import itertools

import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as pe

from matplotlib import rcParams
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Century Schoolbook']
rcParams['font.size'] = 15
rcParams['figure.dpi'] = 300
from matplotlib.markers import CARETDOWNBASE, CARETUPBASE
import matplotlib.dates as mdates

from datetime import date, datetime, timedelta

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[3]:


# Caricamento dei dati dalla Protezione Civile
ds_it = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv', parse_dates=['data'])
ds_it['data'] = ds_it['data'].dt.date
ds_it.set_index('data', inplace=True)


# In[4]:


# Sanity check
ds_it


# In[5]:


# Correzione dati errati 2020-03-10 nazionali
MISSING_CASES = 600
err_date = pd.to_datetime('2020-03-10').date()
err_date_p1 = err_date + timedelta(days=1)

ds_it.loc[err_date, 'totale_casi'] = 10_149 + MISSING_CASES
ds_it.loc[err_date, 'totale_attualmente_positivi'] = 8_514 + MISSING_CASES

ds_it.loc[err_date, 'nuovi_attualmente_positivi'] = 529 + MISSING_CASES
ds_it.loc[err_date_p1, 'nuovi_attualmente_positivi'] = 2076 - MISSING_CASES


# In[26]:


def add_delta_and_growth(ds):
    # Deltas
    ds['totale_casi_DELTA'] = ds['totale_casi'].diff()
    ds['totale_attualmente_positivi_DELTA'] = ds['totale_attualmente_positivi'].diff()
    ds['tamponi_DELTA'] = ds['tamponi'].diff()
    ds['dimessi_guariti_DELTA'] = ds['dimessi_guariti'].diff()
    ds['deceduti_DELTA'] = ds['deceduti'].diff()
    
    ds['growth_factor_cum_infected'] = ds['totale_casi_DELTA'].pct_change() + 1
    ds['growth_factor_curr_infected'] = ds['totale_attualmente_positivi_DELTA'].pct_change() + 1
    
    ds['positive_test_ratio'] = ds['totale_casi_DELTA'] / ds['tamponi_DELTA']


# In[80]:


def add_ra_and_perc(ds):
    days = 3
    ds['totale_casi_RA_' + str(days)] = ds['totale_casi'].rolling(window=days).mean()
    ds['totale_casi_DELTA_RA_' + str(days)] = ds['totale_casi_DELTA'].rolling(window=days).mean()
    
    days = 4
    ds['totale_casi_RA_' + str(days)] = ds['totale_casi'].rolling(window=days).mean()
    ds['totale_casi_DELTA_RA_' + str(days)] = ds['totale_casi_DELTA'].rolling(window=days).mean()


# In[28]:


add_delta_and_growth(ds_it)
add_ra_and_perc(ds_it)


# In[29]:


# Check
#ds_it.head()
ds_it.loc[:, ['totale_casi', 'totale_casi_RA_3', 'totale_casi_DELTA', 'totale_casi_DELTA_RA_4', 'tamponi', 'tamponi_DELTA', 'dimessi_guariti', 'dimessi_guariti_DELTA', 'deceduti', 'deceduti_DELTA']].tail(20)


# In[30]:


SUBTITLE = 'Fonte: Protezione Civile Italia - https://github.com/pcm-dpc/COVID-19 (dati del 10/03/2020 corretti)\nCodice: https://gist.github.com/emazep/ba8cc9d35ca58d73e01a6ac7485e60bb'
SUBTITLE_NO_CORR = 'Fonte: Protezione Civile Italia - https://github.com/pcm-dpc/COVID-19\nCodice: https://gist.github.com/emazep/ba8cc9d35ca58d73e01a6ac7485e60bb'
common_plt_params = {'markersize':8, 'linewidth':4}


# In[31]:


# Growth factor
SLACK = 0.5

ALPHA = 0.7

ax = ds_it.plot(
    y='growth_factor_cum_infected', label='Fattore di crescita normalizzato diagnosticati cumulati', **common_plt_params, marker='o', figsize=(16, 8), zorder=3
)

plt.axhline(y=1, color='red', linewidth=4, zorder=0, alpha=1, label='Limite crescita superlineare/sublineare')
plt.axhline(y=0, color='lightgreen', linewidth=8, zorder=0, alpha=1, label='Fine epidemia')
ax.legend(title="Fattore di crescita Italia", fontsize=20)

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)
ax.set_ylim(bottom=0)

#ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.2))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: "{0:.1f}".format(x).rstrip('0').rstrip('.').replace('.', ',')))

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Fattore di crescita logistica normalizzato diagnosticati cumulati Italia COVID-19', fontsize=21)

fig_growth = plt.gcf()

plt.show()


# In[32]:


# Cases trend
SLACK = 0.57

ALPHA = 0.5

ax = ds_it.plot(y='totale_casi', label='Contagi totali', **common_plt_params, marker='o', figsize=(16, 8), zorder=3)
ax.bar(ds_it.index, ds_it['totale_attualmente_positivi'], label='Pazienti attualmente positivi', color='orange')

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)

ax.legend(title="Casi diagnosticati Italia", fontsize=24)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(1000))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=9)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento casi cumulati e casi in corso diagnosticati Italia COVID-19', fontsize=21)

fig_trend = plt.gcf()

plt.show()


# In[33]:


ALPHA = 0.7
LINE_COLOR = 'blue'
BAR_COLOR = 'tab:orange'
SLACK = 0.85

# Tests trend
_, ax = plt.subplots(1,1,figsize=(16,8))

ax.bar(ds_it.index, ds_it['tamponi_DELTA'], label='Effettuati', color=BAR_COLOR, zorder=0)
ax.plot(ds_it.index, ds_it['totale_casi_DELTA'], label='Positivi', **common_plt_params, marker='o', zorder=3, color=LINE_COLOR)

ax.set_xlim(ax.get_xlim()[0]+SLACK, ax.get_xlim()[1]-SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))

ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(1000))
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
ax.tick_params(axis='y', which='both', labelsize=14)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))

ax.grid(which='major', alpha=ALPHA)

ax.tick_params(axis='y', which='both', right=True, labelright=True)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
plt.xlabel(None)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento giornaliero tamponi effettuati e tamponi positivi Italia COVID-19', fontsize=21)

handles, labels = ax.get_legend_handles_labels()
# sort both labels and handles by labels
labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
ax.legend(handles, labels, title="Tamponi giornalieri Italia", fontsize=24)

fig_tests = plt.gcf()

plt.show()


# In[34]:


# Exitus trend
ALPHA = 0.7
BAR_WIDTH = 0.3
BASE_DATE_STR = '2020-02-24'
BASE_DATE = datetime.strptime(BASE_DATE_STR, '%Y-%m-%d')

ax = ds_it.plot.bar(y=['deceduti', 'dimessi_guariti'], label=['Decessi totali', 'Guarigioni totali'], color=['r', 'limegreen'], figsize=(16,8))

ax.legend(title="Esiti cumulati Italia", fontsize=24)

ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: (BASE_DATE+timedelta(days=x.item())).strftime('%d\n%b\n%Y')))
plt.xticks(rotation=0)
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='major', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento esiti cumulati Italia COVID-19', fontsize=21)

fig_exitus = plt.gcf()

plt.show()


# In[35]:


ALPHA = 0.5
LINE_COLOR = 'orange'
BORDER_COLOR = 'black'
BAR_COLOR = 'tab:blue'
SLACK = 0.9

pe_outline = pe.withStroke(linewidth=6, foreground='black')
pe_shadow = pe.SimpleLineShadow()
pe_normal = pe.Normal()

_, ax = plt.subplots(1,1,figsize=(16,8))

ax.bar(ds_it.index, ds_it['totale_casi_DELTA'], label='Nuovi contagi giornalieri Italia', color=BAR_COLOR, zorder=2)
ax.plot(ds_it.index, ds_it['totale_casi_DELTA_RA_3'], label='Media mobile semplice a 3 giorni', zorder=4, color=LINE_COLOR, linewidth=4, path_effects=[pe_outline, pe_shadow, pe_normal])
#ax.plot(ds_it.index, ds_it['totale_casi_DELTA_RA_4'], label='Media mobile a 4 giorni', zorder=4, color='limegreen', linewidth=4, path_effects=[pe_outline, pe_shadow, pe_normal])

ax.set_xlim(ax.get_xlim()[0]+SLACK, ax.get_xlim()[1]-SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))

ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
ax.tick_params(axis='y', which='both', labelsize=14)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))

ax.grid(which='major', alpha=ALPHA)

ax.tick_params(axis='y', which='both', right=True, labelright=True)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
plt.xlabel(None)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri Italia COVID-19', fontsize=24)

#handles, labels = ax.get_legend_handles_labels()
# sort both labels and handles by labels
#labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
#ax.legend(handles, labels, title="Tamponi giornalieri Italia", fontsize=24)

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), fontsize=24)

fig_daily_incr = plt.gcf()

plt.show()


# In[36]:


ds_reg = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv', parse_dates=['data'])
ds_reg['data'] = ds_reg['data'].dt.date
ds_reg.set_index('data', inplace=True)
ds_reg


# In[37]:


# Columns mapping to avoid column names clashing when merging difefrent regions/province 
def new_columns_mapping(ds, unit_name):
    new_column_names = {}
    for column_name in ds.columns:
        new_column_names[column_name] = column_name + '_' + unit_name
    return new_column_names


# In[82]:


### REGIONAL DATA RESHAPING ###

# Except Lombardia
ITALIAN_REGIONS = [
    'Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia Romagna', 'Friuli Venezia Giulia', 'Lazio', 'Liguria', 'Marche', 'Molise',
    'P.A. Bolzano', 'P.A. Trento', 'Piemonte', 'Sardegna', 'Sicilia', 'Puglia', 'Toscana', 'Umbria', "Valle d'Aosta", 'Veneto'
]
INTERESTING_FIELDS = ['totale_casi', 'tamponi', 'dimessi_guariti', 'deceduti', 'totale_attualmente_positivi', 'nuovi_attualmente_positivi']
    
# Only Lombardia processed here
ds_Lombardia = ds_reg.loc[ds_reg['denominazione_regione'] == 'Lombardia'].loc[:,INTERESTING_FIELDS].copy()
# Corrections first
ds_Lombardia.loc[err_date, 'totale_casi'] = 5_791 + MISSING_CASES
ds_Lombardia.loc[err_date, 'totale_attualmente_positivi'] = 4_427 + MISSING_CASES
ds_Lombardia.loc[err_date, 'nuovi_attualmente_positivi'] = -63 + MISSING_CASES
ds_Lombardia.loc[err_date_p1, 'nuovi_attualmente_positivi'] = 1336 - MISSING_CASES
# Then
add_delta_and_growth(ds_Lombardia)
add_ra_and_perc(ds_Lombardia)
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
    add_delta_and_growth(region_ds)
    add_ra_and_perc(region_ds)
    # Then rename the otherwise conflicting columns
    region_ds.rename(columns=new_columns_mapping(region_ds, region_str), inplace=True)
    # Lastly merge the ds
    ds_regions_sided = pd.merge(left=ds_regions_sided, right=region_ds, on='data').copy()
    
#ds_regions_sided
ds_regions_sided.loc[:, ['totale_casi_Lombardia', 'totale_casi_DELTA_Lombardia', 'totale_casi_DELTA_RA_3_Lombardia', 'totale_casi_DELTA_Emilia Romagna']]


# In[83]:


# Upon request of the column to plot, prepend the local unit (regione/provincia) to it.
def localize_plot_column(column, local_strs):
    return [column + '_' + local_str for local_str in local_strs]


# In[95]:


# Lombardia trend
SLACK = 0.3
ALPHA = 0.5

REGIONS = ['Lombardia']

pe_outline = pe.withStroke(linewidth=6, foreground='black')
pe_shadow = pe.SimpleLineShadow()
pe_normal = pe.Normal()

ax = ds_regions_sided.plot(y=localize_plot_column('totale_casi_DELTA', REGIONS), label=['Andamento giornaliero'], figsize=(16, 8), zorder=2, marker='o', markersize=8, linewidth=4)
plot_column = localize_plot_column('totale_casi_DELTA_RA_3', REGIONS)
ax.plot(ds_it.index, ds_regions_sided[plot_column], label='Media mobile semplice a 3 giorni', zorder=4, color='yellow', linewidth=4, path_effects=[pe_outline, pe_shadow, pe_normal])

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

ax.legend(title='Nuovi contagi giornalieri Lombardia', fontsize=24)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 Lombardia', fontsize=24)

fig_daily_incr_regions_Lombardia = plt.gcf()

plt.show()


# In[54]:


# Highly critical regions trend
SLACK = 0.3
ALPHA = 0.3

REGIONS = ['Toscana', 'Veneto', 'Piemonte', 'Emilia Romagna']
COLUMNS = ['totale_casi_DELTA']

plot_columns = localize_plot_columns(COLUMNS, REGIONS)

ax = ds_regions_sided.plot(y=plot_columns, label=REGIONS, figsize=(16, 8), zorder=2, marker='o', markersize=6, linewidth=3)

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), title='Nuovi contagi giornalieri\n\n(I valori negativi sono dovuti\nad errori sui dati alla fonte)\n', fontsize=24)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 regioni ad alta diffusione (eccetto Lombardia)', fontsize=17)

fig_daily_incr_regions_high = plt.gcf()

plt.show()


# In[63]:


# Medium critical regions trend
SLACK = 0.3
ALPHA = 0.3

REGIONS = ['Campania', 'Lazio', 'Liguria', 'Marche']
COLUMNS = ['totale_casi_DELTA']

plot_columns = localize_plot_columns(COLUMNS, REGIONS)

ax = ds_regions_sided.plot(y=plot_columns, label=REGIONS, figsize=(16, 8), zorder=2, marker='o', markersize=6, linewidth=3)

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), title='Nuovi contagi giornalieri\n\n(I valori negativi sono dovuti\nad errori sui dati alla fonte)\n', fontsize=24)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 regioni a diffusione medio-alta', fontsize=19)

fig_daily_incr_regions_medium_high = plt.gcf()

plt.show()


# In[64]:


# Moderate critical regions trend
SLACK = 0.3
ALPHA = 0.3

REGIONS = ['Friuli Venezia Giulia', 'P.A. Trento', 'P.A. Bolzano', 'Puglia']
COLUMNS = ['totale_casi_DELTA']

plot_columns = localize_plot_columns(COLUMNS, REGIONS)

ax = ds_regions_sided.plot(y=plot_columns, label=REGIONS, figsize=(16, 8), zorder=2, marker='o', markersize=6, linewidth=3)

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), title='Nuovi contagi giornalieri', fontsize=24)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 regioni a diffusione media', fontsize=20)

fig_daily_incr_regions_medium = plt.gcf()

plt.show()


# In[65]:


# Moderate critical regions trend
SLACK = 0.3
ALPHA = 0.3

REGIONS = ['Sicilia', 'Umbria', "Valle d'Aosta", 'Abruzzo']
COLUMNS = ['totale_casi_DELTA']

plot_columns = localize_plot_columns(COLUMNS, REGIONS)

ax = ds_regions_sided.plot(y=plot_columns, label=REGIONS, figsize=(16, 8), zorder=2, marker='o', markersize=6, linewidth=3)

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), title='Nuovi contagi giornalieri\n\n(I valori negativi sono dovuti\nad errori sui dati alla fonte)\n', fontsize=24)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 regioni a diffusione medio-bassa', fontsize=19)

fig_daily_incr_regions_medium_low = plt.gcf()

plt.show()


# In[66]:


# Moderate critical regions trend
SLACK = 0.3
ALPHA = 0.3

REGIONS = ['Molise', 'Basilicata', 'Calabria', 'Sardegna']
COLUMNS = ['totale_casi_DELTA']

plot_columns = localize_plot_columns(COLUMNS, REGIONS)

ax = ds_regions_sided.plot(y=plot_columns, label=REGIONS, figsize=(16, 8), zorder=2, marker='o', markersize=6, linewidth=3)

ax.set_xlim(ax.get_xlim()[0]-SLACK, ax.get_xlim()[1]+SLACK)

ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

handles, labels = ax.get_legend_handles_labels()
ax.legend(reversed(handles), reversed(labels), title='Nuovi contagi giornalieri', fontsize=24)

ax.set_title(SUBTITLE, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 regioni a scarsa diffusione', fontsize=20)

fig_daily_incr_regions_low = plt.gcf()

plt.show()


# In[68]:


ds_prov = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv', parse_dates=['data'])
ds_prov['data'] = ds_prov['data'].dt.date
ds_prov.set_index('data', inplace=True)
ds_prov


# In[69]:


### PROVINCE DATA RESHAPING ###

# Except Lombardia
PROVINCE = ['Bergamo', 'Brescia', 'Cremona', 'Lodi', 'Milano', 'Pavia', 'Piacenza']
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

ds_province_sided


# In[70]:


# Medium critical regions trend
SLACK = 0.3
ALPHA = 0.3

PROVINCE = ['Bergamo', 'Milano', 'Brescia']
COLUMNS = ['totale_casi_DELTA']

plot_columns = localize_plot_columns(COLUMNS, PROVINCE)

ax = ds_province_sided.plot.bar(y=plot_columns, label=PROVINCE, figsize=(16, 8), zorder=1, width=0.7)
#color=['r', 'limegreen', 'mediumblue']

ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: (BASE_DATE+timedelta(days=x.item())).strftime('%d\n%b\n%Y')))
plt.xticks(rotation=0)
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

ax.legend(title='Nuovi contagi giornalieri', fontsize=24)

ax.set_title(SUBTITLE_NO_CORR, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 province ad alta diffusione', fontsize=20)

fig_daily_incr_province_high = plt.gcf()

plt.show()


# In[71]:


# Medium critical regions trend
SLACK = 0.3
ALPHA = 0.3

PROVINCE = ['Lodi', 'Pavia', 'Piacenza', 'Cremona']
COLUMNS = ['totale_casi_DELTA']

plot_columns = localize_plot_columns(COLUMNS, PROVINCE)

ax = ds_province_sided.plot.bar(y=plot_columns, label=PROVINCE, figsize=(16, 8), zorder=1, width=0.75)
#, color=['limegreen', 'darkred', 'gold', 'mediumblue']

ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: (BASE_DATE+timedelta(days=x.item())).strftime('%d\n%b\n%Y')))
plt.xticks(rotation=0)
ax.tick_params(axis='x', which='both', labelsize=12)
ax.xaxis.grid(True, which='both')

ax.yaxis.grid(True, which='both')
ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
ax.tick_params(axis='y', which='both', labelsize=14)

ax.grid(which='both', alpha=ALPHA)
ax.tick_params(axis='y', which='both', right=True, labelright=True)

plt.xlabel(None)

ax.legend(title='Nuovi contagi giornalieri', fontsize=24)

ax.set_title(SUBTITLE_NO_CORR, fontsize=14)
plt.suptitle('Andamento nuovi contagi diagnosticati giornalieri COVID-19 province a diffusione medio-alta', fontsize=19)

fig_daily_incr_province_medium_high = plt.gcf()

plt.show()


# In[ ]:





# In[407]:


fig_trend.savefig('01_trend_ita.png', transparent=False)
fig_daily_incr.savefig('02_daily_incr_ita.png', transparent=False)
fig_exitus.savefig('03_exitus_ita.png', transparent=False)
fig_tests.savefig('04_tests_ita.png', transparent=False)
fig_growth.savefig('05_growth_factor_ita.png', transparent=False)

fig_daily_incr_regions_Lombardia.savefig('06_daily_incr_Lombardia.png', transparent=False)
fig_daily_incr_regions_high.savefig('07_daily_incr_regions_high.png', transparent=False)
fig_daily_incr_regions_medium_high.savefig('08_daily_incr_regions_medium_high.png', transparent=False)
fig_daily_incr_regions_medium.savefig('09_daily_incr_regions_medium.png', transparent=False)
fig_daily_incr_regions_medium_low.savefig('10_daily_incr_regions_medium_low.png', transparent=False)
fig_daily_incr_regions_low.savefig('11_daily_incr_regions_low.png', transparent=False)

fig_daily_incr_province_high.savefig('12_daily_incr_province_high.png', transparent=False)
fig_daily_incr_province_medium_high.savefig('13_daily_incr_province_medium_high.png', transparent=False)


# In[ ]:




