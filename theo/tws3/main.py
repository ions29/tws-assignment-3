from ib_insync import *
from contracts import contracts
from datetime import datetime


def get_date() -> str:
    return datetime.now().strftime("%Y%m%d-00:00:00")


def main():
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
        return
    #                          date   open   high    low  close  volume  average  barCount
    # 0    2022-09-05 15:50:00+01:00  86.39  86.39  86.39  86.39     1.0   86.390         1
    barsDf["time"] = barsDf["date"].dt.time
    barsDf["date"] = barsDf["date"].dt.date
    barsDf = barsDf[
        [
            "date",
            "time",
            "close",
            "volume",
        ]
    ]
    barsDf.rename(columns={"close": "price"}, inplace=True)
    barsDf = barsDf[barsDf["time"] <= datetime.strptime("16:00:00", "%H:%M:%S").time()]
    barsDf = barsDf[barsDf["time"] >= datetime.strptime("9:30:00", "%H:%M:%S").time()]
    print(len(barsDf))
    # barsDf.to_csv("./outputs/bars.csv", index=True)
