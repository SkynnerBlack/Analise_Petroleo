import json
import boto3
import requests
import pandas as pd
from decimal import Decimal

from datetime import datetime, timedelta

# --- Configuration & Initialization ---
dynamodb_table_name = 'MarketCommodityData'
region_name = 'sa-east-1'

def _download_currency_data(partition_key: str, dates_to_download: tuple[str]) -> dict[dict[str]]:
    
    base_url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    all_downloaded_data = []
    cleaned_downloaded_data = {}

    # Extract currency code from partition key
    currency = partition_key.split('#')[1]
        
    # Parse the date string using its current format
    start_date_obj = datetime.strptime(dates_to_download[0], '%Y-%m-%d')
    end_date_obj = datetime.strptime(dates_to_download[-1], '%Y-%m-%d')
    
    # Format the date objects to the BCB's REQUIRED format: MM-DD-YYYY
    formatted_start_date = start_date_obj.strftime('%m-%d-%Y')
    formatted_end_date = end_date_obj.strftime('%m-%d-%Y')

    endpoint = (
        f"CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
        f"@moeda='{currency}'&@dataInicial='{formatted_start_date}'&@dataFinalCotacao='{formatted_end_date}'&"
        f"$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao")
    
    url = base_url + endpoint

    # Execute the HTTP GET request
    response = requests.get(url)

    # Parse the JSON response
    data = response.json()
    
    # Extract the actual data list which is usually under the 'value' key in OData responses
    if 'value' in data:
        all_downloaded_data.extend(data['value'])

    for value in all_downloaded_data:
        
        # Extract the date
        date = value['dataHoraCotacao'].split(' ')[0]
        
        if date not in cleaned_downloaded_data or value['dataHoraCotacao'] > cleaned_downloaded_data[date]['dataHoraCotacao']:

            # Turning into decimal to avoid breaking the results
            value['ask_price'] = Decimal(str(value['cotacaoVenda']))
            value['bid_price'] = Decimal(str(value['cotacaoCompra']))

            value['mid_price'] = (value['ask_price'] + value['bid_price']) / 2
            value['spread'] = value['ask_price'] - value['bid_price']

            cleaned_downloaded_data[date] = value

    desired_keys = ['ask_price', 'bid_price', 'mid_price', 'spread']

    # Build currency_info for each date
    currency_info = {
        date: {key: cleaned_downloaded_data[date][key] 
               for key in desired_keys 
               if key in cleaned_downloaded_data[date]}
        for date in cleaned_downloaded_data
    }

    # Making sure it has all dates, even the ones that do not return from the BCB
    null_dates = set(dates_to_download) - set(currency_info.keys())

    if null_dates:
        for date in null_dates:

            if date not in currency_info.items():

                currency_info[date] = {key: None for key in desired_keys}

    return currency_info

def lambda_handler(event, context):
    # Iterate through each record in the event
    for record in event['Records']:
        
        # The body of the SQS message
        message = record['body']
        requisition = json.loads(message)

        partition_key = requisition['partition_key']
        dates_to_download = tuple(requisition['dates_to_download'])

        if 'CURRENCY' in partition_key:
           downloaded_data = _download_currency_data(partition_key, dates_to_download)