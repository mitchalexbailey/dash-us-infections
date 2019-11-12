import pandas as pd
import json
import urllib3
import glob
import plotly.graph_objects as go

http = urllib3.PoolManager()
infections = ['Listeriosis',
              'Lyme disease, Total',
              'Lyme disease, Confirmed',
              'Lyme disease, Probable',
              'Malaria',
              'Measles, Total',
              'Measles, Indigenous',
              'Measles, Imported']

font_dict = dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
            )


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


def get_dat(year):
    url = f'https://wonder.cdc.gov/nndss/static/{year}/annual/{year}-table2i.txt'
    
    response = http.request('GET', url)
    lines = [x.rstrip() for x in response.data.decode('iso8859_15').split('\n')]

    start_line = lines.index('tab delimited data:')
    dat = pd.DataFrame([x.rstrip().split('\t') for x in lines[start_line+1:]])
    dat.columns = [x.rstrip() for x in lines[start_line-len(dat.columns)-1:start_line-1]]
    dat['Reporting Area'] = dat['Reporting Area'].apply(lambda x: x if x != '' else None)
    
    dat['code'] = dat['Reporting Area'].apply(lambda x: codes.get(x))

    for inf in infections:
        dat[inf] = dat[inf].dropna().apply(lambda x: clean_dat(x))

    return dat


def get_state_dat(year):
    dat = get_dat(year)
    state_dat = dat.dropna(subset=['code'])
    return state_dat


def show_year_map(year='2018',
                  infection='Measles, Total',
                  count_type='Absolute'):
    temp_dat = get_state_dat(year)
    if count_type != 'Absolute':
        temp_dat[infection] = temp_dat.apply(lambda x: x[infection]/state_populations.get(str(year)).get(x['Reporting Area'])*1e5,
                                             axis=1)
    fig = go.Figure(data=go.Choropleth(
        locations=temp_dat['code'],
        z = temp_dat[infection].astype(float),
        locationmode = 'USA-states',
        colorscale = 'Reds',
        colorbar_title = f"{infection.title()} Cases ({count_type})",
        text = temp_dat[infection].apply(lambda x: f'{x} per 100k')
    ))

    fig.update_layout(
        title_text = f'{infection} Cases {year}',
        geo_scope='usa',
        font=font_dict
    )

    return fig


state_populations = get_state_populations()
codes = json.load(open('state_statecode.json'))
