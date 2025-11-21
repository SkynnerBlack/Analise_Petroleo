import json
import boto3

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

def download_currency_data(partition_key, dates_to_download):
  
  base_url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
  endpoint = (
     f"CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
     f"@moeda='{osi_code[currency]}'&@dataInicial='{interval[0]}'&@dataFinalCotacao='{interval[1]}'&"
     f"$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao")

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