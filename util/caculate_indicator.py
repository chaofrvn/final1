import pandas as pd
import pandas_ta as ta


def get_latest_data_point(
    df: pd.DataFrame, field: str | None, indicator: str | None, period: int | None
):

    match indicator:
        case None:
            df = df[[field]]
            df.columns = ["value"]

        case "ma":
            df["value"] = ta.sma(df[field], length=period)
            df = df[["value"]]

        case "ema":
            df["value"] = ta.ema(df[field], length=period)
            df = df[["value"]]

        case "stoch_k":
            df["STOCH_k"] = ta.stoch(df["high"], df["low"], df["close"]).iloc[:, 0]
            df = df[["STOCH_k"]].rename(columns={"STOCH_k": "value"})

        case "stoch_d":
            df["STOCH_d"] = ta.stoch(df["high"], df["low"], df["close"]).iloc[:, 1]
            df = df[["STOCH_d"]].rename(columns={"STOCH_d": "value"})

        case "rsi":
            df["value"] = ta.rsi(df["close"], length=period)
            df = df[["value"]]

        case "macd":
            df["value"] = ta.macd(df["close"])["MACD_12_26_9"]
            df = df[["value"]]

        case "vwap":
            df["value"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
            df = df[["value"]]

        case "atr":
            df["value"] = ta.atr(df["high"], df["low"], df["close"], length=period)
            df = df[["value"]]

        case "obv":
            df["value"] = ta.obv(df["close"], df["volume"])
            df = df[["value"]]

        case "roc":
            df["value"] = ta.roc(df["close"], length=period)
            df = df[["value"]]

    df = df.dropna().head(1)
    if len(df) > 0:
        df = df.dropna().head(1)
        return df
    return None
    # need to make these so that it all return a slide with value is a value also with time


def get_all_data_point(
    df: pd.DataFrame, field: str | None, indicator: str | None, period: int | None
):
    match indicator:
        case None:
            df = df[field].dropna().to_frame()
        case "ma":
            df["MA"] = ta.sma(df[field], length=period)
            # Create a new DataFrame with only the time and the indicator
            df = df[["MA"]].dropna()

        case "ema":
            df["EMA"] = ta.ema(df[field], length=period)
            # Create a new DataFrame with only the time and the indicator
            df = df[["EMA"]].dropna()
            # Rename columns if necessary
            # df.rename(columns={'index': '_time', 'EMA': 'Indicator'}, inplace=True)
        case "stoch":
            df[["STOCH_k", "STOCH_d"]] = ta.stoch(df["high"], df["low"], df["close"])
            # Create a new DataFrame with only the time and the indicator
            df = df[["STOCH_k", "STOCH_d"]].dropna()

        case "rsi":
            df["RSI"] = ta.rsi(df["close"], length=period)
            df = df[["RSI"]].dropna()

        case "macd":
            df[["MACD", "MACD_h", "MACD_s"]] = ta.macd(df["close"])
            df = df[["MACD", "MACD_h", "MACD_s"]].dropna()

        case "vwap":
            df["VWAP"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
            df = df[["VWAP"]]

        case "atr":
            df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=period)
            df = df[["ATR"]]

        case "obv":
            df["OBV"] = ta.obv(df["close"], df["volume"])
            df = df[["OBV"]]

        case "roc":
            df["ROC"] = ta.roc(df["close"], length=period)
            df = df[["ROC"]]
    return df
