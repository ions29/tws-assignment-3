from ib_insync import *
from contracts import contracts
from datetime import datetime
import pandas as pd
import os
import numpy as np


def get_date() -> str:
    return datetime.now().strftime("%Y%m%d-00:00:00")


def get_data_from_tws(ib: IB, contract: Contract, durationStr: str) -> pd.DataFrame:
    contract = contracts[0]

    bars = ib.reqHistoricalData(
        contract,
        endDateTime=get_date(),
        durationStr=durationStr,
        barSizeSetting="10 mins",
        whatToShow="TRADES",
        useRTH=True,
    )

    barsDf = util.df(bars)

    if barsDf is None:
        print("No data received")
        exit(1)
    return barsDf


def prepare_data_from_tws(barsDf: pd.DataFrame) -> pd.DataFrame:
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
    barsDf["flat_delta_px_next_bar"] = barsDf["flat_delta_px_prev_bar"].shift(-1)
    barsDf["percent_delta_px_next_bar"] = barsDf["percent_delta_px_prev_bar"].shift(-1)
    barsDf["flat_delta_px_close_plus_one"] = barsDf["flat_delta_px_close"].shift(-1)
    barsDf["percent_delta_px_close_plus_one"] = barsDf["percent_delta_px_close"].shift(
        -1
    )
    barsDf["flat_delta_volume_prev_day"] = barsDf["volume"] - barsDf["prev_day_volume"]
    barsDf["percent_delta_volume_prev_day"] = (
        barsDf["flat_delta_volume_prev_day"] / barsDf["prev_day_volume"]
    ) * 100
    barsDf["percent_prev_daily_volume"] = (
        (barsDf["volume"]) / barsDf["total_daily_volume_prev_day"] * 100
    )
    return barsDf


def retrieve_and_store_data_in_excel() -> None:
    ib = IB()
    ib.connect()
    ib.reqMarketDataType(3)

    durationStrs = ["11 D", "31 D", "91 D"]
    durationStrsSheets = ["10-days", "30-days", "90-days"]

    for contract in contracts:
        contractName = ib.reqContractDetails(contract)[0].marketName
        print(f"Processing {contractName}")
        bars = [
            prepare_data_from_tws(get_data_from_tws(ib, contract, durationStr))
            for durationStr in durationStrs
        ]
        # create a directory named contractName
        if not os.path.exists(f"./outputs/{contractName}"):
            os.mkdir(f"./outputs/{contractName}")
        with pd.ExcelWriter(f"./outputs/{contractName}/spreadsheet.xlsx") as writer:
            for i, bar in enumerate(bars):
                bar.to_excel(writer, sheet_name=durationStrsSheets[i], index=False)

        with pd.ExcelWriter(f"./outputs/{contractName}/correlations.xlsx") as writer:
            for i, bar in enumerate(bars):
                corr_matrix = bar.corr()
                corr_matrix.to_excel(writer, sheet_name=durationStrsSheets[i])

        print(f"Finished processing {contractName}")


def get_data_from_excel(name: str) -> pd.DataFrame:
    return pd.read_excel(f"./outputs/{name}/spreadsheet.xlsx", sheet_name="90-days")


def main():
    # retrieve_and_store_data_in_excel()
    df = get_data_from_excel("CL")

    df["abs_percent_prev_daily_volume"] = df["percent_prev_daily_volume"].abs()
    df["percent_delta_volume_prev_bar"] = (
        (df["volume"] - df["volume"].shift(1)) / df["volume"].shift(1) * 100
    )

    df2 = df[
        [
            "abs_percent_prev_daily_volume",
            "percent_delta_px_next_bar",
            "percent_prev_daily_volume",
        ]
    ]

    print("=== Correlations ===")
    print("--- Absolute Percent Prev Daily Volume ---")
    for i in range(200):
        df3 = df2[df2["abs_percent_prev_daily_volume"] > i]
        df4 = df3[
            [
                "percent_delta_px_next_bar",
                "percent_prev_daily_volume",
            ]
        ]
        corr = df4.corr()["percent_prev_daily_volume"]["percent_delta_px_next_bar"]
        if corr > 0.15:
            print(f"Threshold: {i}, Correlation: {corr}, Values: {len(df4)}")

    # print(df.head(40))
    # print(df.tail(40))
