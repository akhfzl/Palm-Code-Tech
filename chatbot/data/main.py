import pandas as pd

def read_csv(filename):
    df = pd.read_csv(filename, sep=',') 

    return df 

def fitur_engineering(df, how_long=False):
    format_waktu = "%Y-%m-%d %H:%M:%S"

    df['time_start'] = df['Date'].str.cat(df['Start'], sep=' ')
    df['time_end'] = df['Date'].str.cat(df['End'], sep=' ')

    # engineering long-time
    if how_long:
        df['format_start'] = pd.to_datetime(df['time_start'], format=format_waktu)
        df['format_end'] = pd.to_datetime(df['time_end'], format=format_waktu)

        df['how_long'] = df['format_end'] - df['format_start'] 

    return df
