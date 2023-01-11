from ib_insync import *
from contracts import contracts
from datetime import datetime
import pandas as pd


def get_date() -> str:
    return datetime.now().strftime("%Y%m%d-00:00:00")


def retrieve_data_from_tws() -> pd.DataFrame:
    ib = IB()
    ib.connect()
    ib.reqMarketDataType(3)

    contract = contracts[0]

    bars = ib.reqHistoricalData(
        contract,
        endDateTime=get_date(),
        durationStr="91 D",
        barSizeSetting="10 mins",
        whatToShow="TRADES",
        useRTH=True,
    )

    barsDf = util.df(bars)

    if barsDf is None:
        print("No data received")
        exit(1)
    #                           date   open   high    low  close  volume  average  barCount
    # 0    2022-09-05 15:50:00+01:00  86.39  86.39  86.39  86.39     1.0   86.390         1
    barsDf["time"] = barsDf["date"].dt.time
    barsDf["date"] = barsDf["date"].dt.date
    barsDf.rename(columns={"close": "price"}, inplace=True)
    barsDf = barsDf[barsDf["time"] <= datetime.strptime("16:00:00", "%H:%M:%S").time()]
    barsDf = barsDf[
        barsDf["time"] >= datetime.strptime("9:30:00", "%H:%M:%S").time()
    ].reset_index(drop=True)
    barsDf["nterm"] = barsDf.index
    barsDf = barsDf[
        [
            "nterm",
            "date",
            "time",
            "price",
            "volume",
        ]
    ]
    barsDf["total_daily_volume"] = barsDf.groupby("date")["volume"].transform("sum")
    barsDf = barsDf.merge(
        barsDf.groupby("date")["price"].last().shift(1), on="date"
    ).rename(columns={"price_y": "yesterday_close", "price_x": "price"})
    barsDf["flat_delta_px_prev_bar"] = barsDf["price"] - barsDf["price"].shift(1)
    barsDf["percent_delta_px_prev_bar"] = (
        barsDf["flat_delta_px_prev_bar"] / barsDf["price"].shift(1) * 100
    )
    barsDf["flat_delta_px_close"] = barsDf["price"] - barsDf["yesterday_close"]
    barsDf["percent_delta_px_close"] = (
        barsDf["flat_delta_px_close"] / barsDf["yesterday_close"] * 100
    )
    barsDf = barsDf.merge(
        barsDf.groupby("date")["total_daily_volume"].first().shift(1), on="date"
    ).rename(
        columns={
            "total_daily_volume_y": "total_daily_volume_prev_day",
        }
    )
    for i in range(len(barsDf)):
        for prev_row in range(i - 1, -1, -1):
            if barsDf.iloc[prev_row]["time"] == barsDf.iloc[i]["time"]:
                barsDf.at[i, "prev_day_volume"] = barsDf.at[prev_row, "volume"]
                break

    barsDf = barsDf[
        [
            "nterm",
            "date",
            "time",
            "price",
            "volume",
            "prev_day_volume",
            "total_daily_volume_prev_day",
            "yesterday_close",
            "flat_delta_px_prev_bar",
            "percent_delta_px_prev_bar",
            "flat_delta_px_close",
            "percent_delta_px_close",
        ]
    ]
    return barsDf


def dump_df_to_csv(df: pd.DataFrame) -> None:
    df.to_csv("./outputs/bars.csv", index=False)


def retrieve_data_from_csv() -> pd.DataFrame:
    df = pd.read_csv("./outputs/bars.csv")
    return df


def main():
    # df = retrieve_data_from_tws() # Uncomment to get data from TWS
    df = (
        retrieve_data_from_csv()
    )  # Uncomment to get the data saved to a file to save the query
    # dump_df_to_csv(df)  # Uncomment to save the data

    print(df.head(50))
    print(df.tail(50))
