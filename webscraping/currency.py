import pandas as pd
import requests

def fetch_currency_data(currency_code, start_date, end_date):
    url = f"https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda={currency_code}&DATAINI={start_date}&DATAFIM={end_date}"
    response = requests.get(url)
    
    if response.status_code == 200:
        df = pd.read_csv(pd.compat.StringIO(response.text), sep=";", decimal=",")
        return df
    else:
        print("Failed to fetch data")
        return None

# Example usage:
df = fetch_currency_data("USD", "01/01/2023", "31/12/2023")
print(df.head())