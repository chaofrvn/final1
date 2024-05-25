import pandas as pd
import pandas_ta as ta
def get_value(df:pd.DataFrame,field:str|None,indicator:str|None,period:int|None)->float:

    match indicator:
        case None:
            df = df[[field]].dropna().tail(1)
            df.columns = ['value']

        case 'ma':
            df['value'] = ta.sma(df[field], length=period)
            df = df[['value']].dropna().tail(1)

        case 'ema':
            df['value'] = ta.ema(df[field], length=period)
            df = df[['value']].dropna().tail(1)

        case 'stoch_k':
            df['STOCH_k'], _ = ta.stoch(df['high'], df['low'], df['close'])
            df = df[['STOCH_k']].rename(columns={'STOCH_k': 'value'}).dropna().tail(1)

        case 'stoch_d':
            _, df['STOCH_d'] = ta.stoch(df['high'], df['low'], df['close'])
            df = df[['STOCH_d']].rename(columns={'STOCH_d': 'value'}).dropna().tail(1)

        case 'rsi':
            df['value'] = ta.rsi(df['close'], length=14)
            df = df[['value']].dropna().tail(1)
    # print(type(df))
    return df
            # need to make these so that it all return a slide with value is a value also with time        
  