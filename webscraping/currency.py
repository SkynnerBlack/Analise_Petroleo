import requests
import pandas as pd

import io

def download_currency_data(currency_code: str, start_date: str, end_date: str) -> pd.DataFrame | None:

    start_date = pd.to_datetime(start_date, format="%Y%m%d")
    end_date = pd.to_datetime(end_date, format="%Y%m%d")

    url = "https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do"
    
    payload = {
        "method": "gerarCSVFechamentoMoedaNoPeriodo",
        "ChkMoeda": currency_code,
        "DATAINI": start_date.strftime("%d/%m/%Y"),
        "DATAFIM": end_date.strftime("%d/%m/%Y")
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=exibirBoletim"
    }
    
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:

        currency_data = pd.read_csv(
            io.StringIO(response.text), 
            sep=";", 
            decimal=",",
            usecols=[0, 4, 5],
            header=None )
        currency_data.columns = ["Date", "Sale Value", "Purchase Value"]
        currency_data["Date"] = pd.to_datetime(currency_data["Date"], format="%d%m%Y").dt.strftime("%Y%m%d")
        return currency_data

currency_data = download_currency_data("61", "20240808", "20240809")

# --- #

currency_request = {
        "currency_code": "61",
        "start_date": "20240808",
        "end_date": "20240809"
        }



