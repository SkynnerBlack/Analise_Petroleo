from datetime import date
import pandas as pd

def currency_checker():
    'Function made to check which dates intervals must be downloaded'
    
    start_date = '2021-01-01'
    end_date = date.today()

    # Generate the date range
    date_list = pd.date_range(start=start_date, end=end_date, freq='D')

    # Convert to a list of formatted strings (optional)
    formatted_dates = [d.strftime('%Y-%m-%d') for d in date_list]

    # Print the list
    for date_str in formatted_dates:
        print(date_str)

currency_checker()