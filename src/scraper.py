import json
import boto3
import requests
import pandas as pd

from datetime import datetime, timedelta

def _get_date_range_list(date_range: tuple[str, str]) -> list[str]:
    """Generates a list of expected dates (YYYY-MM-DD) from start_date to today."""
    
    start_date, end_date = date_range

    try:
        # Define start date and today's date
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        date_list = pd.date_range(start=start_date, end=end_date, freq='D')
        return [d.strftime('%Y-%m-%d') for d in date_list.tolist()]
        
    except Exception as e:
        raise(f"Error generating date range: {e}")

def _find_date_intervals(dates_to_download: list[str]) -> list[tuple[str, str]]:
    """Identifies continuous date intervals in the list, splitting at gaps."""
    
    full_interval = _get_date_range_list((dates_to_download[0], dates_to_download[-1]))
    gaps = [date for date in full_interval if date not in dates_to_download]

    intervals = []
    temp_interval = []
    
    for date in full_interval:
        if date in gaps: # Found a gap
            if temp_interval:
                intervals.append(temp_interval) # Close current interval
            temp_interval = [] # Start a new interval
            
        else: # Date is present
            temp_interval.append(date)
            
    if temp_interval: # Append any remaining dates
        intervals.append(temp_interval)

    # Convert list of date lists to list of (start, end) tuples
    intervals = [(interval[0], interval[-1]) for interval in intervals]
        
    return intervals

def download_currency_data(partition_key: str, dates_to_download: list[str]):

  base_url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
  all_downloaded_data = []

  # Extract currency code from partition key
  currency = partition_key.split('#')[1]

  # Extract date interval, considering multiple intervals inside dates_to_download
  intervals = _find_date_intervals(dates_to_download)

  for interval in intervals:

    # Parse the date string using its current format
    start_date_obj = datetime.strptime(interval[0], '%Y-%m-%d')
    end_date_obj = datetime.strptime(interval[1], '%Y-%m-%d')
    
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

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")
    
    # Parse the JSON response
    data = response.json()
    
    # Extract the actual data list which is usually under the 'value' key in OData responses
    if 'value' in data:
        all_downloaded_data.extend(data['value'])

    return all_downloaded_data

def lambda_handler(event, context):
    # Iterate through each record in the event
    for record in event['Records']:
        
        # The body of the SQS message
        message = record['body']
        requisition = json.loads(message)

        partition_key = requisition['partition_key']
        dates_to_download = requisition['dates_to_download']

        if 'CURRENCY' in partition_key:
           downloaded_data = download_currency_data(partition_key, dates_to_download)


event = {
  "Records": [
    {
      "messageId": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
      "receiptHandle": "AQEBwD+o7m1Z5yK9n3m4h5k6l7P8q9r0s1t2u3v4x5y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4R5S6T7U8V9W0X1Y2Z3...",
      "body": "{\n    \"partition_key\": \"CURRENCY#USD\",\n    \"dates_to_download\": [\n        \"2023-01-31\",\n        \"2023-02-01\",\n        \"2023-02-02\",\n        \"2023-02-03\",\n        \"2023-02-04\",\n        \"2023-02-05\",\n        \"2023-02-06\",\n        \"2023-02-07\",\n        \"2023-02-08\",\n        \"2023-02-09\",\n        \"2023-02-10\",\n        \"2023-02-11\",\n        \"2023-02-12\",\n        \"2023-02-13\",\n        \"2023-02-14\",\n        \"2023-02-15\",\n        \"2023-02-16\",\n        \"2023-02-17\",\n        \"2023-02-18\",\n        \"2023-02-19\",\n        \"2023-02-20\",\n        \"2023-02-21\",\n        \"2023-02-22\",\n        \"2023-02-23\",\n        \"2023-02-24\",\n        \"2023-02-25\",\n        \"2023-02-26\",\n        \"2023-02-27\",\n        \"2023-02-28\"\n    ]\n}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1732021000000",
        "SenderId": "AIDAJ02PEX70B5GSS2P1D",
        "ApproximateFirstReceiveTimestamp": "1732021000000"
      },
      "messageAttributes": {},
      "md5OfBody": "00a1b2c3d4e5f67890a1b2c3d4e5f678",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:sa-east-1:123456789012:MinhaFilaCombustivel",
      "awsRegion": "sa-east-1"
    }
  ]
}

lambda_handler(event, 'teste')