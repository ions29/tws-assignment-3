from ib_insync import contract

contractInfos = [
    {
        "conId": 296574745,
        "exchange": "NYMEX",
    },
    {
        "conId": 297249704,
        "exchange": "IPE",
    },
    {
        "conId": 7089,
        "exchange": "NYSE",
    },
    {
        "conId": 470458975,
        "exchange": "NYSE",
    },
    {
        "conId": 4215217,
        "exchange": "NYSE",
    },
    {
        "conId": 13977,
        "exchange": "NYSE",
    },
    {
        "conId": 6890,
        "exchange": "NYSE",
    },
    {
        "conId": 5684,
        "exchange": "NYSE",
    },
]

contracts = [contract.Contract(**info) for info in contractInfos]
