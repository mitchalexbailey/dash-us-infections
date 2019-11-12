import pandas as pd
import json
import urllib3
import glob
import plotly.graph_objects as go
import logging

from constants import columns_by_table_clean, columns_by_table

http = urllib3.PoolManager()
infections = ['Measles, Total']
label_cols = ['code', 'Reporting Area', 'Total Resident Population']

font_dict = dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
            )

def get_diseases(tables):
    # tables = display names from columns_by_table_clean
    table_letters = [columns_by_table_clean.get(x) for x in tables]
    cols = []
    for letter in table_letters:
        cols = cols + columns_by_table.get(letter)

    global infections
    infections = cols

    return cols


def get_state_populations(simple=True):
    def clean(x):
        colnames = x.iloc[0, :]
        dat = x.iloc[1:, :]
        dat.columns = colnames
        return dat
    
    census_populations = {}
    census_population_files = glob.glob('./census_populations/*_data_*.csv')
    for f in census_population_files:
        year = f.split('/')[-1].split('.')[0].replace('ACSDP1Y', '')
        temp = clean(pd.read_csv(f))
        if simple:
            census_populations[year] = dict(zip(temp['Geographic Area Name'],
                                                temp['Estimate!!SEX AND AGE!!Total population'].astype(int)))
        else:
            census_populations[year] = temp
    
    return census_populations


def clean_dat(x):
    try:
        x = str(x).replace(',', '')
        num_x = float(x)
        return num_x
    except:
        return None


def get_dat(year,  tables=['Malaria, Measles, Lyme disease, Listeriosis']):
    if tables is None:
        tables = list(columns_by_table_clean.values())
    else:
        tables = [columns_by_table_clean.get(x) for x in tables]

    dat = pd.DataFrame()

    for table in tables:
        url = f'https://wonder.cdc.gov/nndss/static/{year}/annual/{year}-table2{table}.txt'
        
        response = http.request('GET', url)
        lines = [x.rstrip() for x in response.data.decode('iso8859_15').split('\n')]

        start_line = lines.index('tab delimited data:')
        dat_lines = [x.rstrip().split('\t') for x in lines[start_line+1:]]
        temp_dat = pd.DataFrame(dat_lines)
        temp_dat = temp_dat.iloc[:, :len(dat_lines[0])]
        cols = [x.rstrip() for x in lines[start_line-len(temp_dat.columns)-1:start_line-1]]
        temp_dat.columns = cols

        for c in cols:
            if c != 'Reporting Area':
                try:
                    temp_dat[c] = temp_dat[c].dropna().apply(lambda x: clean_dat(x))
                except:
                    logging.warning(f'Failed to convert column {c}')

        if len(dat)==0:
            dat = temp_dat
        else:
            dat = pd.merge(dat, temp_dat, on='Reporting Area', how='outer')


    dat['code'] = dat['Reporting Area'].apply(lambda x: codes.get(x))
    global infections
    infections = [x for x in list(dat.columns) if x not in label_cols]

    return dat


def get_state_dat(year, tables=['Malaria, Measles, Lyme disease, Listeriosis']):
    dat = get_dat(year, tables)
    state_dat = dat[dat['Reporting Area'].isin(state_populations['2018'].keys())]
    return state_dat


def show_year_map(year,
                  infection,
                  count_type,
                  tables):
    temp_dat = get_state_dat(year, tables=tables)
    if count_type != 'Absolute':
        absolute_clause =  'Relative to Overall State Population'
        
        for table in tables:
            temp_table = columns_by_table_clean.get(table)
            table_cols = columns_by_table.get(temp_table)
            for col in table_cols:
                if col in temp_dat:
                    temp_dat[col] = temp_dat.apply(lambda x: x[col]/state_populations.get(str(year)).get(x['Reporting Area'])*1e5 if type(x[col])==float and state_populations.get(str(year)).get(x['Reporting Area']) is not None else None,
                                                    axis=1)
        htext = list(temp_dat[infection].apply(lambda x: f'{round(x, 3)} per 100k'))
    else:
        absolute_clause = 'Absolute'
        htext = list(temp_dat[infection].apply(lambda x: f'{x} cases in {year}'))

    fig = go.Figure(
        data=go.Choropleth(
        locations=temp_dat['code'],
        z = temp_dat[infection].astype(float),
        locationmode = 'USA-states',
        colorscale = 'Reds',
        colorbar_title = f"{infection.title()} Cases ({count_type})",
        text = htext,
        showscale=False,
    ))

    fig.update_layout(
        title_text = f'{infection} Cases {year}',
        geo_scope='usa',
        font=font_dict,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin = go.layout.Margin(
            t=50,
            l=5,
            r=5,
            b=5
        )
    )

    return fig


state_populations = get_state_populations()
codes = json.load(open('state_statecode.json'))
