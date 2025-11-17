import json
import boto3



def get_currency(currency: str, interval: touple):

    osi_code = {
        'real': 'BRL',
        'dolar': 'USD',
        'riyal': 'SAR'
    }
    
    base_url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    endpoint = (
        f"CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
        f"@moeda='{osi_code[currency]}'&@dataInicial='{interval[0]}'&@dataFinalCotacao='{interval[1]}'&"
        f"$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
    )
    

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

lambda_handler('teste', 'teste')