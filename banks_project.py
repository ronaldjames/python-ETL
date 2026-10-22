# Code for ETL operations on Market Capitalization data

# Importing the required libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

url = 'https://web.archive.org/web/20230908091635 /https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["Name", "MC_USD_Billion"]
db_name = 'Banks.db'
table_name = 'Largest_banks'
csv_path = './Largest_banks_data.csv'
exchange_rates_csv_path = './exchange_rate.csv'

def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S'  # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now()  # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open("./code_log.txt", "a") as f:
        f.write(timestamp + ' : ' + message + '\n')

def extract(url, table_attribs):
    page = requests.get(url).text
    data = BeautifulSoup(page, 'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    tables = data.find_all('tbody')
    rows = tables[0].find_all('tr')
    for row in rows:
        col = row.find_all('td')
        if len(col) != 0:
           # get the Bank Name
           links = col[1].find_all("a")
           name = links[-1].get_text(strip=True)
           # get the Market Capitalization
           market_cap = col[2].get_text(strip=True)

           data_dict = {"Name": name,
                             "MC_USD_Billion": market_cap}
           df1 = pd.DataFrame(data_dict, index=[0])
           df = pd.concat([df, df1], ignore_index=True)
    return df

def transform(df,exchange_rates_csv_path):
    # Read the exchange rates into a dictionary: {'EUR': 0.93, 'GBP': 0.8, 'INR': 82.95}
    rates = pd.read_csv(exchange_rates_csv_path)
    rates = rates.set_index('Currency').to_dict()['Rate']

    df['MC_GBP_Billion'] = [np.round(float(x) * rates['GBP'], 2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(float(x) * rates['EUR'], 2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(float(x) * rates['INR'], 2) for x in df['MC_USD_Billion']]

    return df

def load_to_csv(df, csv_path):
    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)

def run_query(query_statement, sql_connection):
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)

log_progress('Preliminaries complete. Initiating ETL process')

df = extract(url, table_attribs)

log_progress('Data extraction complete. Initiating Transformation process')

df = transform(df,exchange_rates_csv_path)

log_progress('Data transformation complete. Initiating loading process')

load_to_csv(df, csv_path)

log_progress('Data saved to CSV file')

sql_connection = sqlite3.connect(db_name)

log_progress('SQL Connection initiated.')

load_to_db(df, sql_connection, table_name)

log_progress('Data loaded to Database as table. Running the query')

query_statement = f"SELECT * from {table_name} WHERE Name LIKE '%Bank%'"
run_query(query_statement, sql_connection)

log_progress('Process Complete.')

sql_connection.close()