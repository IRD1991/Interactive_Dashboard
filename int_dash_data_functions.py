"""Dependencies-------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------"""

import pandas as pd
import requests
import io
import os
import csv
import json
import ast
import pprint
from bs4 import BeautifulSoup
from datetime import datetime
from functools import reduce

"""Generic Functions--------------------------------------------------------------------------
-------------------------------------------------------------------------------------------"""

def find_data_url(parent_url, substring):
    """Finds url on a webpage using given substring for matching.
    
    Webscrapes weboage to find all URLs then looks for strings that contain substring.
    If more than one match found will fail to run, substring must be unique to desired data url.
    
    Parameters:
    -----------
    parent_url (str) - URL of webpage to webscrape to find link to data
    sustring (str) - substring to match to identify correct link for data
    
    Returns:
    --------
    data_url (str) - URL of dataset need to download
    """
    # identify all urls
    reqs = requests.get(parent_url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
 
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))
        
    # find url for data download
    substr = substring
    results = [i for i in links if substr in i]
    data_url = list(set(results))
    
    if len(data_url) > 1:
        print('Substring did not return unique match. Please provide more suitable substring.')
    else:
        data_url = data_url[0]
        return data_url


def get_ons_dataset(id: str, api_url='https://api.beta.ons.gov.uk/v1/'):
    response = requests.get(f'{api_url}datasets/{id}')
    dataset_json = response.json()
    dataset_latest = dataset_json['links']['latest_version']['href']
    dataset_meta_json = requests.get(f'{dataset_latest}/metadata').json()
    dataset_latest_csv = dataset_meta_json['downloads']['csv']['href']
    return pd.read_csv(dataset_latest_csv, storage_options = {'User-Agent': 'Mozilla/5.0'})


"""Get Data Functions-------------------------------------------------------------------------
-------------------------------------------------------------------------------------------"""

def get_cpi_data():
    return get_ons_dataset('cpih01')


def get_gdp_data():
    return get_ons_dataset('gdp-to-four-decimal-places')


def get_mortgage_data():
    url = 'https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?' \
        'csv.x=yes&Datefrom=01/Feb/1990&Dateto=now&SeriesCodes=LPMVTVU&CSVF=TT&UsingCodes=Y&VPD=Y&VFD=N'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/54.0.2840.90 '
                  'Safari/537.36'
    }

    r = requests.get(url, headers=headers)
    mortgages_df = pd.read_csv(io.StringIO(r.text), header=2)
    return mortgages_df


def get_interest_data():
    url = 'https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?' \
        'csv.x=yes&Datefrom=01/Feb/1990&Dateto=now&SeriesCodes=IUMABEDR&CSVF=TT&UsingCodes=Y&VPD=Y&VFD=N'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/54.0.2840.90 '
                  'Safari/537.36'
    }

    r = requests.get(url, headers=headers)
    interest_df = pd.read_csv(io.StringIO(r.text), header=2)
    return interest_df


def get_ukhpi_data():
    parent_url = 'https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-november-2023'
    ukhpi_substr = 'Indices-20'
    url = find_data_url(parent_url, ukhpi_substr)
    ukhpi_df = pd.read_csv(url)
    return ukhpi_df


def get_avg_price_data():
    parent_url = 'https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-november-2023'
    avg_price_substr ='Average-prices-20'
    url = find_data_url(parent_url, avg_price_substr)
    avg_price_df = pd.read_csv(url)
    return avg_price_df


"""Format Data Functions----------------------------------------------------------------------
-------------------------------------------------------------------------------------------"""

def format_cpi_data(df: pd.DataFrame):
    overall_cpi_df = df[df['Aggregate'].isin(['Overall Index', '04 Housing, water, electricity, gas and other fuels'])]\
        .drop(columns = ['Time', 'uk-only', 'Geography', 'cpih1dim1aggid'])\
        .reset_index(drop=True)
    overall_cpi_df['mmm-yy'] = overall_cpi_df['mmm-yy'].apply(lambda x: datetime.strptime(x, '%b-%y').strftime('%d/%m/%Y'))
    overall_cpi_df['Aggregate'].mask(overall_cpi_df['Aggregate'] == '04 Housing, water, electricity, gas and other fuels',
                                 'Housing Associated Costs', inplace=True)
    overall_cpi_df = overall_cpi_df.rename(columns={'v4_0': 'cpi', 'mmm-yy': 'Date'})
    overall_cpi_df['Date'] = pd.to_datetime(overall_cpi_df['Date'], format='%d/%m/%Y')
    overall_cpi_df = overall_cpi_df.pivot(index='Date', columns='Aggregate', values='cpi')
    overall_cpi_df['Housing Associated Costs Inflation Rate'] = overall_cpi_df['Housing Associated Costs'].pct_change()
    overall_cpi_df['Overall Inflation Rate'] = overall_cpi_df['Overall Index'].pct_change()
    return overall_cpi_df.sort_values('Date')


def format_gdp_data(df: pd.DataFrame):
    monthly_gdp_df = df[df['sic-unofficial'] == 'A--T']\
        .drop(columns = ['Time', 'uk-only', 'Geography', 'sic-unofficial'])\
        .reset_index(drop=True)
    monthly_gdp_df['mmm-yy'] = monthly_gdp_df['mmm-yy'].apply(lambda x: datetime.strptime(x, '%b-%y').strftime('%d/%m/%Y'))
    monthly_gdp_df['UnofficialStandardIndustrialClassification'] = 'Monthly GDP'
    monthly_gdp_df = monthly_gdp_df.rename(columns={'v4_0': 'gdp',
                                                'mmm-yy': 'Date',
                                                'UnofficialStandardIndustrialClassification': 'GDP'})
    monthly_gdp_df['Date'] = pd.to_datetime(monthly_gdp_df['Date'], format='%d/%m/%Y')
    monthly_gdp_df = monthly_gdp_df.pivot(index='Date', columns='GDP', values='gdp')
    return monthly_gdp_df.sort_values('Date')


def format_mortgage_data(df: pd.DataFrame):
    mortgages_df = df
    mortgages_df['DATE'] = pd.to_datetime(mortgages_df['DATE'], format='%d %b %Y')  + pd.offsets.MonthBegin(1)
    mortgages_df.rename(columns={
            'DATE': 'Date',
            'LPMVTVU': 'Mortgage Approvals'}, inplace=True)
    mortgages_df.set_index('Date', inplace=True)
    return mortgages_df.sort_values('Date')


def format_interest_data(df: pd.DataFrame):
    interest_df = df
    interest_df['DATE'] = pd.to_datetime(interest_df['DATE'], format='%d %b %Y') + pd.offsets.MonthBegin(1)
    interest_df.rename(columns={
            'DATE': 'Date',
            'IUMABEDR': 'Base Interest Rate'}, inplace=True)
    interest_df.set_index('Date', inplace=True)
    return interest_df.sort_values('Date')


def format_ukhpi_data(df: pd.DataFrame):
    ukhpi_df = df
    ukhpi_df['Date'] = pd.to_datetime(ukhpi_df['Date'], format='%Y-%m-%d')
    ukhpi_df.drop(columns='Area_Code', inplace=True)
    desired_regions = ['England', 'Wales', 'Northern Ireland', 'Scotland']
    national_ukhpi_df = ukhpi_df[ukhpi_df['Region_Name'].isin(desired_regions)]
    national_ukhpi_df = national_ukhpi_df.pivot(index='Date', columns='Region_Name', values='Index')
    national_ukhpi_df['United Kingdom'] = national_ukhpi_df.mean(axis=1)
    national_ukhpi_df.columns = [f'UKHPI {c}' for c in national_ukhpi_df]
    for col in national_ukhpi_df:
        national_ukhpi_df[f'{col} % Change'] = national_ukhpi_df[col].pct_change()
    return national_ukhpi_df.sort_values('Date')


def format_avg_price_data(df: pd.DataFrame):
    avg_price_df = df
    avg_price_df['Date'] = pd.to_datetime(avg_price_df['Date'], format='%Y-%m-%d')
    avg_price_df.drop(columns=['Area_Code', 'Average_Price_SA', 'Monthly_Change', 'Annual_Change'], inplace=True)
    desired_regions = ['England', 'Wales', 'Northern Ireland', 'Scotland']
    national_avg_price_df = avg_price_df[avg_price_df['Region_Name'].isin(desired_regions)]
    national_avg_price_df = national_avg_price_df.pivot(index='Date', columns='Region_Name', values='Average_Price')
    national_avg_price_df['United Kingdom'] = national_avg_price_df.mean(axis=1)
    national_avg_price_df.columns = [f'Average Property Price {c}' for c in national_avg_price_df]
    return national_avg_price_df.sort_values('Date')

def stitch_all_data(dfs_list: list):
    dfs_merged = reduce(lambda  left,right: pd.merge(left,right,
                                                         left_index=True, right_index=True,
                                                        how='outer'), dfs_list)
    dfs_merged.dropna(inplace=True)
    return dfs_merged
