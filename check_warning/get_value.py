import pandas as pd
import pandas_ta as ta


def get_value(
    df: pd.DataFrame, field: str | None, indicator: str | None, period: int | None
) -> float:

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
            # print(type(df))
    df = df.dropna().tail(1)
    if len(df) > 0:
        df = df.dropna().tail(1)
        return df
    return None
    # need to make these so that it all return a slide with value is a value also with time
