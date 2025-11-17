import json
import boto3
import pandas as pd
from typing import Tuple
from datetime import datetime

# Testando Integração com a AWS V3

# --- Configuration & Initialization ---
dynamodb_table_name = 'MarketCommodityData'
sqs_queue_name = 'download_queue'
region_name = 'sa-east-1'
retry_limit = 5

partitions = {
    'CURRENCY': ('CURRENCY#USD', 'CURRENCY#BRL', 'CURRENCY#SAR'),
    'FUEL': ('FUEL#GASOLINE', 'FUEL#DIESEL', 'FUEL#ETHANOL', 'FUEL#LPG'),
}

start_date = '2023-01-01'
end_date = '2023-02-28'
# end_date = datetime.now().strftime('%Y-%m-%d')

# --- Boto3 Initialization ---

try:
    dynamodb = boto3.resource('dynamodb', region_name)
    table = dynamodb.Table(dynamodb_table_name)
except Exception as e:
    raise(f"Error initializing DynamoDB: {e}")

try:
    sqs_client = boto3.client('sqs', region_name)
except Exception as e:
    print(f"Error initializing SQS: {e}")

def _get_date_range_list(date_range: Tuple[str, str]) -> list[str]:
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

def _check_missing_dates(partition_key: str, date_range: Tuple[str, str], expected_dates: list) -> list[str]:
    """Checks for dates that were supposed to be recorded but are missing in DynamoDB."""

    start_date, end_date = date_range

    expression_attribute_names = {
        '#pk': 'info_type',
        '#dt': 'date'
    }

    expression_attribute_values = {
        ':pk_value': partition_key,
        ':start_dt': start_date,
        ':end_dt': end_date
    }

    key_condition_expression = "#pk = :pk_value AND #dt BETWEEN :start_dt AND :end_dt"

    query_params = {
        'KeyConditionExpression': key_condition_expression, # PK memory alocation condition
        'ExpressionAttributeNames': expression_attribute_names, # Atribute name declaration
        'ExpressionAttributeValues': {**expression_attribute_values} # Atribute value declaration
    }
    
    response = table.query(**query_params)
    
    selected_dataset = response['Items']

    recorded_datesset = [item.get('date') for item in response.get('Items', [])]
    missing_dates = [date for date in expected_dates if date not in recorded_datesset]
    
    return selected_dataset, missing_dates

def _check_nonexisting_values(selected_dataset: dict, retry_limit: int) -> list[str]:
    '''Rechecks for dates that are recorder as Null on the dataset, because of inexisting on the source.

    Max trying time is defined by retry_limit
    '''

    nullvalue_dates = []

    for item in selected_dataset:
        date = item.get('date')
        value = item.get('value')

        if value is None:
            retry_count = item.get('retry_count', 0)
            
            if retry_count < retry_limit:
                nullvalue_dates.append(date)

    return nullvalue_dates

def send_to_sqs(queue_name, partition_key: str, downloadable_dates: list[str]):
    """Sends a message to the specified SQS queue with the partition key and list of dates to download."""

    response = sqs_client.get_queue_url(
        QueueName=queue_name
    )
    
    queue_url = response['QueueUrl']

    # Constrói o dicionário de mensagem
    queue_message = {
        'partition_key': partition_key,
        'dates_to_download': downloadable_dates
    }

    # Serializa o dicionário em uma string JSON
    message_body_json = json.dumps(queue_message)

    # Envia a mensagem
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body_json,
    )

def lambda_handler(event, context):
    
    expected_dates = _get_date_range_list((start_date, end_date))
     
    for info in partitions:
        for partition_key in partitions[info]:
             
            selected_dataset, missing_dates = _check_missing_dates(partition_key, (start_date, end_date), expected_dates)

            nullvalue_dates = _check_nonexisting_values(selected_dataset, retry_limit)

            downloadable_dates = sorted(missing_dates + nullvalue_dates)

            max_sqs_batch = 30

            # Send dates to SQS in batches to avoid exceeding limits
            for i in range(0, len(downloadable_dates), max_sqs_batch):
                batch = downloadable_dates[i:i + max_sqs_batch]
                if batch:
                    send_to_sqs(sqs_queue_name, partition_key, batch)

            print('teste')

lambda_handler('teste', 'teste')
