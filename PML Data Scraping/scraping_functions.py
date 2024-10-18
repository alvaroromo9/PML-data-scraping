import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# GLOBAL PARAMS
NODES_FILE = 'Catalogo_Nodos.xlsx'
nodes_df = pd.read_excel(NODES_FILE)
nodes = list(set(nodes_df['CLAVE'].tolist()))
base_url = 'https://ws01.cenace.gob.mx:8082/SWPML/SIM/SIN/MDA'

def chunk_of_nodes(nodes, chunk_size=20):
    for i in range(0, len(nodes), chunk_size):
        yield nodes[i:(i + chunk_size)]

def download_nodes_data(nodes_list=['01PLO-115', '08SUR-115'], years=[2017]):
    nodes_str = ','.join(nodes_list)
    data = []

    for year in years:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        current_start_date = start_date

        while current_start_date <= end_date:
            # Current end date
            current_end_date = min(current_start_date + timedelta(days=6), end_date)

            # Format dates for url 
            start_year = current_start_date.strftime('%Y')
            start_month = current_start_date.strftime('%m')
            start_day = current_start_date.strftime('%d')

            end_year = current_end_date.strftime('%Y')
            end_month = current_end_date.strftime('%m')
            end_day = current_end_date.strftime('%d')

            # Create API URL
            full_url = f'{base_url}/{nodes_str}/{start_year}/{start_month}/{start_day}/{end_year}/{end_month}/{end_day}/JSON'

            # Send the GET request
            response = requests.get(full_url)

            # Loop to extract data (if successful)
            if response.status_code == 200:
                print(f'Data fetched successfully until {current_end_date}')
                response_json = response.json()

                for res in response_json['Resultados']:
                    clv_nodo = res['clv_nodo']
                    
                    for valor in res['Valores']:
                        row = {'clv_nodo': clv_nodo, 
                            'fecha': valor['fecha'], 
                            'hora': valor['hora'], 
                            'pml': valor['pml'], 
                            'pml_ene': valor['pml_ene'], 
                            'pml_per': valor['pml_per'], 
                            'pml_cng': valor['pml_cng']}
                        data.append(row)

            else:
                print('Failed to fetch data')

            current_start_date = current_end_date + timedelta(days=1)

    df = pd.DataFrame(data)
    return df


def download_all_nodes(nodes, years, chunk_size=20):
    temp_df = pd.DataFrame()
    total_chunks = np.ceil(len(nodes)/chunk_size)
    i = 1
    for node_chunk in chunk_of_nodes(nodes, chunk_size):
        print(f'Processing chunk {i} of {total_chunks}')
        df = download_nodes_data(nodes_list=node_chunk, years=years)
        temp_df = pd.concat([df, temp_df], ignore_index=True)
        i += 1

    return temp_df



df = download_all_nodes(nodes=nodes, years=[2017])
df.to_csv('full_pml_mda_2017')

#print(df.head())