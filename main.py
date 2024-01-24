from thefirstock import thefirstock
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

API_KEY = "e2ff1142c1a2f1a1067b27e38aa072e8"
Vendor_Code = "HS1765_API"
UserId = "HS1765"
password = "Algotr#10"
Totp = "1965"

def login():
    login = thefirstock.firstock_login(
        userId=UserId,
        password=password,
        TOTP=Totp,
        vendorCode=Vendor_Code,
        apiKey=API_KEY
    )
    return login

def get_data():
    timePriceSeries = thefirstock.firstock_TimePriceSeries(
        exchange="NSE",
        tradingSymbol="RELIANCE-EQ",
        startTime="01/01/2024 09:45:32",
        endTime="01/02/2024 09:58:32",
        interval="3",
        userId=UserId
    )
    
    return timePriceSeries

def calculate_indicators(df):
    # Calculate RSI and EMA
    df['rsi'] = ta.rsi(df['intc'].astype(float), length=14)
    df['ema5'] = ta.ema(df['intc'].astype(float), 5)

    # Trigger Candle condition
    trigger_candle_condition = (
        (df['rsi'].astype(float) < 40) &
        (df['into'].astype(float) < df['ema5'].astype(float)) &
        (df['inth'].astype(float) < df['ema5'].astype(float)) &
        (df['intl'].astype(float) < df['ema5'].astype(float)) &
        (df['intc'].astype(float) < df['ema5'].astype(float))
    )
    df['trigger_candle'] = trigger_candle_condition

    # Filter rows with trigger candle
    trigger_candles = df[df['trigger_candle']]

    # Entry condition
    entry_condition = trigger_candles['inth'] > trigger_candles['inth'].shift(1)
    entry_points = trigger_candles[entry_condition]

    # Convert columns to numeric explicitly
    entry_points['inth'] = pd.to_numeric(entry_points['inth'], errors='coerce')
    entry_points['intl'] = pd.to_numeric(entry_points['intl'], errors='coerce')
    entry_points['intc'] = pd.to_numeric(entry_points['intc'], errors='coerce')

    # Calculate Risk, Reward, Stop Loss, Target
    risk_multiplier = 2
    stop_loss_points = 25
    target_points = 40

    entry_points['risk'] = entry_points['inth'] - entry_points['intl']
    entry_points['reward'] = risk_multiplier * entry_points['risk']
    entry_points['stop_loss'] = entry_points[['risk', 'intc']].min(axis=1).apply(lambda x: min(x, stop_loss_points))
    entry_points['target'] = entry_points[['reward', 'intc']].min(axis=1).apply(lambda x: min(x, target_points))

    return df, entry_points







def main():
    login_data = login()
    timePriceSeries = get_data()
    df = pd.DataFrame(timePriceSeries["data"])
    # df[['into', 'inth', 'intl', 'intc']] = df[['into', 'inth', 'intl', 'intc']].apply(pd.to_numeric, errors='coerce')
    # Convert 'time' column to datetime
    df['time'] = pd.to_datetime(df['time'], format='%d-%m-%Y %H:%M:%S')

    # Sort data by time
    # Set 'time' column as index
    df.set_index('time', inplace=True)
    # Check if the 'time' column is present after conversion
    print(df.columns)
    print(df.index)
    df, entry_points = calculate_indicators(df)
    

if __name__ == "__main__":
    main()
