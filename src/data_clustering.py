import json
import boto3
import pandas as pd
from typing import Tuple
from datetime import datetime

# --- Configuration & Initialization ---
dynamodb_table_name = 'MarketCommodityData'
sqs_queue_name = 'download_queue'
region_name = 'sa-east-1'
max_sqs_batch = 30
retry_limit = 5

partitions = {
    'CURRENCY': ('CURRENCY#USD', 'CURRENCY#BRL', 'CURRENCY#SAR')
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

def _return_checkable_dates(partition_key: str, date_range: Tuple[str, str]) -> list[dict]:
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
    
    try: 
        response = table.query(**query_params)
    except Exception as e:
        raise(f"Error querying DynamoDB: {e}")

    recorded_dates = response['Items']
    
    return recorded_dates

def _check_missing_dates(recorded_dates: list[dict], expected_dates: list[str]) -> list[str]:
    '''Compares expected dates with checkable dates to find missing ones.'''

    recorded = {item['date'] for item in recorded_dates}
    missing_dates = [date for date in expected_dates if date not in recorded]

    return missing_dates

def _check_nullvalue_values(recorded_dates: list[dict], missing_dates: list[str], retry_limit: int) -> list[str]:
    '''Rechecks for dates that are recorder as Null on the dataset, because of inexisting on the source.

    Max trying time is defined by retry_limit
    '''
    nullvalue_dates = []
    
    for item in recorded_dates:
        if item['date'] not in missing_dates:
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

    # Builds the message body
    queue_message = {
        'partition_key': partition_key,
        'dates_to_download': downloadable_dates
    }

    # Converts the message body to JSON
    message_body_json = json.dumps(queue_message)

    try:
        # Sends the message to the SQS queue
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body_json,
        )

    except Exception as e:
        raise(f"Error sending message to SQS: {e}")

def lambda_handler(event, context):
    
    expected_dates = _get_date_range_list((start_date, end_date))
     
    for info in partitions:
        for partition_key in partitions[info]:
             
            recorded_dates = _return_checkable_dates(partition_key, (start_date, end_date))

            missing_dates = _check_missing_dates(recorded_dates, expected_dates)

            nullvalue_dates = _check_nullvalue_values(recorded_dates, missing_dates, retry_limit)

            downloadable_dates = sorted(missing_dates + nullvalue_dates)

            # Send dates to SQS in batches to avoid exceeding limits
            for i in range(0, len(downloadable_dates), max_sqs_batch):
                batch = downloadable_dates[i:i + max_sqs_batch]
                if batch:
                    send_to_sqs(sqs_queue_name, partition_key, batch)

lambda_handler(None, None)