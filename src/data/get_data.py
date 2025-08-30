import requests
import pandas as pd
from datetime import datetime


def extract_uitf_data(url, filename=None):
    """
    Extract UITF data from API endpoint and return as DataFrame
    
    Args:
        url (str): The API endpoint URL
        filename (str, optional): Filename to save the DataFrame as CSV. If None, won't save.
    
    Returns:
        pandas.DataFrame: DataFrame containing the extracted data
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
        
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    # Parse JSON data
    data = response.json()

    records = []
    for item in data['data_point']:
        label = item.get('label', '')
        value = item.get('y', 0)
        #convert the date
        try:
            # Convert label to proper date format
            date_obj = datetime.strptime(label, "%b %d, %Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except:
            formatted_date = label
            
        records.append({
                    'date': formatted_date,
                    'original_label': label,
                    'navpu_value': value
                })

    df = pd.DataFrame(records)
    
    # Save to file if filename is provided
    if filename!="":
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    return df

def calculate_rsi(prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
def add_buy_signals(csv_file_path, output_file_path=None):
    """
    Add buy signal classification to UITF data
    
    Args:
        csv_file_path (str): Path to input CSV file
        output_file_path (str): Path to save output CSV file (optional)
    
    Returns:
        pandas.DataFrame: DataFrame with buy signals added
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Convert date to datetime and sort
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"Processing {len(df)} records from {df['date'].min()} to {df['date'].max()}")
    
    # Calculate technical indicators
    df['price_change'] = df['navpu_value'].pct_change()
    df['price_change_7d'] = df['navpu_value'].pct_change(periods=7)
    df['price_change_30d'] = df['navpu_value'].pct_change(periods=30)
    
    # Moving averages
    df['ma_7'] = df['navpu_value'].rolling(window=7).mean()
    df['ma_30'] = df['navpu_value'].rolling(window=30).mean()
    df['ma_90'] = df['navpu_value'].rolling(window=90).mean()
    
    # RSI calculation (14-day)
    def calculate_rsi(prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    df['rsi'] = calculate_rsi(df['navpu_value'])
    
    # Support and resistance levels (rolling min/max)
    df['support_30d'] = df['navpu_value'].rolling(window=30).min()
    df['resistance_30d'] = df['navpu_value'].rolling(window=30).max()
    
    # Initialize buy column
    df['buy'] = 0
    
    # Buy Signal Strategy 1: Golden Cross (MA7 crosses above MA30)
    df['golden_cross'] = ((df['ma_7'] > df['ma_30']) & 
                         (df['ma_7'].shift(1) <= df['ma_30'].shift(1))).astype(int)
    
    # Buy Signal Strategy 2: RSI Oversold Recovery (RSI was below 30, now above 35)
    df['rsi_oversold_recovery'] = ((df['rsi'] > 35) & 
                                  (df['rsi'].shift(1) <= 30)).astype(int)
    
    # Buy Signal Strategy 3: Significant Dip Recovery (5%+ drop, then 2%+ recovery)
    df['dip_recovery'] = ((df['price_change_7d'] < -0.05) & 
                         (df['price_change'] > 0.02)).astype(int)
    
    # Buy Signal Strategy 4: Near Support Level (within 2% of 30-day low)
    df['near_support'] = ((df['navpu_value'] - df['support_30d']) / df['support_30d'] < 0.02).astype(int)
    
    # Buy Signal Strategy 5: Strong Uptrend (price above all MAs and trending up)
    df['uptrend'] = ((df['navpu_value'] > df['ma_7']) & 
                    (df['navpu_value'] > df['ma_30']) & 
                    (df['navpu_value'] > df['ma_90']) &
                    (df['price_change_7d'] > 0.02)).astype(int)
    
    # Buy Signal Strategy 6: Dollar Cost Averaging (monthly intervals)
    df['month_year'] = df['date'].dt.to_period('M')
    df['dca'] = df.groupby('month_year').cumcount() == 0  # First trading day of each month
    df['dca'] = df['dca'].astype(int)
    
    # Composite Buy Signal - Multiple conditions
    df['buy'] = (
        (df['golden_cross'] == 1) |  # Golden cross
        (df['rsi_oversold_recovery'] == 1) |  # RSI recovery
        (df['dip_recovery'] == 1) |  # Dip recovery
        ((df['near_support'] == 1) & (df['rsi'] < 50)) |  # Near support with moderate RSI
        (df['uptrend'] == 1) |  # Strong uptrend
        (df['dca'] == 1)  # Dollar cost averaging
    ).astype(int)
    
    # Add a buy strength score (0-6 based on how many signals triggered)
    df['buy_strength'] = (df['golden_cross'] + df['rsi_oversold_recovery'] + 
                         df['dip_recovery'] + df['near_support'] + 
                         df['uptrend'] + df['dca'])
    
    # Clean up intermediate columns (keep only essential ones)
    columns_to_keep = ['date', 'original_label', 'navpu_value', 'buy', 'buy_strength',
                       'price_change', 'ma_7', 'ma_30', 'rsi']
    
    result_df = df[columns_to_keep].copy()
    
    # Add buy signal explanations
    def get_buy_reason(row):
        reasons = []
        if df.loc[row.name, 'golden_cross'] == 1:
            reasons.append("Golden Cross")
        if df.loc[row.name, 'rsi_oversold_recovery'] == 1:
            reasons.append("RSI Recovery")
        if df.loc[row.name, 'dip_recovery'] == 1:
            reasons.append("Dip Recovery")
        if df.loc[row.name, 'near_support'] == 1:
            reasons.append("Near Support")
        if df.loc[row.name, 'uptrend'] == 1:
            reasons.append("Strong Uptrend")
        if df.loc[row.name, 'dca'] == 1:
            reasons.append("DCA Signal")
        
        return "; ".join(reasons) if reasons else ""
    
    result_df['buy_reason'] = result_df.apply(get_buy_reason, axis=1)

    result_df['future_return_7d'] = result_df['navpu_value'].shift(-7) / result_df['navpu_value'] - 1
    result_df['future_return_30d'] = result_df['navpu_value'].shift(-30) / result_df['navpu_value'] - 1
    
    if output_file_path:
        result_df.to_csv(output_file_path, index=False)
        print(f"\nData saved to: {output_file_path}")
    
    return result_df


def local_data_ingestion(start="2019-01-01", end=""):
    if end =="":
        end_date = datetime.today().strftime('%Y-%m-%d')
    else:
        end_date = end
    
    url = f"https://www.uitf.com.ph/daily_navpu_details_json.php?from={start}&to={end_date}&bank_id=31&fund_id=355&verification_id=1&btn=Filter"
    
    extract_uitf_data(url, filename="../../data/raw/ATRGFNP_hist.csv")
    
    input_file = "../../data/raw/ATRGFNP_hist.csv"
    output_file = "../../data/raw/ATRGFNP_hist_with_buy_signals.csv"

    add_buy_signals(input_file, output_file)
    
def data_ingestion(start="2019-01-01", end=""):
    if end =="":
        end_date = datetime.today().strftime('%Y-%m-%d')
    else:
        end_date = end
    
    url = f"https://www.uitf.com.ph/daily_navpu_details_json.php?from={start}&to={end_date}&bank_id=31&fund_id=355&verification_id=1&btn=Filter"
    
    extract_uitf_data(url, filename="data/raw/ATRGFNP_hist.csv")
    
    input_file = "data/raw/ATRGFNP_hist.csv"
    output_file = "data/raw/ATRGFNP_hist_with_buy_signals.csv"

    add_buy_signals(input_file, output_file)
    
    

    
    
  